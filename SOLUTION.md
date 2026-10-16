# LedgerSvc


## Modul 1 - Linux and Networking
Answers:

# 1 RSS dan VSZ

RSS (Resident Set Size) merupakan jumlah dari RAM fisik yang digunakan dalam sebuah proses.
VSZ (Virtual Set Size) merupakan total virtual memory yang dialokasikan untuk sebuah proses, tidak hanya mengandalkan RAM fisik tapi juga menggunakan drive seperti HDD/SSD.

# 2 Troubleshoot

Untuk ‘curl http://10.0.110.240:3000’, saya akan menjalakan beberapa commands berikut terlebih dahulu:
- ip route get 10.0.110.240. Untuk mengecek route jaringan mana yang digunakan system untuk menuju destinasi/tujuan. 
- ping -c 3 10.0.110.240. Memeriksa apakah destinasi/tujuan merespon ping yang sudah dilakukan. Jika tidak ada respon belum tentu host mati, bisa karena protocol ICMP diblok oleh firewall.
- nc -zv -w 3 10.0.110.240 3000. Mengecek apakah port TCP 3000 dapat dijangkau. Jika berhasi koneksi TCP terjadi, jika timeout kemungkinan ada masalah routing, firewall atau host tidak merespon.

Deliverables: The Unit File, 'diagnose.sh, sample output 

## Modul 2 - Containerization (Docker)
Answers:

Dockerfile:
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd --create-home appuser

COPY app.py wsgi.py ./

USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]

docker-compose.yml:
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_NAME: ledger
      DB_USER: ledger
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ledger
      POSTGRES_USER: ledger
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ledger -d ledger"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  postgres_data:

Image size: 212 MB (Docker report disk usage: 52.1 MB).
curl output:


curl -i http://localhost:8080/ready
HTTP/1.1 200 OK
Server: gunicorn
Date: Fri, 16 Oct 2026 13:19:19 GMT
Connection: close
Content-Type: application/json
Content-Length: 19

{"status":"ready"}

curl -i http://localhost:8080/balance
HTTP/1.1 200 OK
Server: gunicorn
Date: Fri, 16 Oct 2026 13:21:40 GMT
Connection: close
Content-Type: application/json
Content-Length: 16

{"balance":0.0}

## Modul 3 - Kubernetes
Answers:
kubectl get pods,svc -n cand01
NAME                             READY   STATUS    RESTARTS   AGE
pod/ledgersvc-7b899dd49b-6j8vp   1/1     Running   0          7d5h
pod/ledgersvc-7b899dd49b-qjjkn   1/1     Running   0          7d5h

NAME                TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
service/ledgersvc   NodePort   10.43.217.198   <none>        8080:30080/TCP   7d5h

curl http://10.0.110.240:30080/balance
{"balance":400.75}

Liveness probe digunakan untuk memeriksa apakah aplikasi masih berjalan dengan baik. Jika pemeriksaan ini gagal beberapa kali sesuai konfigurasi, Kubernetes dapat me-restart container tersebut, sedangkan Readiness probe digunakan untuk memeriksa apakah aplikasi sudah siap menerima traffic. Jika pemeriksaan ini gagal, Kubernetes akan berhenti mengirimkan traffic ke pod tersebut melalui Service, tetapi container tidak otomatis di-restart. Jika konfigurasi probe tidak tepat, rollout bisa menyebabkan downtime. Contohnya, jika liveness probe terlalu agresif, aplikasi yang sebenarnya hanya membutuhkan waktu startup lebih lama bisa direstart terus menerus. Sebaliknya, jika readiness probe tidak dikonfigurasi dengan benar, traffic bisa masuk ke pod yang belum siap melayani request.

## Modul 4 - Databases (PostgreSQL, MySQL, ClickHouse)
Answers:
Saya akan memilih ClickHouse untuk kebutuhan analisis data dalam jumlah besar, seperti application logs, metrics, atau events, karena ClickHouse dirancang untuk menjalankan query analitik dan agregasi data dengan cepat. Sementara itu, saya akan memilih PostgreSQL atau MySQL untuk aplikasi yang membutuhkan transaksi, pengelolaan data yang saling berhubungan, serta operasi CRUD yang sering dilakukan.

## Modul 5 - Observability with Grafana
Answers:
Dashboard JSON, screenshoots, alert rule, runbook note.

## Modul 6 - Cloud (Huawei Cloud)
Answers:
Region adalah lokasi geografis tempat penyedia cloud (Huawei) menyediakan infra. Sementara itu, Availability Zone (AZ) adalah lokasi atau kelompok infra terpisah di dalam suatu Region.
Perbedaan ini penting untuk menjaga ketersediaan layanan. Jika aplikasi hanya berjalan di satu AZ dan AZ tersebut mengalami trouble, aplikasi tidak dapat diakses. Dengan menjalankan aplikasi di beberapa AZ dalam satu Region, layanan masih bisa berjalan jika salah satu AZ mengalami gangguan, selama komponen lainnya dirancang untuk mendukung failover.
Jadi, penggunaan multi-AZ membantu mengurangi risiko downtime akibat gangguan pada satu lokasi infrastruktur.

Saya akan menjalankan aplikasi di minimal dua ECS (Elastic Cloud Server) yang ditempatkan di AZ berbeda dalam satu Region Huawei Cloud. Kemudian, saya akan menggunakan ELB (Elastic Load Balance) untuk mendistribusikan traffic ke ECS yang tersedia.
ELB juga dapat melakukan health check untuk memeriksa kondisi backend. Jika salah satu ECS mengalami gangguan, traffic dapat diarahkan ke ECS lain yang masih sehat. Saya juga akan menggunakan Cloud Eye untuk memantau penggunaan CPU, memory, dan kondisi layanan, serta mengatur alarm jika terjadi masalah. 
Dengan desain ini, aplikasi tidak bergantung pada satu ECS atau satu AZ saja. Namun, saya juga perlu memastikan database dan komponen penting lainnya tidak menjadi single point of failure.

