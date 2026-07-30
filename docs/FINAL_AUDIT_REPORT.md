# Final Audit Report — v2.0.0

Dokumen ini merekam bukti Quality Gate Tahap 10 untuk kandidat rilis v2.0.0.
Checklist operasional tetap berada di
[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

## 1. Identitas kandidat

- Branch: `development/v2-finalization`
- Entry point: `app.py`
- Target runtime: Python 3.11
- Target rilis: `v2.0.0`
- Baseline sebelum Tahap 10: Tahap 9 — README dan screenshots
- Tanggal audit: 29 Juli 2026
- Keputusan saat patch Tahap 10 dibuat: **CONDITIONAL NO-GO**

`CONDITIONAL NO-GO` berarti quality gate telah tersedia di repository, tetapi
commit hasil penerapan pada komputer pemilik repository belum boleh di-merge
atau diberi tag sebelum seluruh perintah pada bagian 6 menghasilkan status
hijau.

## 2. Quality gate yang ditambahkan

| Gerbang | Implementasi | Cakupan |
|---|---|---|
| Data dan metrik | `tests/test_data_metrics.py` | 9 sumber, grain, KPI, filter, empty-state, ekspor, RFM, cohort |
| Streamlit | `tests/test_streamlit_app.py` | 5 bagian, status default, empty-state, kontrol ekspor |
| Notebook | `tests/test_notebook.py` | 74 cell, 19 code cell, eksekusi tanpa output error |
| Integritas rilis | `tests/test_repository_integrity.py` | Size/SHA-256 data, artefak terlarang, pola credential, link lokal |
| CI | `.github/workflows/quality-gate.yml` | Python 3.11, application test, notebook, dependency audit |
| Konfigurasi test | `pytest.ini` | Marker `slow`, `streamlit`, dan `notebook` |

Streamlit diuji melalui `streamlit.testing.v1.AppTest`, sehingga test
berinteraksi dengan file aplikasi yang sama dengan deployment—bukan duplikasi
logika dashboard.

## 3. Baseline regresi yang dikunci

| Metrik | Expected |
|---|---:|
| Delivered orders | 96.478 |
| Unique customers | 93.358 |
| Item rows | 110.197 |
| Product GMV | R$13.221.498,11 |
| Order value | R$15.419.773,75 |
| AOV | R$159,8268387612 |
| Average rating | 4,1561865209 |
| Repeat customer | 3,0002784978% |
| Weighted retention M+1 | 0,4827206641% |
| Weighted retention M+3 | 0,2546858212% |
| Top payment segment | `High-Value One-Time` |
| Customer pada top segment | 8.466 |
| Payment share top segment | 34,8879997905% |

Nilai presisi digunakan hanya untuk mendeteksi regresi. Tampilan dashboard
tetap membulatkan angka agar mudah dibaca.

## 4. Bukti yang telah tersedia

### Diverifikasi pada workspace Tahap 10

- baseline Git sebelum perubahan bersih;
- sembilan CSV lengkap;
- size dan SHA-256 seluruh CSV cocok dengan inventaris atribusi;
- geolocation berisi 1.000.163 baris, 61.273.883 byte, dan SHA-256
  `b514f6fc991b9566aeba02aa5d67e2c3630f034b60a0e05aa0d082a3b66d88d6`;
- KPI, repeat rate, cohort retention, dan top RFM segment dihitung ulang dari
  CSV dan cocok dengan baseline;
- seluruh file Python Tahap 10 lolos parsing/kompilasi statis;
- diff tidak mengandung whitespace error;
- tidak ada credential pattern atau artefak lokal yang sengaja ditambahkan.

### Bukti yang dibawa dari tahap sebelumnya

- Tahap 7: instalasi bersih Python 3.11.15, `pip check`, import, kompilasi,
  notebook 19/19 cell, dan smoke test lima bagian lulus;
- Tahap 9: deployment publik dapat dibuka, kelima bagian dapat dinavigasi,
  dan screenshot berasal dari aplikasi deploy.

Bukti lama menjaga kontinuitas, tetapi tidak menggantikan kewajiban menjalankan
test baru pada commit Tahap 10.

## 5. Desain CI

Workflow mempunyai tiga job:

1. **Application and regression tests**
   - checkout dengan Git LFS;
   - Python 3.11;
   - instalasi `requirements-dev.txt` dan `pip check`;
   - kompilasi;
   - data/metric/integrity tests;
   - Streamlit five-section smoke test.
2. **Notebook execution**
   - environment terpisah agar memori tidak bertumpuk dengan dashboard;
   - mengeksekusi seluruh 19 code cell melalui `nbclient`.
3. **Dependency vulnerability audit**
   - tidak mengunduh dataset LFS;
   - menjalankan `pip-audit==2.10.1` terhadap `requirements-dev.txt`.

Seluruh job hanya mempunyai permission `contents: read`.

## 6. Perintah final pada komputer pemilik repository

Jalankan dari root repository pada Python 3.11:

```bash
python --version
python -m pip install -r requirements-dev.txt
python -m pip check
python -m compileall -q app.py tests
python -m pytest -m "not streamlit and not notebook"
python -m pytest -m streamlit
python -m pytest -m notebook
python -m pip install pip-audit==2.10.1
python -m pip_audit -r requirements-dev.txt
git diff --check
git status
```

Seluruh perintah harus exit code 0 dan working tree harus bersih.

## 7. Pemeriksaan manual build kandidat

Automated test tidak dapat menilai kualitas visual berdasarkan piksel.
Sebelum keputusan GO, periksa build yang menunjuk commit Tahap 10:

- desktop: 1440 × 900;
- mobile: 390 × 844;
- kelima tombol bagian tidak terpotong dan dapat dipilih;
- sidebar dapat dibuka/tutup;
- filter tanggal, state, kategori, status, dan seller state berfungsi;
- Bubble/Heatmap dapat dipilih dan peta dapat di-zoom;
- tooltip chart utama dapat dibaca;
- `Siapkan file CSV` berubah menjadi `Unduh hasil filter (.csv)`;
- CSV berhasil diunduh dan mempunyai satu baris per order;
- tidak ada teks bertabrakan, overflow horizontal, area kosong abnormal, atau
  exception.

## 8. Kriteria perubahan keputusan

Status berubah menjadi **GO** hanya jika:

- seluruh perintah bagian 6 lulus pada commit yang sama;
- ketiga job CI hijau setelah branch di-push;
- pemeriksaan manual bagian 7 lulus;
- tidak ada perubahan baru setelah audit, kecuali commit administratif merge
  yang diuji ulang;
- reviewer memastikan tag `v2.0.0` akan menunjuk commit final di `main`.

Jika satu angka regresi berubah, jangan langsung memperbarui expected value.
Tentukan lebih dahulu apakah perubahan tersebut merupakan bug atau perubahan
metodologi yang disengaja dan terdokumentasi.
