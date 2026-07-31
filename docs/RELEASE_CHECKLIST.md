# Release Checklist — v2.0.0

Checklist ini adalah sumber keputusan GO/NO-GO untuk rilis v2.0.0. Tanda centang mencerminkan kondisi kandidat rilis pada 31 Juli 2026 dan hanya berlaku untuk commit final yang disebutkan dalam dokumen ini.

## 1. Identitas rilis

- Repository: `mpnabil95/olist-ecommerce-intelligence`
- Source branch finalisasi: `development/v2-finalization` — sudah di-merge
- Target branch rilis: `main`
- Target tag: `v2.0.0`
- Entry point: `app.py`
- Target Python: 3.11
- Status saat checklist diperbarui: **READY FOR FINAL GO REVIEW**
- Checkpoint: merge ke `main`, repository rename, deployment ulang,
  dan CI utama telah selesai; verifikasi lokal akhir dan release hygiene
  masih menunggu.
- Candidate commit: latest verified commit on `main`
- Bukti audit: [`FINAL_AUDIT_REPORT.md`](FINAL_AUDIT_REPORT.md)

## 2. Source control

- [x] Branch finalisasi terpisah dari `main`
- [x] Riwayat v1/Dicoding dipertahankan pada branch/tag legacy
- [x] Working tree bersih sebelum Tahap 8
- [x] `app.py` menjadi satu-satunya entry point dashboard v2
- [x] File eksperimen dan artefak sementara tidak dilacak
- [x] `geolocation_dataset.csv` menggunakan Git LFS
- [x] Diff kandidat commit Tahap 8 telah direview
- [x] Branch finalisasi telah di-push
- [x] Branch finalisasi telah di-merge ke `main` melalui merge commit
- [x] Commit hasil merge telah diverifikasi

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
- [x] Tidak ada CSV turunan, output sensitif, atau file personal yang dilacak Git
- [ ] Arsip/source package GitHub Release diperiksa setelah release dibuat

## 4. Metric integrity

- [x] Product GMV hanya menggunakan harga produk
- [x] Order value menggunakan harga produk + freight
- [x] AOV menggunakan total order value / order unik dalam filter
- [x] Rating diagregasi pada level order
- [x] Repeat customer menggunakan ≥2 delivered order
- [x] RFM monetary menggunakan total payment
- [x] Weighted retention hanya menggunakan cohort yang cukup matang
- [x] Notebook dan dashboard mempunyai definisi metrik yang konsisten
- [x] Automated regression test mengunci KPI default
- [x] Automated test mengunci RFM dan cohort default

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
- [x] Workflow CI mengulangi pemeriksaan environment pada setiap PR ke `main`
- [x] Workflow CI hijau pada commit kandidat rilis di `main`

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
- [x] Smoke test Streamlit tersimpan di repository
- [x] Test filter, empty-state, dan lima bagian tersimpan di repository
- [x] Layout desktop dan mobile diperiksa dari build kandidat rilis
- [x] Seluruh tombol download dan tooltip diverifikasi

## 7. Notebook quality

- [x] Notebook mempunyai 74 cell
- [x] Terdapat 19 code cell dengan execution count 1–19
- [x] Tidak terdapat output error
- [x] Environment metadata menggunakan Python 3.11
- [x] Pertanyaan bisnis, interpretasi, rekomendasi, dan batasan tersedia
- [x] Tidak terdapat path atau interpreter ID spesifik mesin
- [x] Notebook dieksekusi ulang dari clean clone kandidat rilis
- [x] Output notebook dibandingkan dengan KPI dashboard kandidat rilis

## 8. Documentation and licensing

- [x] `docs/DATA_DICTIONARY.md` tersedia
- [x] `docs/METHODOLOGY.md` tersedia
- [x] `docs/DATA_ATTRIBUTION.md` tersedia
- [x] `docs/RELEASE_CHECKLIST.md` tersedia
- [x] `LICENSE` memisahkan kode asli dari dataset pihak ketiga
- [x] Changelog menunjuk `app.py` dan mencakup finalisasi Tahap 1–6
- [x] README profesional selesai
- [x] Screenshot lima bagian dashboard tersedia
- [x] Diagram arsitektur data tersedia
- [x] KPI definitions dan limitations tertaut dari README
- [x] Instruksi instalasi, notebook, dan deployment diuji dari README
- [x] Seluruh link internal dan eksternal lolos pemeriksaan
- [x] Final audit report dan perintah quality gate tersedia

## 9. Security and repository hygiene

- [x] `.env`, secret Streamlit, virtual environment, cache, dan log diabaikan
- [x] Tidak ada credential di file yang dilacak
- [x] Tidak ada output ekspor analitik yang dilacak
- [x] File konfigurasi tidak mengandung secret
- [x] Credential-pattern scan tersedia dan audit workspace bersih
- [x] Dependency vulnerability scan ditinjau
- [ ] Paket/arsip rilis diperiksa agar tidak membawa `.env`, cache, atau file lokal

## 10. Deployment

- [x] Deployment target telah dipilih
- [x] `app.py` digunakan sebagai main file
- [x] Git LFS/data availability pada platform target dipastikan
- [ ] Resource limit diuji pada cold start dan rerun
- [x] Dashboard health check berhasil pada deployment Tahap 9
- [x] URL deployment final ditambahkan ke README

## 11. Final audit

Item berikut hanya berlaku untuk commit kandidat rilis yang sama.

- [x] `git status --short` kosong
- [x] `git diff --check` bersih
- [x] Test suite hijau
- [x] Notebook execution hijau
- [x] Streamlit smoke/regression test hijau
- [x] Fresh CI checkout dengan Git LFS dan checksum dataset hijau
- [x] Dataset checksum hijau
- [x] Markdown local-link check hijau
- [ ] Link eksternal utama diverifikasi manual
- [ ] Resource/cold-start check deployment hijau
- [x] Reviewer menetapkan keputusan **GO**

## 12. Merge, tag, dan GitHub Release

Langkah ini hanya boleh dilakukan setelah seluruh item wajib di bagian 11
selesai.

- [x] Branch `development/v2-finalization` telah di-merge ke `main`
- [ ] `main` ditarik ulang dari remote
- [ ] Commit merge diuji ulang
- [ ] Annotated tag `v2.0.0` dibuat pada commit final
- [ ] Tag di-push
- [ ] GitHub Release dibuat dari tag `v2.0.0`
- [ ] Release notes mencantumkan fitur, metrik, instalasi, breaking changes,
      data license, dan known limitations
- [x] URL dashboard final telah ditambahkan dan diverifikasi
- [ ] Aset dan source archive GitHub Release diverifikasi setelah publikasi
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
