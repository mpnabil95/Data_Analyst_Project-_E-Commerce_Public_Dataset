# Methodology

Dokumen ini menjelaskan cara proyek mengubah sembilan CSV Olist menjadi
notebook analisis dan dashboard Streamlit yang dapat direproduksi.

## 1. Tujuan analisis

Analisis menjawab enam pertanyaan bisnis:

1. Bagaimana skala, pertumbuhan, dan pola bulanan bisnis?
2. Kategori apa yang unggul dari sisi unit dan Product GMV?
3. Bagaimana keterlambatan pengiriman berkaitan dengan rating?
4. Wilayah customer mana yang terbesar dan berisiko dari sisi layanan?
5. Seberapa sehat repeat purchase, RFM, dan cohort retention?
6. Bagaimana payment mix dan konsentrasi Product GMV antar-seller?

Temuan bersifat deskriptif dan observasional. Analisis tidak membuktikan
hubungan kausal.

## 2. Ruang lingkup

- Sumber: Brazilian E-Commerce Public Dataset by Olist.
- Periode timestamp pembelian dalam sumber: 2016–2018.
- Geografi: Brasil.
- Unit observasi: order, item, payment record, review, customer anonim,
  seller anonim, produk anonim, dan prefix kode pos.
- Default dashboard: seluruh rentang tanggal, seluruh state/kategori/seller,
  dengan status `delivered`.
- Mata uang: Brazilian Real (BRL/R$).

## 3. Pipeline analitik

```text
9 CSV sumber
    ↓
Penemuan file dan validasi kelengkapan
    ↓
Konversi tipe, cleaning, dan audit key
    ↓
Agregasi review, payment, dan geolocation
    ↓
Order-level fact + item-level fact
    ↓
Filter interaktif
    ↓
KPI, chart, peta, RFM, cohort, dan ekspor
```

Notebook merupakan sumber analisis lengkap. Dashboard menggunakan rumus metrik
yang sama, tetapi menghitung visual sesuai bagian aktif agar pemakaian memori
dan waktu rerun tetap terkendali.

## 4. Data ingestion dan validasi

`app.py` mencari sembilan file pada root aplikasi, `data/`,
`project_sources/`, direktori induk yang relevan, dan current working
directory. Nama dengan prefiks angka seperti `01-customers_dataset.csv` tetap
dikenali.

Sebelum membangun data mart, aplikasi memeriksa:

- semua file wajib tersedia;
- semua kolom wajib tersedia;
- jumlah baris tidak berada di bawah ambang dataset lengkap;
- file geolocation bukan pointer Git LFS atau salinan terpotong.

Notebook menambahkan audit:

- ukuran, dtype, missing value, dan duplikasi;
- uniqueness key;
- referential integrity antar-tabel;
- rekonsiliasi `payment_value` dengan `product_gmv + freight_value`.

Ambang jumlah baris pada dashboard adalah detektor kelengkapan, bukan filter
analisis.

## 5. Cleaning dan standardisasi

### 5.1 Timestamp

Kolom waktu order dikonversi dengan `errors="coerce"`. Durasi dihitung dalam
hari dengan membagi selisih detik terhadap 86.400.

### 5.2 Kategori

Nama kategori Portugis digabungkan dengan tabel terjemahan. Jika terjemahan
tidak tersedia, nama asli dipertahankan. Underscore diubah menjadi spasi dan
label ditampilkan dalam title case. Nilai yang tetap kosong diberi label
`Unknown`.

### 5.3 Review

Karena satu order dapat mempunyai beberapa record review, `review_score`
dirata-ratakan per `order_id` sebelum join. Rating dashboard kemudian dihitung
dari satu nilai review per order.

### 5.4 Geolocation

Geolocation diproses dengan urutan berikut:

1. hapus missing value pada prefix, latitude, atau longitude;
2. hapus baris duplikat;
3. ubah koordinat menjadi numerik;
4. pertahankan latitude `[-34, 6]` dan longitude `[-74, -34]`;
5. hitung median latitude/longitude per prefix kode pos;
6. join hasilnya ke customer.

Median mengurangi pengaruh observasi ekstrem dan banyak observasi pada prefix
yang sama. Peta menunjukkan lokasi representatif prefix, bukan alamat presisi.

## 6. Fact table dan aturan join

### 6.1 Order-level fact

Notebook membangun satu baris per `order_id`:

- item diagregasi menjadi jumlah item, produk unik, seller unik, Product GMV,
  dan freight;
- payment diagregasi menjadi total payment, jumlah record, maksimum cicilan,
  dan metode;
- review diagregasi menjadi rating rata-rata dan indikator komentar;
- hasilnya digabungkan dengan order dan customer.

Fact ini digunakan untuk KPI order, delivery, rating, RFM, cohort, payment, dan
analisis statistik.

### 6.2 Item-level fact

Dashboard mempertahankan satu baris per item:

```text
order_items
  → products + translation
  → sellers
  → orders + customers + review order-level + geolocation
```

Fact ini digunakan untuk filter kategori/seller, Product GMV, unit, dan
portofolio produk. Untuk metrik order-level, dashboard membuat `order_view`
dengan satu baris per `order_id`.

### 6.3 Pencegahan double counting

- Product GMV dan freight dijumlahkan pada item grain.
- Order dihitung dengan `nunique(order_id)`.
- Customer dihitung dengan `nunique(customer_unique_id)`.
- Review dirata-ratakan ke order sebelum join item.
- Payment tidak langsung dijoin ke item; payment diagregasi atau dipilih
  berdasarkan order ID.

## 7. Filter dan periode pembanding

Filter dashboard:

- rentang tanggal pembelian, inklusif;
- state customer;
- kategori produk;
- status order;
- state seller.

Filter diterapkan pada item-level fact. Karena itu, filter kategori/seller
memilih item yang cocok dan order yang mengandung item tersebut.

KPI periode sebelumnya menggunakan rentang kalender dengan panjang yang sama,
tepat sebelum tanggal awal terpilih. Delta tidak ditampilkan jika denominator
periode sebelumnya tidak valid.

Sparkline menggunakan:

- harian untuk rentang ≤60 hari;
- mingguan untuk rentang 61–180 hari;
- bulanan untuk rentang >180 hari.

## 8. Definisi metrik

| Metrik | Formula | Grain |
|---|---|---|
| Product GMV | `Σ price` | Item |
| Order value | `Σ (price + freight_value)` | Item, lalu dapat diagregasi ke order |
| Orders | `nunique(order_id)` | Order |
| Unique customers | `nunique(customer_unique_id)` | Customer |
| AOV | `total order value / order unik dalam filter` (`delivered` secara default) | Order |
| Average rating | Mean review score setelah agregasi per order | Order |
| Review coverage | Order dengan rating / seluruh order terpilih | Order |
| Delivery days | Delivery customer − purchase timestamp | Order |
| Delay days | Delivery customer − estimated delivery | Order |
| On-time rate | Mean dari `delivery_actual <= delivery_estimate` | Order delivered dengan tanggal tersedia |
| Low-rating rate | Proporsi review score ≤2 | Order ber-review |
| Repeat-customer rate | Customer dengan ≥2 delivered order / customer delivered | Customer |
| Payment share | Payment value metode / total payment value | Payment record |

Product GMV tidak mencakup freight dan bukan revenue bersih atau profit.
`payment_value` dapat berbeda sedikit dari `order_value` karena voucher,
pembulatan, atau mekanisme pembayaran.

### 8.1 Semantik filter kategori/seller

Saat kategori atau seller dipilih:

- Product GMV dan order value dashboard hanya mencakup item yang cocok;
- jumlah order adalah order unik yang memiliki item cocok;
- payment mix dan monetary RFM menggunakan keseluruhan payment dari order yang
  terpilih.

Perbedaan ini disengaja: filter memilih order melalui item, sedangkan
`payment_value` hanya bermakna sebagai total pembayaran order.

## 9. Delivery dan rating

Order dinyatakan on-time jika:

```text
order_delivered_customer_date <= order_estimated_delivery_date
```

Notebook membandingkan rating order on-time dan late dengan:

- Mann–Whitney U dua sisi untuk perbedaan distribusi rating;
- korelasi Spearman antara `delivery_days` dan `review_score`;
- low-rating rate dan rating rata-rata sebagai effect description.

Nilai p mengukur konsistensi statistik, bukan besarnya dampak atau kausalitas.
Faktor lain seperti kualitas produk, komunikasi seller, dan ekspektasi
customer tidak dikontrol oleh dataset.

## 10. RFM segmentation

RFM hanya memakai delivered order pada hasil filter aktif.

- **Reference date:** satu hari setelah tanggal pembelian delivered terakhir.
- **Recency:** hari sejak pembelian delivered terakhir.
- **Frequency:** delivered order unik per customer.
- **Monetary:** total payment value order tersebut.

Ambang dinamis:

- `R25` dan `R75`: kuartil ke-25 dan ke-75 recency;
- `M75` dan `M90`: kuartil ke-75 dan ke-90 monetary.

| Segmen | Aturan |
|---|---|
| `Champions` | Frequency ≥2, recency ≤R25, monetary ≥M75 |
| `At-Risk Repeat` | Frequency ≥2 dan recency >R75 |
| `Loyal Repeat` | Frequency ≥2 selain dua kondisi di atas |
| `High-Value One-Time` | Frequency =1 dan monetary ≥M90 |
| `Recent One-Time` | Frequency =1 dan recency ≤R25 |
| `Hibernating One-Time` | Frequency =1 dan recency >R75 |
| `Regular One-Time` | One-time customer yang tidak memenuhi kondisi lain |

Segmentasi bersifat heuristik dan relatif terhadap populasi hasil filter; ini
bukan model prediktif customer lifetime value.

## 11. Cohort retention

1. Ambil bulan delivered order pertama setiap customer sebagai
   `cohort_month`.
2. Hitung selisih bulan setiap transaksi terhadap bulan akuisisi sebagai
   `cohort_index`.
3. Hitung customer unik pada setiap pasangan cohort-month dan index.
4. Bagi jumlah M+n dengan ukuran cohort M+0.

Weighted M+1 dan M+3 hanya memakai cohort yang sudah mempunyai kesempatan
observasi selama 1 atau 3 bulan. Dashboard menampilkan M+0 sampai M+6 dan
maksimal 14 cohort matang. Nilai default yang telah diregresikan:

- repeat-customer rate: 3,0003%;
- weighted M+1 retention: 0,4827%;
- weighted M+3 retention: 0,2547%.

Customer Value dihitung secara lazy: fungsi RFM/cohort hanya dipanggil saat
bagian tersebut dipilih.

## 12. Nilai default yang direkonsiliasi

Untuk seluruh rentang dengan status `delivered`:

| Metrik | Nilai |
|---|---:|
| Delivered orders | 96.478 |
| Unique customers | 93.358 |
| Item rows | 110.197 |
| Product GMV | R$13.221.498,11 |
| Order value | R$15.419.773,75 |
| AOV | R$159,83 |
| Average rating | 4,1562 / 5 |

Angka mentah disimpan dengan presisi penuh; pembulatan di atas mengikuti
format tampilan.

## 13. Reproducibility

- Python target: 3.11.
- Dashboard: `requirements.txt`.
- Notebook: `requirements-notebook.txt`.
- Audit/development: `requirements-dev.txt`.
- Tahap 7 telah memverifikasi instalasi bersih pada Python 3.11.15,
  `pip check`, import utama, kompilasi, lima bagian UI, dan eksekusi 19/19 code
  cell notebook.
- `geolocation_dataset.csv` disimpan melalui Git LFS.

## 14. Batasan

- Data historis 2016–2018 tidak mewakili kondisi pasar saat ini.
- Data dianonimkan; nama produk dan identitas customer/seller tidak tersedia.
- Dataset tidak memuat profit, margin, biaya promosi, inventory, traffic, atau
  conversion funnel.
- Product GMV bukan revenue bersih dan bukan profit.
- Review tidak tersedia pada seluruh order.
- Hubungan delivery-rating adalah asosiasi observasional.
- Pada multi-seller order, keterlambatan tidak selalu dapat diatribusikan
  kepada satu seller.
- Geolocation berbasis prefix kode pos dan median, bukan alamat aktual.
- Cohort dibatasi oleh akhir periode observasi sehingga cohort muda mengalami
  right-censoring.
- RFM memakai aturan kuartil dan harus divalidasi sebelum digunakan untuk
  keputusan pemasaran nyata.

## 15. Referensi internal

- Struktur kolom: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)
- Sumber dan lisensi data: [`DATA_ATTRIBUTION.md`](DATA_ATTRIBUTION.md)
- Riwayat dashboard: [`DASHBOARD_CHANGELOG.md`](DASHBOARD_CHANGELOG.md)
- Gerbang rilis: [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)
