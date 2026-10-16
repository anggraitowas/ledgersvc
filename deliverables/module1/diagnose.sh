#!/bin/bash

echo "===== Hostname ====="
hostname

echo "===== Uptime ====="
uptime

echo "===== Top 5 Processes by Memory ====="
ps aux --sort=-%mem | head -n 6

echo "===== Disk Usage ====="
df -h

echo "===== Listening TCP Ports ====="
sudo ss -lntp

echo "===== Check PostgreSQL Port ====="
nc -zv -w 3 localhost 5432
