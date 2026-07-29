# Data Attribution and License

## 1. Sumber data

Proyek ini menggunakan **Brazilian E-Commerce Public Dataset by Olist**:

- Creator/publisher: **Olist**
- Platform: **Kaggle**
- Halaman sumber:
  <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>
- Cakupan: order e-commerce anonim di Brasil, termasuk customer, seller,
  produk, item, payment, review, dan geolocation.
- Lisensi dataset: **Creative Commons
  Attribution-NonCommercial-ShareAlike 4.0 International
  (CC BY-NC-SA 4.0)**
- Teks lisensi:
  <https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode>
- Ringkasan:
  <https://creativecommons.org/licenses/by-nc-sa/4.0/>

Attribution statement:

> Brazilian E-Commerce Public Dataset by Olist, provided by Olist through
> Kaggle, licensed under CC BY-NC-SA 4.0. This project cleans, joins,
> aggregates, and visualizes the data; Olist does not endorse this project.

## 2. Kewajiban penggunaan dataset

CC BY-NC-SA 4.0 mengharuskan pengguna:

- memberikan atribusi yang sesuai kepada Olist dan menautkan sumber;
- menautkan lisensi;
- menjelaskan bahwa material telah diproses atau diadaptasi;
- menggunakan material hanya untuk tujuan nonkomersial;
- membagikan adaptasi dataset di bawah lisensi yang sama atau lisensi yang
  kompatibel;
- tidak menerapkan pembatasan tambahan yang menghalangi hak yang diberikan
  lisensi.

Teks lisensi resmi tetap menjadi rujukan hukum utama. Dokumentasi ini bukan
nasihat hukum.

## 3. Perubahan yang dilakukan proyek

CSV sumber dipertahankan sebagai data mentah. Pipeline analitik melakukan
transformasi in-memory berikut:

- konversi timestamp dan tipe numerik;
- penghapusan duplikasi geolocation;
- pembuangan koordinat di luar bounding box konservatif Brasil;
- median koordinat per prefix kode pos;
- agregasi item, payment, dan review pada grain yang sesuai;
- terjemahan dan pemformatan kategori;
- derivasi Product GMV, order value, delivery, rating, RFM, cohort retention,
  dan segmentasi customer;
- filter dan visualisasi interaktif.

Ekspor dashboard adalah tabel turunan dari hasil filter dan tetap mengandung
material yang berasal dari dataset Olist.

## 4. Pemisahan lisensi kode dan data

| Material | Pemegang hak/sumber | Lisensi |
|---|---|---|
| `app.py`, konfigurasi, dan kode asli proyek | Muhammad Pangeran Nabil | MIT License |
| Dokumentasi asli proyek | Muhammad Pangeran Nabil | MIT License, kecuali kutipan atau material pihak ketiga |
| Kode dan narasi asli dalam notebook | Muhammad Pangeran Nabil | MIT License |
| Tabel, angka, dan grafik notebook yang diturunkan dari data Olist | Olist dan kontributor adaptasi yang relevan | CC BY-NC-SA 4.0 |
| `data/*.csv` | Olist | CC BY-NC-SA 4.0 |
| Transformasi atau ekspor yang mengandung bagian substansial data Olist | Olist dan kontributor adaptasi yang relevan | CC BY-NC-SA 4.0 |
| Nama dan merek Olist/Kaggle | Pemilik masing-masing | Tidak diberikan melalui MIT |

File `LICENSE` di root tidak melisensikan ulang CSV Olist. Pengguna yang hanya
ingin memakai kode tetap harus memperoleh dataset secara sah dan mematuhi
lisensinya.

## 5. Inventaris dan integritas file

Checksum berikut merepresentasikan file yang diverifikasi pada 29 Juli 2026.

| File | Baris data | Ukuran byte | SHA-256 |
|---|---:|---:|---|
| `customers_dataset.csv` | 99.441 | 9.033.957 | `983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2` |
| `geolocation_dataset.csv` | 1.000.163 | 61.273.883 | `b514f6fc991b9566aeba02aa5d67e2c3630f034b60a0e05aa0d082a3b66d88d6` |
| `order_items_dataset.csv` | 112.650 | 15.438.671 | `0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279` |
| `order_payments_dataset.csv` | 103.886 | 5.777.138 | `4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0` |
| `order_reviews_dataset.csv` | 99.224 | 14.346.950 | `81336b6e5183133b632a3d9ed899428e33430987fa540926a6daa8b4a2157598` |
| `orders_dataset.csv` | 99.441 | 17.654.914 | `8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf` |
| `product_category_name_translation.csv` | 71 | 2.542 | `9da093e114e517534d7a6903b253b0d24a582830b99ea9e8ef48a90b79d60967` |
| `products_dataset.csv` | 32.951 | 2.379.446 | `3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc` |
| `sellers_dataset.csv` | 3.095 | 174.703 | `1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e` |

Jumlah baris tidak mencakup header. `geolocation_dataset.csv` dikelola dengan
Git LFS; setelah clone, jalankan `git lfs pull` sebelum memulai dashboard.

## 6. Citation

Format sitasi yang disarankan:

```text
Olist. (2018). Brazilian E-Commerce Public Dataset by Olist [Data set].
Kaggle. https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
```

BibTeX:

```bibtex
@dataset{olist_brazilian_ecommerce,
  author    = {Olist},
  title     = {Brazilian E-Commerce Public Dataset by Olist},
  year      = {2018},
  publisher = {Kaggle},
  url       = {https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce},
  note      = {Licensed under CC BY-NC-SA 4.0}
}
```

## 7. Disclaimer

Proyek ini merupakan analisis independen untuk pendidikan dan portfolio.
Proyek tidak berafiliasi dengan, disponsori oleh, atau didukung secara resmi
oleh Olist maupun Kaggle. Data dianonimkan, tetapi pengguna tetap harus
menghindari upaya re-identifikasi.
