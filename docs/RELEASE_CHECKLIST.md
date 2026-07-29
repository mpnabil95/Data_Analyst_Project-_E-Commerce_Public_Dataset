# Release Checklist — v2.0.0

Checklist ini adalah sumber keputusan GO/NO-GO untuk rilis v2.0.0. Tanda
centang mencerminkan kondisi repository pada 29 Juli 2026, bukan jaminan untuk
commit yang berubah setelah tanggal tersebut.

## 1. Identitas rilis

- Target branch pengembangan: `development/v2-finalization`
- Target branch rilis: `main`
- Target tag: `v2.0.0`
- Entry point: `app.py`
- Target Python: 3.11
- Status saat checklist dibuat: **belum siap dirilis**
- Checkpoint: Tahap 8 — Dokumentasi dan Lisensi selesai; Tahap 9 belum dimulai

## 2. Source control

- [x] Branch finalisasi terpisah dari `main`
- [x] Riwayat v1/Dicoding dipertahankan pada branch/tag legacy
- [x] Working tree bersih sebelum Tahap 8
- [x] `app.py` menjadi satu-satunya entry point dashboard v2
- [x] File eksperimen dan artefak sementara tidak dilacak
- [x] `geolocation_dataset.csv` menggunakan Git LFS
- [x] Diff kandidat commit Tahap 8 telah direview
- [ ] Branch finalisasi telah di-push
- [ ] Pull request ke `main` telah dibuat dan direview
- [ ] Commit hasil merge telah diverifikasi

## 3. Data integrity

- [x] Sembilan CSV wajib tersedia
- [x] Jumlah baris sembilan CSV sesuai dataset lengkap
- [x] Checksum geolocation cocok dengan objek Git LFS resmi proyek
- [x] Dashboard menolak dataset terpotong/pointer LFS
- [x] Primary/candidate key dan referential integrity diaudit di notebook
- [x] Koordinat di luar bounding box Brasil dikeluarkan sebelum median
- [x] Data dictionary tersedia
- [x] Atribusi dan lisensi dataset tersedia
- [ ] Clean clone menjalankan `git lfs pull` dan memverifikasi checksum
- [ ] Tidak ada CSV turunan, output sensitif, atau file personal dalam paket rilis

## 4. Metric integrity

- [x] Product GMV hanya menggunakan harga produk
- [x] Order value menggunakan harga produk + freight
- [x] AOV menggunakan total order value / order unik dalam filter
- [x] Rating diagregasi pada level order
- [x] Repeat customer menggunakan ≥2 delivered order
- [x] RFM monetary menggunakan total payment
- [x] Weighted retention hanya menggunakan cohort yang cukup matang
- [x] Notebook dan dashboard mempunyai definisi metrik yang konsisten
- [ ] Automated regression test mengunci KPI default
- [ ] Automated test mengunci RFM dan cohort default

Expected default regression values:

| Metrik | Expected |
|---|---:|
| Delivered orders | 96.478 |
| Unique customers | 93.358 |
| Item rows | 110.197 |
| Product GMV | R$13.221.498,11 |
| Order value | R$15.419.773,75 |
| AOV | R$159,83 |
| Average rating | 4,1562 |
| Repeat customer | 3,0003% |
| Weighted retention M+1 | 0,4827% |
| Weighted retention M+3 | 0,2547% |

## 5. Environment and dependencies

- [x] `.python-version` menetapkan Python 3.11
- [x] Runtime dependency dipin pada `requirements.txt`
- [x] Notebook dependency dipin pada `requirements-notebook.txt`
- [x] Development dependency dipin pada `requirements-dev.txt`
- [x] Instalasi bersih Python 3.11.15 berhasil
- [x] `pip check` bersih
- [x] Import seluruh modul utama berhasil
- [x] `app.py` dapat dikompilasi
- [x] Notebook 19/19 code cell dapat dieksekusi
- [ ] CI mengulangi pemeriksaan environment pada setiap PR

## 6. Dashboard quality

- [x] Ringkasan dapat dirender
- [x] Customer & Peta dapat dirender
- [x] Customer Value dapat dirender
- [x] Produk & Seller dapat dirender
- [x] Layanan & Pembayaran dapat dirender
- [x] Empty-state untuk hasil tanpa delivered order tersedia
- [x] Customer Value dihitung secara lazy
- [x] Filter representatif telah diuji manual
- [x] Dark theme dikunci melalui `.streamlit/config.toml`
- [ ] Smoke test Streamlit tersimpan di repository
- [ ] Test filter, empty-state, dan lima bagian tersimpan di repository
- [ ] Layout desktop dan mobile diperiksa dari build kandidat rilis
- [ ] Seluruh tombol download dan tooltip diverifikasi

## 7. Notebook quality

- [x] Notebook mempunyai 74 cell
- [x] Terdapat 19 code cell dengan execution count 1–19
- [x] Tidak terdapat output error
- [x] Environment metadata menggunakan Python 3.11
- [x] Pertanyaan bisnis, interpretasi, rekomendasi, dan batasan tersedia
- [x] Tidak terdapat path atau interpreter ID spesifik mesin
- [ ] Notebook dieksekusi ulang dari clean clone kandidat rilis
- [ ] Output notebook dibandingkan dengan KPI dashboard kandidat rilis

## 8. Documentation and licensing

- [x] `docs/DATA_DICTIONARY.md` tersedia
- [x] `docs/METHODOLOGY.md` tersedia
- [x] `docs/DATA_ATTRIBUTION.md` tersedia
- [x] `docs/RELEASE_CHECKLIST.md` tersedia
- [x] `LICENSE` memisahkan kode asli dari dataset pihak ketiga
- [x] Changelog menunjuk `app.py` dan mencakup finalisasi Tahap 1–6
- [ ] README profesional selesai
- [ ] Screenshot lima bagian dashboard tersedia
- [ ] Diagram arsitektur data tersedia
- [ ] KPI definitions dan limitations tertaut dari README
- [ ] Instruksi instalasi, notebook, dan deployment diuji dari README
- [ ] Seluruh link internal dan eksternal lolos pemeriksaan

## 9. Security and repository hygiene

- [x] `.env`, secret Streamlit, virtual environment, cache, dan log diabaikan
- [x] Tidak ada credential di file yang dilacak
- [x] Tidak ada output ekspor analitik yang dilacak
- [x] File konfigurasi tidak mengandung secret
- [ ] Secret scan dijalankan pada kandidat rilis
- [ ] Dependency vulnerability scan ditinjau
- [ ] Paket/arsip rilis diperiksa agar tidak membawa `.env`, cache, atau file lokal

## 10. Deployment

- [ ] Deployment target telah dipilih
- [ ] `app.py` digunakan sebagai main file
- [ ] Git LFS/data availability pada platform target dipastikan
- [ ] Resource limit diuji pada cold start dan rerun
- [ ] Dashboard health check berhasil
- [ ] URL deployment final ditambahkan ke README

## 11. Final audit

- [ ] `git status --short` kosong
- [ ] `git diff --check` bersih
- [ ] Test suite hijau
- [ ] Notebook execution hijau
- [ ] Streamlit smoke/regression test hijau
- [ ] Clean clone test hijau
- [ ] Dataset checksum hijau
- [ ] Documentation link check hijau
- [ ] Reviewer menetapkan keputusan **GO**

## 12. Merge, tag, dan GitHub Release

Langkah ini hanya boleh dilakukan setelah seluruh item wajib di bagian 11
selesai.

- [ ] PR di-merge ke `main`
- [ ] `main` ditarik ulang dari remote
- [ ] Commit merge diuji ulang
- [ ] Annotated tag `v2.0.0` dibuat pada commit final
- [ ] Tag di-push
- [ ] GitHub Release dibuat dari tag `v2.0.0`
- [ ] Release notes mencantumkan fitur, metrik, instalasi, breaking changes,
      data license, dan known limitations
- [ ] URL dashboard dan aset rilis diverifikasi
- [ ] Tag dipastikan menunjuk tepat ke commit final di `main`

## 13. Aturan GO/NO-GO

Rilis berstatus **NO-GO** jika salah satu kondisi berikut terjadi:

- dataset tidak lengkap atau checksum geolocation tidak cocok;
- KPI dashboard berbeda dari regression baseline tanpa perubahan metodologi
  yang terdokumentasi;
- notebook atau salah satu dari lima bagian dashboard gagal;
- lisensi/atribusi dataset tidak tersedia;
- README belum menjelaskan instalasi dan batasan;
- test atau clean-clone audit gagal;
- working tree tidak bersih;
- tag tidak akan menunjuk commit final di `main`.

Keputusan **GO** hanya diberikan pada satu commit kandidat rilis yang telah
lulus seluruh gerbang Tahap 10.
