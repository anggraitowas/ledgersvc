# LedgerSvc — Tes Teknis DevOps

## Gambaran Umum

Repositori ini berisi aplikasi LedgerSvc dan dokumentasi implementasi untuk tes teknis DevOps.

## Modul 1 — Linux dan systemd

- Mengonfigurasi dan memeriksa layanan systemd `ledger-warmup`.
- Menggunakan `diagnose.sh` untuk mengumpulkan informasi diagnostik layanan.
- Menyimpan contoh keluaran perintah sebagai bukti dan bahan pemecahan masalah.

Berkas terkait:
- `diagnose.sh`
- `module1-sample-output.txt`
- `module1-service-status.txt`

## Modul 2 — Docker

- Menyiapkan `Dockerfile` untuk membangun image aplikasi.
- Menyiapkan konfigurasi Docker Compose.
- Menggunakan variabel lingkungan untuk konfigurasi aplikasi.
- Mengecualikan berkas `.env` dari pelacakan Git.

Berkas terkait:
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.gitignore`

## Modul 3 — Kubernetes

- Men-deploy LedgerSvc ke namespace `cand01` pada k3s.
- Mengonfigurasi dua replika aplikasi.
- Mengekspos aplikasi melalui NodePort `30080`.
- Menggunakan ConfigMap untuk konfigurasi dan Secret untuk kredensial.
- Mengonfigurasi pemeriksaan kesehatan dan kesiapan aplikasi.

Hasil pengujian:
- Alamat aplikasi: `http://10.0.110.240:30080/balance`
- Respons yang diamati: HTTP 200 dengan isi `{"balance":0.0}`.

Berkas terkait:
- `module3/deployment.yaml`
- `module3/configmap.yaml`
- `module3/service.yaml`

## Modul 4 — Basis Data

- PostgreSQL: menjalankan kueri data ledger dan menghitung total transaksi harian.
- MySQL: menjalankan kueri data pelanggan yang dibuat dalam tujuh hari terakhir.
- ClickHouse: menjalankan kueri peristiwa kunjungan halaman dan menghitung jumlah kunjungan berdasarkan halaman.

Catatan: Sebagian tabel telah berisi data sebelum test. Hasil kueri perlu ditafsirkan dengan mempertimbangkan data yang sudah ada.

## Modul 5 — Pemantauan

- Kontainer Prometheus dan Grafana tersedia di lingkungan pengujian.
- LedgerSvc menyediakan metrik aplikasi melalui endpoint `/metrics`.
- Metrik yang diamati mencakup jumlah permintaan, histogram durasi permintaan, dan status koneksi basis data.

Pekerjaan yang masih perlu diverifikasi:
- Memastikan konfigurasi pengambilan metrik Prometheus dan status target.
- Menyelesaikan serta menguji dashboard Grafana dan aturan peringatan jika diwajibkan.
- Menyimpan tangkapan layar atau hasil ekspor dashboard sebagai bukti.

## Modul 6 — Huawei Cloud

- Membuat ECS melalui Huawei Cloud Console di region AP-Jakarta (`ap-southeast-3`).
- Mengonfigurasi VPC, subnet, alamat IP publik (EIP), dan Security Group.
- Menyediakan akses HTTP ke server web Nginx melalui alamat IP publik ECS.

Hasil pengujian:
- Membuka alamat IP publik ECS melalui peramban.
- Memastikan halaman Nginx berhasil ditampilkan.

Bukti yang perlu disimpan:
- `module6-nginx.png`
- `module6-ecs.png`
- `module6-security-group.png`
