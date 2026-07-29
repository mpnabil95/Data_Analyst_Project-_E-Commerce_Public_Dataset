# Data Dictionary

Dokumen ini menjelaskan sembilan tabel sumber Olist yang digunakan oleh
`app.py` dan `notebooks/ecommerce_analysis.ipynb`, termasuk grain, key, relasi,
nullability, dan field analitik turunannya.

## 1. Konvensi

- **Grain** adalah makna satu baris pada sebuah tabel.
- **PK** berarti key unik pada file sumber.
- **FK** berarti key yang menghubungkan tabel ke tabel lain.
- **Nullable** ditulis berdasarkan isi CSV yang digunakan proyek, bukan
  berdasarkan batasan database formal.
- Seluruh ID merupakan identifier anonim dan tidak boleh ditafsirkan sebagai
  identitas dunia nyata.
- Mata uang pada `price`, `freight_value`, dan `payment_value` adalah Brazilian
  Real (BRL/R$).
- Timestamp sumber tidak menyertakan informasi zona waktu.

## 2. Ringkasan tabel sumber

| Dataset | Grain | Baris | Kolom | Key utama |
|---|---|---:|---:|---|
| `customers_dataset.csv` | Satu customer record untuk satu order | 99.441 | 5 | `customer_id` |
| `geolocation_dataset.csv` | Satu observasi koordinat untuk prefix kode pos | 1.000.163 | 5 | Tidak ada PK tunggal |
| `order_items_dataset.csv` | Satu item dalam satu order | 112.650 | 7 | (`order_id`, `order_item_id`) |
| `order_payments_dataset.csv` | Satu payment record dalam satu order | 103.886 | 5 | (`order_id`, `payment_sequential`) |
| `order_reviews_dataset.csv` | Satu review record untuk satu order | 99.224 | 7 | Tidak ada PK tunggal yang sepenuhnya unik |
| `orders_dataset.csv` | Satu order | 99.441 | 8 | `order_id` |
| `product_category_name_translation.csv` | Satu pasangan nama kategori | 71 | 2 | `product_category_name` |
| `products_dataset.csv` | Satu produk anonim | 32.951 | 9 | `product_id` |
| `sellers_dataset.csv` | Satu seller anonim | 3.095 | 4 | `seller_id` |

## 3. Relasi utama

| Dari | Ke | Kardinalitas analitik | Keterangan |
|---|---|---|---|
| `orders.customer_id` | `customers.customer_id` | many-to-one | Setiap order mempunyai satu customer record |
| `order_items.order_id` | `orders.order_id` | many-to-one | Satu order dapat mempunyai banyak item |
| `order_payments.order_id` | `orders.order_id` | many-to-one | Satu order dapat mempunyai beberapa payment record |
| `order_reviews.order_id` | `orders.order_id` | many-to-one | Review dirata-ratakan ke level order |
| `order_items.product_id` | `products.product_id` | many-to-one | Setiap item merujuk satu produk |
| `order_items.seller_id` | `sellers.seller_id` | many-to-one | Setiap item merujuk satu seller |
| `products.product_category_name` | `product_category_name_translation.product_category_name` | many-to-one | Nama Portugis diterjemahkan ke Inggris jika tersedia |
| `customers.customer_zip_code_prefix` | `geolocation.geolocation_zip_code_prefix` | many-to-one setelah agregasi | Koordinat median dihitung per prefix kode pos |

`customer_id` dan `customer_unique_id` mempunyai fungsi berbeda.
`customer_id` bersifat order-scoped, sedangkan `customer_unique_id` digunakan
untuk menghubungkan pembelian berbeda dari customer anonim yang sama.

## 4. Customers

- **File:** `customers_dataset.csv`
- **Grain:** satu customer record yang digunakan oleh satu order.

| Kolom | Tipe konseptual | Nullable | Key | Deskripsi |
|---|---|:---:|---|---|
| `customer_id` | string | Tidak | PK | Identifier customer yang direferensikan oleh `orders`; unik per customer record/order |
| `customer_unique_id` | string | Tidak | Logical key | Identifier anonim lintas order untuk analisis repeat customer |
| `customer_zip_code_prefix` | integer | Tidak | FK geografis | Lima digit awal kode pos customer |
| `customer_city` | string | Tidak | — | Nama kota customer dalam data sumber |
| `customer_state` | category/string | Tidak | — | Kode state Brasil dua huruf |

## 5. Geolocation

- **File:** `geolocation_dataset.csv`
- **Grain:** satu observasi latitude/longitude untuk suatu prefix kode pos.

| Kolom | Tipe konseptual | Nullable | Key | Deskripsi |
|---|---|:---:|---|---|
| `geolocation_zip_code_prefix` | integer | Tidak | Grouping key | Lima digit awal kode pos |
| `geolocation_lat` | float | Tidak | — | Latitude observasi |
| `geolocation_lng` | float | Tidak | — | Longitude observasi |
| `geolocation_city` | string | Tidak | — | Nama kota pada observasi geolokasi |
| `geolocation_state` | category/string | Tidak | — | Kode state Brasil dua huruf |

Sebelum join, dashboard:

1. menghapus baris tanpa prefix/koordinat dan baris duplikat;
2. mempertahankan koordinat dalam bounding box konservatif Brasil:
   latitude `[-34, 6]` dan longitude `[-74, -34]`;
3. mengambil median latitude dan longitude per prefix kode pos.

Proses tersebut menggunakan 738.299 observasi valid dan menghasilkan 19.010
prefix kode pos untuk join ke tabel customer.

## 6. Order items

- **File:** `order_items_dataset.csv`
- **Grain:** satu item atau unit produk dalam satu order.

| Kolom | Tipe konseptual | Nullable | Key | Deskripsi |
|---|---|:---:|---|---|
| `order_id` | string | Tidak | FK, PK komposit | Identifier order |
| `order_item_id` | integer | Tidak | PK komposit | Nomor urut item dalam order |
| `product_id` | string | Tidak | FK | Identifier produk anonim |
| `seller_id` | string | Tidak | FK | Identifier seller anonim |
| `shipping_limit_date` | datetime | Tidak | — | Batas waktu seller menyerahkan item untuk pengiriman |
| `price` | float/BRL | Tidak | — | Harga produk, tidak termasuk freight |
| `freight_value` | float/BRL | Tidak | — | Biaya freight yang dialokasikan pada item |

## 7. Order payments

- **File:** `order_payments_dataset.csv`
- **Grain:** satu payment record atau metode pembayaran dalam satu order.

| Kolom | Tipe konseptual | Nullable | Key | Deskripsi |
|---|---|:---:|---|---|
| `order_id` | string | Tidak | FK, PK komposit | Identifier order |
| `payment_sequential` | integer | Tidak | PK komposit | Nomor urut payment record dalam order |
| `payment_type` | category/string | Tidak | — | Metode pembayaran, misalnya `credit_card`, `boleto`, atau `voucher` |
| `payment_installments` | integer | Tidak | — | Jumlah cicilan yang tercatat |
| `payment_value` | float/BRL | Tidak | — | Nilai pembayaran pelanggan pada record tersebut |

Satu order dapat mempunyai lebih dari satu record karena metode pembayaran
campuran atau transaksi berurutan. Nilai order-level harus dihitung dengan
menjumlahkan `payment_value` per `order_id`.

## 8. Order reviews

- **File:** `order_reviews_dataset.csv`
- **Grain:** satu review record yang terhubung ke satu order.

| Kolom | Tipe konseptual | Nullable | Null | Deskripsi |
|---|---|:---:|---:|---|
| `review_id` | string | Tidak | 0 | Identifier review; tidak sepenuhnya unik pada file |
| `order_id` | string | Tidak | 0 | FK ke order; beberapa order memiliki lebih dari satu record |
| `review_score` | integer | Tidak | 0 | Skor ulasan 1–5 |
| `review_comment_title` | string | Ya | 87.656 | Judul komentar review |
| `review_comment_message` | string | Ya | 58.247 | Isi komentar review |
| `review_creation_date` | datetime | Tidak | 0 | Tanggal review dibuat |
| `review_answer_timestamp` | datetime | Tidak | 0 | Timestamp review dijawab/dikirim |

Dashboard merata-ratakan seluruh `review_score` per `order_id` sebelum
menggabungkannya dengan order. Cara ini mencegah order dengan beberapa review
memiliki bobot berlebih.

## 9. Orders

- **File:** `orders_dataset.csv`
- **Grain:** satu order.

| Kolom | Tipe konseptual | Nullable | Null | Key/Deskripsi |
|---|---|:---:|---:|---|
| `order_id` | string | Tidak | 0 | PK; identifier order |
| `customer_id` | string | Tidak | 0 | FK ke `customers.customer_id` |
| `order_status` | category/string | Tidak | 0 | Status terakhir order |
| `order_purchase_timestamp` | datetime | Tidak | 0 | Timestamp pembelian |
| `order_approved_at` | datetime | Ya | 160 | Timestamp pembayaran/order disetujui |
| `order_delivered_carrier_date` | datetime | Ya | 1.783 | Timestamp diserahkan kepada carrier |
| `order_delivered_customer_date` | datetime | Ya | 2.965 | Timestamp diterima customer |
| `order_estimated_delivery_date` | datetime | Tidak | 0 | Tanggal estimasi pengiriman |

Nilai `order_status` yang tersedia adalah `approved`, `canceled`, `created`,
`delivered`, `invoiced`, `processing`, `shipped`, dan `unavailable`.
Dashboard memilih `delivered` secara default.

## 10. Product category translation

- **File:** `product_category_name_translation.csv`
- **Grain:** satu pasangan nama kategori Portugis dan Inggris.

| Kolom | Tipe konseptual | Nullable | Key | Deskripsi |
|---|---|:---:|---|---|
| `product_category_name` | string | Tidak | PK/FK | Nama kategori dalam bahasa Portugis |
| `product_category_name_english` | string | Tidak | — | Terjemahan kategori dalam bahasa Inggris |

Jika terjemahan tidak tersedia, dashboard memakai nama Portugis. Underscore
diganti spasi dan label ditampilkan dalam title case.

## 11. Products

- **File:** `products_dataset.csv`
- **Grain:** satu produk anonim.

| Kolom | Tipe konseptual | Nullable | Null | Deskripsi |
|---|---|:---:|---:|---|
| `product_id` | string | Tidak | 0 | PK; identifier produk anonim |
| `product_category_name` | string | Ya | 610 | FK ke tabel terjemahan kategori |
| `product_name_lenght` | float/integer | Ya | 610 | Panjang nama produk dalam karakter |
| `product_description_lenght` | float/integer | Ya | 610 | Panjang deskripsi produk dalam karakter |
| `product_photos_qty` | float/integer | Ya | 610 | Jumlah foto produk |
| `product_weight_g` | float | Ya | 2 | Berat produk dalam gram |
| `product_length_cm` | float | Ya | 2 | Panjang produk dalam sentimeter |
| `product_height_cm` | float | Ya | 2 | Tinggi produk dalam sentimeter |
| `product_width_cm` | float | Ya | 2 | Lebar produk dalam sentimeter |

Ejaan `lenght` dipertahankan karena merupakan nama kolom asli. Dataset tidak
menyediakan nama produk. Dashboard karena itu menampilkan kategori dan enam
karakter awal `product_id`, tanpa mengarang nama produk.

## 12. Sellers

- **File:** `sellers_dataset.csv`
- **Grain:** satu seller anonim.

| Kolom | Tipe konseptual | Nullable | Key | Deskripsi |
|---|---|:---:|---|---|
| `seller_id` | string | Tidak | PK | Identifier seller anonim |
| `seller_zip_code_prefix` | integer | Tidak | — | Lima digit awal kode pos seller |
| `seller_city` | string | Tidak | — | Kota seller |
| `seller_state` | category/string | Tidak | — | Kode state Brasil dua huruf |

Dashboard hanya menggunakan `seller_id` dan `seller_state` dalam fact table
utama v2.0.0.

## 13. Field analitik turunan

### 13.1 Order-level

| Field | Definisi |
|---|---|
| `product_gmv` | Jumlah `price` seluruh item dalam order |
| `freight_value` | Jumlah `freight_value` seluruh item dalam order |
| `order_value` | `product_gmv + freight_value` |
| `payment_value` | Jumlah seluruh payment record dalam order |
| `review_score` | Rata-rata seluruh review score pada order |
| `delivery_days` | Selisih hari antara delivery ke customer dan pembelian |
| `delivery_delay_days` / `delay_days` | Delivery aktual dikurangi estimasi; nilai positif berarti terlambat |
| `is_on_time` / `on_time` | `True` jika delivery aktual tidak melewati estimasi |
| `item_count` | Jumlah baris item dalam order |
| `unique_products` | Jumlah `product_id` unik dalam order |
| `seller_count` | Jumlah `seller_id` unik dalam order |

### 13.2 Item-level dashboard

| Field | Definisi |
|---|---|
| `gmv` | Salinan numerik `price`; product GMV pada grain item |
| `order_value` | `gmv + freight_value` pada grain item |
| `category` | Kategori Inggris, fallback Portugis, kemudian `Unknown` |
| `customer_lat`, `customer_lng` | Median koordinat valid per prefix kode pos customer |
| `customer_lifetime_delivered_orders` | Delivered order unik customer sepanjang riwayat |
| `customer_segment` | `Repeat customer`, `One-time customer`, atau `Belum ada pesanan selesai` |
| `payment_label` | Label metode pembayaran yang diformat untuk tampilan |

### 13.3 RFM dan cohort

| Field | Definisi |
|---|---|
| `reference_date` | Satu hari setelah tanggal pembelian delivered terakhir pada hasil filter |
| `recency` | Hari sejak delivered order terakhir sampai `reference_date` |
| `frequency` | Jumlah delivered order unik per `customer_unique_id` |
| `monetary` | Total `payment_value` dari delivered order terpilih |
| `segment` | Salah satu dari tujuh segmen berbasis recency, frequency, dan monetary |
| `cohort_month` | Bulan delivered order pertama customer pada ruang lingkup analisis |
| `cohort_index` | Selisih bulan antara transaksi dan `cohort_month`; M+0 adalah bulan akuisisi |
| `retention` | Customer aktif pada M+n dibagi customer pada M+0 untuk kohort yang sama |

## 14. Grain yang harus digunakan

| Analisis | Grain yang benar |
|---|---|
| Product GMV, unit, produk, kategori, seller | Item-level |
| Jumlah order, AOV, rating, delivery | Order-level |
| Payment mix | Payment-record level |
| RFM | Customer-level setelah agregasi order dan payment |
| Cohort retention | Customer-month level |
| Peta | Prefix kode pos setelah agregasi koordinat |

Mencampur grain tanpa agregasi dapat menggandakan payment, review, atau order.
Implementasi proyek membuat fact table terpisah dan melakukan deduplikasi
`order_id` sebelum menghitung metrik order-level.
