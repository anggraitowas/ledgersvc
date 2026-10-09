"""
ledgersvc - a tiny fintech-flavoured HTTP service used for the SRE technical test.

It exposes a small "ledger" API backed by PostgreSQL and instruments itself with
Prometheus metrics. It is intentionally simple and readable so that a junior
candidate can containerise, deploy, and observe it without needing to understand
a large codebase.

Endpoints
---------
  GET  /health    Liveness  - always 200 if the process is up.
  GET  /ready     Readiness - 200 only if the database is reachable.
  GET  /metrics   Prometheus exposition format.
  GET  /balance   Returns the current ledger balance (reads from the DB).
  POST /transfer  Body: {"amount": <number>} - appends a ledger entry.

Configuration (all via environment variables)
----------------------------------------------
  DB_HOST      (default: localhost)
  DB_PORT      (default: 5432)
  DB_NAME      (default: ledger)
  DB_USER      (default: ledger)
  DB_PASSWORD  (default: <empty>)     # in real life this comes from a Secret
  APP_PORT     (default: 8080)
  BIND_ADDRESS (default: 0.0.0.0)     # deliberately configurable for a pairpro fault
"""

import os
import time
import logging

from flask import Flask, jsonify, request
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# ----------------------------------------------------------------------------
# Logging - structured-ish plain lines so candidates can practise reading logs.
# ----------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s",
)
log = logging.getLogger("ledgersvc")

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "ledger")
DB_USER = os.getenv("DB_USER", "ledger")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
APP_PORT = int(os.getenv("APP_PORT", "8080"))
BIND_ADDRESS = os.getenv("BIND_ADDRESS", "0.0.0.0")

# ----------------------------------------------------------------------------
# Prometheus metrics
# ----------------------------------------------------------------------------
REQUESTS = Counter(
    "ledgersvc_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "ledgersvc_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)
DB_UP = Gauge(
    "ledgersvc_db_up",
    "1 if the database is reachable, 0 otherwise",
)

app = Flask(__name__)
pool = None


def init_pool():
    """Create a small connection pool. Retries so the app can start slightly
    before the database is ready (common in compose / k8s startup ordering)."""
    global pool
    for attempt in range(1, 11):
        try:
            pool = SimpleConnectionPool(
                1,
                5,
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=3,
            )
            with pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS ledger_entries (
                            id     SERIAL PRIMARY KEY,
                            amount NUMERIC NOT NULL,
                            ts     TIMESTAMPTZ NOT NULL DEFAULT now()
                        );
                        """
                    )
                    conn.commit()
                pool.putconn(conn)
            log.info("connected to database %s:%s/%s", DB_HOST, DB_PORT, DB_NAME)
            DB_UP.set(1)
            return
        except Exception as exc:  # noqa: BLE001 - we want to log any failure
            DB_UP.set(0)
            log.error(
                "db connection attempt %d/10 failed: %s", attempt, exc
            )
            time.sleep(2)
    log.error("giving up on database after 10 attempts; starting degraded")


@app.route("/health")
def health():
    REQUESTS.labels("GET", "/health", "200").inc()
    return jsonify(status="ok"), 200


@app.route("/ready")
def ready():
    """Readiness depends on the database being reachable."""
    try:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        pool.putconn(conn)
        DB_UP.set(1)
        REQUESTS.labels("GET", "/ready", "200").inc()
        return jsonify(status="ready"), 200
    except Exception as exc:  # noqa: BLE001
        DB_UP.set(0)
        log.error("readiness check failed: %s", exc)
        REQUESTS.labels("GET", "/ready", "503").inc()
        return jsonify(status="not-ready", error=str(exc)), 503


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/balance")
def balance():
    with LATENCY.labels("/balance").time():
        try:
            conn = pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT COALESCE(SUM(amount), 0) FROM ledger_entries;")
                total = cur.fetchone()[0]
            pool.putconn(conn)
            REQUESTS.labels("GET", "/balance", "200").inc()
            return jsonify(balance=float(total)), 200
        except Exception as exc:  # noqa: BLE001
            log.error("balance query failed: %s", exc)
            REQUESTS.labels("GET", "/balance", "500").inc()
            return jsonify(error=str(exc)), 500


@app.route("/transfer", methods=["POST"])
def transfer():
    with LATENCY.labels("/transfer").time():
        data = request.get_json(silent=True) or {}
        amount = data.get("amount")
        if amount is None:
            REQUESTS.labels("POST", "/transfer", "400").inc()
            return jsonify(error="amount is required"), 400
        try:
            conn = pool.getconn()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO ledger_entries (amount) VALUES (%s) RETURNING id;",
                    (amount,),
                )
                entry_id = cur.fetchone()[0]
                conn.commit()
            pool.putconn(conn)
            log.info("recorded transfer id=%s amount=%s", entry_id, amount)
            REQUESTS.labels("POST", "/transfer", "201").inc()
            return jsonify(id=entry_id, amount=amount), 201
        except Exception as exc:  # noqa: BLE001
            log.error("transfer failed: %s", exc)
            REQUESTS.labels("POST", "/transfer", "500").inc()
            return jsonify(error=str(exc)), 500


if __name__ == "__main__":
    init_pool()
    log.info("starting ledgersvc on %s:%s", BIND_ADDRESS, APP_PORT)
    app.run(host=BIND_ADDRESS, port=APP_PORT)
