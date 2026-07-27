# Riwayat Pengembangan Dashboard `app_2.py`

> Dokumentasi perubahan `app_2_v1.py` hingga `app_2_v15.py`  
> Proyek: **FP-E-Commerce — Olist Commerce Intelligence**  
> Framework: **Streamlit, Pandas, Plotly, Folium, dan Streamlit-Folium**  
> Versi final yang direkomendasikan: **`app_2_v15.py`**

---

## 1. Tujuan Dokumentasi

Dokumen ini menjelaskan evolusi dashboard e-commerce berbasis Streamlit mulai dari revisi pertama (`app_2_v1.py`) sampai versi final (`app_2_v15.py`). Dokumentasi disusun untuk:

1. memberikan riwayat teknis yang jelas sebelum project dipublikasikan ke GitHub;
2. menjelaskan masalah yang ditemukan pada setiap tahap pengembangan;
3. mencatat solusi yang diterapkan pada setiap versi;
4. menunjukkan alasan perubahan arsitektur komponen visual, terutama grafik dan KPI card;
5. membantu maintainer berikutnya memahami keputusan desain tanpa harus membandingkan seluruh file secara manual.

### Catatan rekonstruksi

Riwayat ini disusun berdasarkan file versi yang tersimpan, snapshot `app_2.py`, serta catatan evaluasi visual selama proses revisi. File bernama eksplisit `app_2_v2.py` sampai `app_2_v15.py` tersedia dalam arsip. Untuk `v1`, perubahan dipetakan dari snapshot revisi pertama `app_2.py` yang dibuat setelah evaluasi terhadap versi awal.

Pada beberapa versi, terutama `v3`, perubahan bersifat stabilisasi dan tidak mengubah logika analitik utama. Karena itu, dokumentasi membedakan antara:

- **perubahan fungsional**, yaitu perubahan fitur, pemrosesan data, atau perilaku aplikasi;
- **perubahan presentasi**, yaitu perubahan CSS, tema, grafik, KPI, dan responsivitas;
- **perubahan stabilisasi**, yaitu perbaikan kecil untuk mempertahankan hasil revisi sebelumnya.

---

## 2. Gambaran Versi Awal `app_2.py`

Sebelum seri revisi `v1–v15`, dashboard awal sudah memiliki fondasi analitik yang lengkap. Dashboard dirancang untuk Brazilian E-Commerce Public Dataset by Olist dan memproses sembilan dataset utama:

- `customers_dataset.csv`;
- `sellers_dataset.csv`;
- `order_payments_dataset.csv`;
- `product_category_name_translation.csv`;
- `products_dataset.csv`;
- `geolocation_dataset.csv`;
- `order_reviews_dataset.csv`;
- `order_items_dataset.csv`;
- `orders_dataset.csv`.

### 2.1 Fitur dasar yang telah tersedia

Versi awal telah menyediakan:

- pembacaan dataset lokal dan unggahan melalui sidebar;
- normalisasi nama file, termasuk dukungan prefiks angka seperti `01-customers_dataset.csv`;
- validasi kelengkapan file dan kolom wajib;
- cache pembacaan data menggunakan `st.cache_data`;
- pembangunan data mart pada level item pesanan;
- penggabungan data order, customer, produk, seller, review, pembayaran, dan geolokasi;
- filter tanggal, state customer, kategori, status pesanan, dan state seller;
- KPI berupa GMV, jumlah pesanan, customer unik, average order value, dan rating;
- perbandingan KPI dengan periode sebelumnya;
- grafik tren GMV dan pesanan;
- analisis status pesanan, kategori, state, seller, layanan pengiriman, review, dan pembayaran;
- peta customer interaktif menggunakan Folium dalam mode bubble map dan heatmap;
- tabel kualitas dataset;
- ekspor hasil filter ke CSV.

### 2.2 Struktur halaman

Dashboard menggunakan empat tab utama:

1. **Ringkasan** — tren transaksi, status pesanan, kategori, dan kontribusi wilayah;
2. **Customer & Peta** — distribusi customer dan visualisasi geospasial;
3. **Produk & Seller** — performa produk, kategori, seller, dan state seller;
4. **Layanan & Pembayaran** — pengiriman, ulasan, keterlambatan, dan metode pembayaran.

### 2.3 Masalah awal

Walaupun fungsionalitas analitik sudah lengkap, beberapa masalah visual dan deployment masih ditemukan:

- background Plotly transparan menyebabkan grafik menyatu dengan background dashboard;
- warna label, sumbu, legend, dan grid belum selalu terbaca;
- aplikasi gagal menemukan dataset ketika file dashboard dipindahkan ke subfolder;
- KPI card masih sederhana dan belum memiliki sparkline;
- belum tersedia dukungan tema gelap dan layout mobile yang memadai;
- penggunaan HTML custom pada KPI kemudian menimbulkan masalah teks HTML tampil secara literal;
- implementasi light mode dan dark mode berkembang tidak seimbang;
- tab navigasi masih terlihat menyatu dan kurang menyerupai kontrol yang dapat diklik;
- kode state Brasil seperti `SP`, `RJ`, dan `MG` belum ramah bagi pengguna nonteknis;
- chart produk terlaris hanya menampilkan potongan `product_id` yang tampak abstrak;
- label pada diagram retensi customer dapat saling bertabrakan.

Seri `v1–v15` berfokus untuk menyelesaikan masalah-masalah tersebut tanpa mengubah inti analisis data.

---

## 3. Ringkasan Kronologi Versi

| Versi | Tanggal | Fokus utama | Hasil utama |
|---|---:|---|---|
| `v1` | 17 Juli 2026 | Kontras visual Plotly | Grafik dipisahkan secara visual dari background dashboard |
| `v2` | 17 Juli 2026 | Penemuan dataset | Dashboard dapat membaca folder data di direktori induk |
| `v3` | 17 Juli 2026 | Stabilisasi | Perbaikan path dan kontras grafik dikonsolidasikan |
| `v4` | 17 Juli 2026 | Redesign UI | Dark-mode toggle, sparkline SVG, dan responsive CSS diperkenalkan |
| `v5` | 17 Juli 2026 | Koreksi sparkline | Konstruksi SVG diperbaiki, tetapi rendering note masih berisiko |
| `v6` | 17 Juli 2026 | Sanitasi KPI | Input KPI dibersihkan melalui `clean_metric_text()` |
| `v7` | 18 Juli 2026 | Penguatan KPI HTML | Sanitasi dan struktur SVG dibuat lebih eksplisit dan aman |
| `v8` | 18 Juli 2026 | Pemisahan komponen KPI | Sparkline dipindahkan ke Plotly dan note memakai `st.caption()` |
| `v9` | 18 Juli 2026 | Penyatuan kembali KPI | KPI disatukan dalam satu card dengan SVG yang lebih terstruktur |
| `v10` | 18 Juli 2026 | Migrasi ke native Streamlit | Value dan delta mulai menggunakan `st.metric()` |
| `v11` | 18 Juli 2026 | Executive KPI hybrid | Header, value, sparkline, dan badge delta dirancang ulang |
| `v12` | 18 Juli 2026 | KPI native penuh | HTML custom KPI hampir seluruhnya dihapus |
| `v13` | 19 Juli 2026 | Konsolidasi native KPI | API KPI final, key unik, validasi sparkline, dan tinggi card stabil |
| `v14` | 19 Juli 2026 | Final dark-only | Seluruh dashboard dikonsolidasikan menjadi tema gelap tunggal |
| `v15` | 19 Juli 2026 | Final UI polish | Navigasi, label state, identitas produk, dan diagram retensi disempurnakan |

---

# 4. Rincian Perubahan Setiap Versi

## 4.1 `app_2_v1.py` — Perbaikan Kontras Grafik

### Latar belakang

Pada dashboard awal, `paper_bgcolor` dan `plot_bgcolor` Plotly menggunakan warna transparan. Dalam beberapa kondisi, warna grafik dan teks menyatu dengan background halaman sehingga visual sulit dibaca.

### Perubahan utama

Fungsi `style_figure()` diperbarui dengan:

- background grafik putih eksplisit;
- warna teks utama yang lebih gelap;
- warna title, tick, label sumbu, dan legend yang ditentukan secara eksplisit;
- grid Y yang lebih terlihat;
- garis sumbu X yang lebih jelas;
- hover label dengan background putih dan teks gelap;
- margin grafik yang lebih lapang;
- ukuran judul grafik yang ditingkatkan.

Contoh konsep perubahan:

```python
paper_bgcolor = "#FFFFFF"
plot_bgcolor = "#FFFFFF"
font_color = "#1E293B"
grid_color = "#E2E8F0"
```

### Dampak

- Grafik tidak lagi terlihat menyatu dengan background aplikasi.
- Line chart, bar chart, histogram, dan donut chart menjadi lebih mudah dibaca.
- Dashboard memperoleh baseline visual yang lebih menyerupai business intelligence dashboard.

### Batasan

- Tema masih berorientasi light mode.
- KPI card belum memiliki sparkline.
- Penemuan sumber data masih terbatas pada folder aplikasi dan working directory.

---

## 4.2 `app_2_v2.py` — Pencarian Dataset pada Folder Induk

### Latar belakang

Ketika file dashboard dipindahkan ke subfolder seperti `v2-rewrite/`, folder `data/` berada satu tingkat di atas file aplikasi. Implementasi sebelumnya hanya mencari dataset di:

- direktori file aplikasi;
- `data/` di dalam direktori aplikasi;
- `project_sources/` di dalam direktori aplikasi;
- current working directory.

Akibatnya, dashboard menyatakan dataset tidak ditemukan meskipun file CSV sebenarnya tersedia.

### Perubahan utama

Fungsi `discover_local_sources()` diperluas untuk mencari pada:

```python
APP_DIR.parent
APP_DIR.parent.parent
```

Untuk setiap direktori induk, dashboard juga memeriksa:

```text
<data-induk>/data/
<data-induk>/project_sources/
```

### Dampak

Dashboard menjadi lebih fleksibel terhadap struktur repository seperti:

```text
project-root/
├── data/
│   └── *.csv
└── v2-rewrite/
    └── app_2_v2.py
```

### Nilai teknis

Perubahan ini penting untuk deployment GitHub karena file aplikasi tidak harus berada dalam folder yang sama dengan dataset. Struktur project dapat dipisahkan dengan lebih rapi.

---

## 4.3 `app_2_v3.py` — Checkpoint Stabilisasi

### Fokus

`v3` berfungsi sebagai versi konsolidasi setelah perbaikan kontras dan path dataset.

### Perubahan dan kondisi

- mekanisme pencarian folder induk dipertahankan;
- style grafik berkontras tinggi dipertahankan;
- struktur filter, data mart, peta, tab, dan ekspor tidak diubah secara fundamental;
- tidak ditemukan perubahan besar pada formula KPI maupun agregasi data.

### Dampak

`v3` menjadi checkpoint yang relatif stabil sebelum redesign antarmuka pada `v4`.

### Catatan

Versi ini lebih tepat dikategorikan sebagai **maintenance release** daripada feature release. Tujuannya adalah memastikan perbaikan sebelumnya tidak merusak logika analitik.

---

## 4.4 `app_2_v4.py` — Redesign UI, Sparkline, Dark Mode, dan Responsivitas

### Latar belakang

Dashboard telah berfungsi, tetapi visual KPI masih sederhana. Target berikutnya adalah membuat tampilan lebih modern dan mendekati dashboard Power BI atau executive cockpit.

### Perubahan utama

#### 1. State untuk tema

Diperkenalkan state:

```python
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
```

Sidebar memperoleh toggle dark mode.

#### 2. KPI dengan sparkline

Fungsi `metric_card()` menerima parameter baru:

```python
spark: list[float] | None = None
```

Data tren dikonversi menjadi titik SVG dan disisipkan ke KPI card.

#### 3. Responsive CSS

Media query ditambahkan untuk:

- mengurangi padding halaman pada layar sempit;
- mengecilkan judul hero;
- mengecilkan nilai KPI;
- menurunkan tinggi minimum card;
- meningkatkan keterbacaan pada perangkat mobile.

#### 4. Dark mode awal

Ketika toggle aktif, CSS mengganti:

- background aplikasi;
- warna card;
- warna border;
- warna title, value, note, dan section heading.

### Dampak

- Dashboard mulai memiliki identitas visual modern.
- KPI dapat menampilkan mini-trend.
- Pengguna dapat mencoba tema terang dan gelap.
- Dashboard mulai responsif pada layar kecil.

### Masalah yang muncul

KPI dibangun menggunakan string HTML berlapis dan SVG inline. Kombinasi f-string, HTML, SVG, dan data dinamis meningkatkan risiko:

- sintaks f-string tidak stabil;
- tag HTML tampil sebagai teks;
- card terpotong;
- spacing tidak konsisten;
- perbedaan rendering antarversi Streamlit.

Masalah inilah yang mendominasi revisi `v5–v12`.

---

## 4.5 `app_2_v5.py` — Koreksi Konstruksi SVG Sparkline

### Latar belakang

Ekspresi untuk membangun atribut `points` SVG pada `v4` terlalu kompleks dan rentan terhadap konflik kurung kurawal pada f-string.

### Perubahan utama

Penyusunan string sparkline diperbaiki sehingga ekspresi:

```python
" ".join(points)
```

dapat diproses dengan benar di dalam SVG.

### Eksperimen rendering note

Pada tahap ini, `note` dimasukkan langsung ke HTML card agar memungkinkan format yang lebih fleksibel. Namun, keputusan tersebut membuka risiko:

- HTML dari `note` tidak terkontrol;
- entity dan tag dapat ditampilkan tidak sesuai;
- perbedaan perilaku sanitasi Streamlit menjadi lebih terlihat.

### Dampak

- Sparkline lebih mungkin dirender tanpa syntax error.
- Struktur KPI masih belum stabil sepenuhnya.
- Versi ini menjadi tahap eksperimen, bukan solusi final.

---

## 4.6 `app_2_v6.py` — Sanitasi Terpusat untuk Teks KPI

### Latar belakang

Setelah HTML mulai terlihat sebagai teks pada KPI, dibutuhkan mekanisme untuk memastikan seluruh input KPI diperlakukan sebagai plain text.

### Perubahan utama

Diperkenalkan fungsi:

```python
def clean_metric_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", str(text))
    return html.escape(text)
```

Fungsi tersebut digunakan untuk:

- title KPI;
- value KPI;
- note KPI.

### Tujuan teknis

Sanitasi dilakukan melalui dua tahap:

1. menghapus tag HTML dengan regular expression;
2. melakukan HTML escaping terhadap karakter yang tersisa.

### Dampak

- Parameter KPI tidak lagi dipercaya sebagai HTML.
- Risiko tag HTML ikut dirender atau tampil secara literal berkurang.
- Komponen KPI menjadi lebih aman terhadap data dinamis.

### Batasan

Walaupun teks sudah dibersihkan, struktur card masih menggabungkan HTML dan SVG dalam satu string. Dengan demikian, potensi masalah layout belum sepenuhnya hilang.

---

## 4.7 `app_2_v7.py` — Penguatan Struktur HTML KPI

### Fokus

`v7` memperjelas kontrak komponen KPI: semua input diperlakukan sebagai plain text dan sparkline tidak boleh menerima HTML dari luar.

### Perubahan utama

- `safe_title`, `safe_value`, dan `safe_note` dibuat secara eksplisit;
- tag pada note dihapus sebelum di-escape;
- sparkline hanya dibuat jika data memiliki lebih dari satu titik;
- SVG menggunakan `preserveAspectRatio="none"`;
- elemen polyline ditutup secara eksplisit;
- HTML card dibangun sebagai satu variabel `card_html` sebelum dikirim ke `st.markdown()`.

### Dampak

- Alur sanitasi menjadi lebih mudah dibaca dan diaudit.
- Data sparkline satu titik tidak lagi dipaksakan menjadi garis.
- Struktur komponen lebih defensif daripada `v6`.

### Batasan

KPI masih bergantung pada `unsafe_allow_html=True`. Masalah spesifik browser atau perubahan DOM Streamlit masih dapat memengaruhi hasil akhir.

---

## 4.8 `app_2_v8.py` — Memisahkan HTML, Plotly, dan Caption

### Latar belakang

Menyatukan title, value, SVG, dan note dalam satu HTML card masih menghasilkan tampilan yang tidak konsisten. `v8` mencoba mengurangi ketergantungan pada HTML custom.

### Perubahan utama

KPI dipecah menjadi beberapa komponen:

1. title dan value tetap dirender melalui HTML card;
2. sparkline tidak lagi menggunakan SVG inline, tetapi menggunakan mini-chart Plotly;
3. note ditampilkan melalui komponen native `st.caption()`;
4. seluruh bagian ditempatkan di dalam `st.container()`.

### Dampak

- Note tidak lagi berada di dalam nested HTML.
- Sparkline memperoleh rendering Plotly yang lebih konsisten.
- Risiko teks HTML tampil literal berkurang.

### Konsekuensi visual

Karena card HTML, chart Plotly, dan caption adalah tiga blok Streamlit terpisah, tampilan KPI dapat terlihat seperti beberapa elemen yang tidak benar-benar berada dalam satu card. Ini mendorong upaya penyatuan kembali pada `v9`.

---

## 4.9 `app_2_v9.py` — Penyatuan Kembali KPI dalam Satu Card

### Latar belakang

Pendekatan `v8` lebih stabil secara rendering, tetapi kontinuitas visual card berkurang. `v9` mencoba mengembalikan semua elemen ke satu struktur visual.

### Perubahan utama

- title, value, sparkline, dan note kembali ditempatkan dalam satu HTML card;
- sparkline menggunakan class khusus `.spark-mini`;
- titik sparkline dihitung dengan pembagi yang aman menggunakan `max(len(spark) - 1, 1)`;
- semua teks tetap melewati `clean_metric_text()`;
- struktur HTML diberi jarak dan baris yang lebih jelas agar mudah dipelihara.

### Dampak

- KPI kembali terlihat sebagai satu unit visual.
- Sanitasi input tetap dipertahankan.
- Kode lebih terbaca daripada implementasi SVG awal.

### Batasan

Solusi masih bergantung pada satu string HTML yang besar. Pada hasil pengujian, masalah rendering belum sepenuhnya hilang. Karena itu, mulai `v10`, arsitektur KPI dipindahkan ke komponen native Streamlit.

---

## 4.10 `app_2_v10.py` — Migrasi KPI ke `st.metric()`

### Latar belakang

Setelah beberapa iterasi HTML, akar masalah dinilai berasal dari ketergantungan berlebihan pada custom HTML di dalam layout Streamlit.

### Perubahan utama

Diperkenalkan fungsi baru:

```python
render_kpi_card(...)
```

KPI ditempatkan dalam:

```python
st.container(border=True)
```

Kemudian:

- title masih diberi aksen kecil melalui HTML;
- value dan delta menggunakan `st.metric()`;
- sparkline tetap dapat dibuat menggunakan Plotly;
- note/value tidak lagi dibangun sebagai nested HTML.

### Dampak

- Nilai KPI dan delta menggunakan rendering resmi Streamlit.
- Risiko HTML literal turun secara signifikan.
- Responsivitas mengikuti perilaku layout Streamlit.
- Card mulai lebih kompatibel dengan perubahan versi Streamlit.

### Batasan

Perpaduan antara title HTML dan `st.metric()` masih menghasilkan layout hybrid. Ukuran, jarak, dan tinggi antarcard belum sepenuhnya seragam.

---

## 4.11 `app_2_v11.py` — Eksperimen Executive KPI Hybrid

### Tujuan

`v11` mencoba meningkatkan estetika KPI agar lebih menyerupai executive dashboard.

### Perubahan utama

- header KPI menggunakan aksen garis vertikal;
- value dibuat lebih besar melalui HTML;
- sparkline Plotly dapat ditempatkan di bawah value;
- delta ditampilkan sebagai badge berbentuk pill;
- parameter `trend` dan `icon` diperkenalkan.

### Dampak positif

- KPI memiliki hierarki visual yang kuat.
- Warna aksen lebih terlihat.
- Delta memperoleh treatment visual khusus.

### Masalah hasil pengujian

Versi ini kembali mencampur beberapa blok HTML dan Plotly dalam satu container. Pada tampilan aktual, layout menjadi berantakan dan tinggi card tidak konsisten. Selain itu, badge delta menggunakan gaya positif secara umum sehingga tidak selalu mencerminkan delta negatif secara semantik.

### Keputusan berikutnya

Daripada terus menambah CSS dan HTML custom, `v12` menyederhanakan KPI menjadi komponen native sepenuhnya.

---

## 4.12 `app_2_v12.py` — KPI Native Streamlit Penuh

### Latar belakang

Hasil `v11` menunjukkan bahwa tampilan kompleks belum tentu lebih stabil. Prioritas dialihkan dari dekorasi menuju keandalan rendering.

### Perubahan utama

Fungsi KPI `v12` menggunakan:

- `st.container(border=True)` sebagai card;
- `st.caption()` untuk header;
- `st.metric()` untuk nilai;
- Plotly untuk sparkline;
- `st.caption()` untuk delta atau keterangan.

HTML custom untuk isi utama KPI dihapus.

### Dampak

- Risiko HTML tampil sebagai teks hampir sepenuhnya dieliminasi.
- Komponen lebih mudah dipelihara.
- Tampilan lebih konsisten dengan lifecycle Streamlit.
- KPI layanan seperti waktu pengiriman, keterlambatan, dan ulasan negatif juga menggunakan komponen yang sama.

### Batasan

- Delta belum dimanfaatkan langsung di dalam `st.metric()` pada semua skenario.
- Ukuran card dan spacing masih perlu dikunci melalui CSS.
- Implementasi tema terang dan gelap masih tidak seimbang.

---

## 4.13 `app_2_v13.py` — Konsolidasi Arsitektur KPI Final

### Tujuan

`v13` menyatukan pelajaran dari `v10–v12` menjadi API KPI yang lebih matang.

### Perubahan utama

#### 1. Signature KPI yang lebih jelas

```python
render_kpi_card(
    title,
    value,
    accent,
    *,
    delta=None,
    note=None,
    spark=None,
    key=...
)
```

Keyword-only arguments mencegah tertukarnya `delta`, `note`, dan `accent`.

#### 2. `st.metric()` sebagai inti

Label, value, dan delta dirender melalui `st.metric()`.

#### 3. Validasi sparkline

Nilai `None`, `NaN`, dan infinite dikeluarkan sebelum chart dibuat. Sparkline hanya ditampilkan jika tersedia setidaknya dua titik valid.

#### 4. Key unik Plotly

Setiap mini-chart memperoleh key unik seperti:

```python
key=f"spark_{key}"
```

Hal ini mencegah konflik elemen Plotly yang identik.

#### 5. Static sparkline

Sparkline menggunakan:

```python
"staticPlot": True
```

Tujuannya agar mini-chart tidak menampilkan toolbar atau interaksi yang tidak diperlukan.

#### 6. Tinggi card lebih konsisten

Ketika sparkline tidak tersedia, spacer tetap disediakan agar card tidak berubah tinggi secara drastis.

#### 7. Perbaikan delta

`percent_delta()` mulai mengembalikan `None` jika periode pembanding tidak valid. Ini lebih sesuai untuk `st.metric()` dibandingkan string panjang seperti “Periode pembanding tidak tersedia”.

### Dampak

- Arsitektur KPI menjadi stabil dan reusable.
- Masalah HTML literal diselesaikan pada level desain komponen.
- Parameter KPI lebih sulit disalahgunakan.
- Mini-chart lebih aman dan konsisten.

### Masalah tersisa

`v13` masih mempertahankan toggle light/dark. Sementara itu, sebagian besar Plotly masih menggunakan background putih dan beberapa annotation memakai warna navy. Akibatnya:

- light mode terlihat cukup baik;
- dark mode hanya mengubah sebagian komponen;
- sidebar, input, tab, tabel, colorbar, legend, tooltip, dan annotation belum seluruhnya mengikuti tema;
- terjadi ketimpangan kualitas visual antara kedua mode.

Masalah ini menjadi alasan utama pembuatan `v14`.

---

## 4.14 `app_2_v14.py` — Final Dark-Only Dashboard

### Keputusan desain

Daripada mempertahankan dua tema yang kualitasnya tidak seimbang, `v14` menetapkan satu tema final: **dark mode only**.

Pendekatan ini mengurangi kompleksitas CSS, menghilangkan konflik tema, dan memungkinkan seluruh komponen memperoleh treatment visual yang konsisten.

### Perubahan utama

#### 1. Penghapusan toggle tema

Toggle light/dark di sidebar dihapus. Dashboard selalu menggunakan tema gelap.

#### 2. Design token dark mode

Palet warna diperluas untuk memisahkan fungsi setiap token:

```python
COLORS = {
    "navy": ...,
    "surface": ...,
    "surface_2": ...,
    "blue": ...,
    "cyan": ...,
    "violet": ...,
    "emerald": ...,
    "amber": ...,
    "rose": ...,
    "text": ...,
    "muted": ...,
    "grid": ...,
    "border": ...,
}
```

Token tersebut digunakan secara konsisten pada card, grafik, teks, grid, border, tooltip, dan annotation.

#### 3. CSS dark mode menyeluruh

CSS tidak hanya mengubah `.stApp`, tetapi juga mencakup:

- sidebar;
- label dan caption;
- date input;
- multiselect dan tag;
- popover dan listbox;
- tab aktif dan nonaktif;
- metric card;
- dataframe;
- tombol download;
- insight box;
- expander;
- divider;
- placeholder dan help text.

#### 4. KPI final berbasis komponen native

KPI menggunakan kombinasi final:

- `st.container(border=True)`;
- `st.metric()`;
- `st.caption()`;
- Plotly sparkline;
- key unik;
- validasi data sparkline;
- delta opsional;
- note opsional.

Tidak ada title, value, note, atau delta yang disisipkan ke nested HTML.

#### 5. Delta yang aman

Jika pembanding tidak valid, `percent_delta()` mengembalikan `None`. Dengan demikian, Streamlit tidak menampilkan teks tidak relevan atau nilai seperti `undefined`.

#### 6. Plotly dark mode

Fungsi `style_figure()` disesuaikan untuk:

- `paper_bgcolor` dan `plot_bgcolor` gelap;
- font terang;
- grid gelap dengan kontras cukup;
- legend gelap;
- hover label gelap;
- title dan tick yang terbaca;
- colorbar title dan tick berwarna terang;
- annotation yang tidak lagi menggunakan warna navy gelap.

#### 7. Donut chart dan annotation

Teks di tengah donut menggunakan token `text`, bukan `navy`. Border irisan dan label juga disesuaikan agar terbaca pada background gelap.

#### 8. Responsivitas

Layout KPI menggunakan aturan wrap:

- desktop: lima KPI dapat berada dalam satu baris;
- tablet: kolom membungkus menjadi dua;
- mobile: satu KPI per baris;
- nilai KPI menggunakan ukuran adaptif;
- hero dan padding halaman mengecil pada viewport sempit.

#### 9. File konfigurasi pendamping

Versi final disertai rekomendasi `.streamlit/config.toml` untuk mengunci warna tema Streamlit dan mengurangi ketergantungan terhadap preferensi browser atau user.

### Dampak akhir

- tidak ada lagi ketimpangan light mode dan dark mode;
- tidak ada toggle tema yang dapat menghasilkan kombinasi CSS setengah aktif;
- KPI tidak menampilkan HTML sebagai teks;
- grafik, legend, tooltip, colorbar, dan annotation konsisten;
- sidebar dan input dapat dibaca dengan jelas;
- tampilan lebih siap dipublikasikan sebagai portfolio project di GitHub.

### Status

`app_2_v14.py` merupakan baseline dark-only yang stabil. Versi ini kemudian dipoles lebih lanjut pada `app_2_v15.py` untuk meningkatkan navigasi dan keterbacaan informasi.

---


## 4.15 `app_2_v15.py` — Final UI Polish dan Peningkatan Keterbacaan

### Latar belakang

Setelah design system dark-only pada `v14` stabil, evaluasi akhir menemukan empat masalah pengalaman pengguna yang tidak berkaitan dengan formula analitik:

1. menu **Ringkasan**, **Customer & Peta**, **Produk & Seller**, serta **Layanan & Pembayaran** terlihat menyatu;
2. kode state Brasil masih sulit dipahami oleh pengguna yang tidak familier dengan singkatan wilayah;
3. chart produk terlaris menampilkan potongan hash `product_id` tanpa konteks yang cukup;
4. label dan persentase pada diagram retensi customer saling bertabrakan.

`v15` tidak melakukan redesign total. Versi ini mempertahankan fondasi dark-only `v14`, kemudian menambahkan lapisan penyempurnaan visual dan semantic labeling.

### Perubahan utama

#### 1. Navigasi tab diubah menjadi tombol/pill terpisah

Komponen tetap menggunakan `st.tabs()`, tetapi elemen `role="tab"` diberi styling khusus:

- `gap` antar-menu;
- border pada setiap tab;
- background dan radius masing-masing tombol;
- state hover dengan perubahan background, border, dan translasi ringan;
- state aktif dengan gradient, border biru, dan warna teks putih;
- wrapping otomatis ketika ruang horizontal tidak mencukupi;
- tab highlight dan border bawaan Streamlit disembunyikan.

Pendekatan ini mempertahankan logika navigasi native Streamlit, tetapi membuat setiap pilihan fitur terlihat sebagai kontrol yang terpisah dan jelas.

#### 2. Kamus nama lengkap state Brasil

Ditambahkan konstanta `STATE_NAMES` yang memetakan kode state ke nama lengkap, misalnya:

```python
STATE_NAMES = {
    "SP": "São Paulo",
    "RJ": "Rio de Janeiro",
    "MG": "Minas Gerais",
    # ...
}
```

Fungsi berikut digunakan sebagai formatter terpusat:

```python
def format_state_name(code, include_code=True):
    ...
```

Format default menjadi:

```text
São Paulo (SP)
Rio de Janeiro (RJ)
Minas Gerais (MG)
```

Formatter diterapkan pada:

- filter state customer;
- filter state seller;
- insight otomatis;
- chart kontribusi state customer;
- tabel profil wilayah;
- chart kekuatan seller per state;
- tooltip visualisasi terkait wilayah.

Nilai kode asli tetap digunakan pada proses filter dan agregasi. Dengan demikian, perubahan ini hanya memperbaiki lapisan presentasi dan tidak mengubah data sumber.

#### 3. Panduan kode state pada sidebar

Sidebar memperoleh expander **“Panduan kode state Brasil”** yang memuat daftar kode dan nama seluruh state. Daftar ditampilkan dalam layout ringkas yang dapat di-scroll.

Manfaatnya:

- pengguna tidak perlu mencari arti kode di luar dashboard;
- kode tetap dapat digunakan sebagai referensi teknis;
- nama lengkap menjadi konteks utama untuk pembacaan bisnis.

#### 4. Label produk terlaris dibuat lebih informatif

Dataset publik Olist tidak menyediakan kolom nama produk. Karena itu, `v15` tidak mengarang nama produk dan tidak mengganti ID dengan label yang tidak didukung data.

Sebagai solusi, label chart dibentuk dari:

```text
<Kategori Produk> · <6 karakter awal ID>
```

Contoh:

```text
Health Beauty · BB50F2
```

Fungsi `shorten_label()` digunakan untuk membatasi panjang kategori agar chart tetap rapi. Tooltip tetap menyediakan:

- `product_id` lengkap;
- kategori;
- GMV;
- jumlah unit;
- rating rata-rata.

Perubahan ini memberikan konteks bisnis tanpa menghilangkan traceability terhadap ID asli.

#### 5. Diagram retensi customer diperbaiki

Diagram retensi sebelumnya menampilkan label dan persentase langsung pada irisan donut, sehingga teks berpotensi bertabrakan. Pada `v15`:

- teks pada irisan dikurangi agar chart tidak padat;
- label segmen dan persentase dipindahkan ke legend;
- legend ditempatkan secara horizontal di bawah chart;
- margin bawah diperbesar;
- jumlah total customer unik ditempatkan di tengah donut;
- detail jumlah dan persentase tetap tersedia melalui hover tooltip.

Hasilnya, perbandingan **One-time customer** dan **Repeat customer** menjadi lebih bersih dan mudah dibaca.

#### 6. Penyempurnaan visualisasi wilayah dan seller

Nama lengkap state juga digunakan pada sumbu chart. Beberapa penyesuaian layout diterapkan agar label panjang tidak terpotong:

- chart state customer menggunakan orientasi horizontal;
- margin kiri diperbesar;
- `automargin=True` digunakan pada sumbu;
- label state seller dimiringkan secara terkontrol;
- tooltip tetap menampilkan kode state asli.

### Dampak akhir

- navigasi utama lebih jelas sebagai sekumpulan pilihan fitur;
- dashboard lebih mudah digunakan oleh pengguna yang tidak memahami kode administratif Brasil;
- chart produk tidak lagi hanya berisi karakter acak tanpa konteks;
- retensi customer tidak memiliki teks yang saling menimpa;
- seluruh perubahan tetap konsisten dengan design system dark-only;
- formula KPI, filter, data mart, peta, dan ekspor tidak berubah.

### Status

`app_2_v15.py` merupakan versi final yang direkomendasikan sebagai source utama deployment dan portfolio GitHub.

---

# 5. Evolusi Teknis Berdasarkan Area

## 5.1 Penemuan dan pemuatan data

| Tahap | Implementasi |
|---|---|
| Versi awal–`v1` | Mencari file di folder aplikasi, `data/`, `project_sources/`, dan current working directory |
| `v2` dan seterusnya | Menambahkan pencarian di satu dan dua tingkat direktori induk |
| Seluruh versi | Mendukung unggahan CSV melalui sidebar jika file lokal tidak lengkap |
| Seluruh versi | Menggunakan fingerprint file untuk cache |
| Seluruh versi | Memvalidasi sembilan dataset dan kolom wajib sebelum membangun data mart |

## 5.2 Visualisasi Plotly

| Tahap | Karakteristik |
|---|---|
| Versi awal | Background transparan; beberapa teks menyatu dengan halaman |
| `v1–v13` | Background putih dan teks gelap dengan kontras tinggi |
| `v14–v15` | Plotly dark-native: background, font, grid, tooltip, legend, colorbar, dan annotation diselaraskan |

## 5.3 Arsitektur KPI

| Versi | Arsitektur KPI |
|---|---|
| `v1–v3` | HTML card sederhana tanpa sparkline |
| `v4–v7` | HTML card dengan SVG sparkline inline |
| `v8` | HTML title/value + Plotly sparkline + native caption |
| `v9` | HTML card terpadu + SVG `spark-mini` |
| `v10` | Hybrid HTML title + native `st.metric()` |
| `v11` | Hybrid executive card dengan HTML value dan badge delta |
| `v12` | Native Streamlit untuk header, value, dan note |
| `v13–v15` | API native KPI final dengan optional delta/note/spark dan key unik |

## 5.4 Tema

| Versi | Tema |
|---|---|
| `v1–v3` | Light mode |
| `v4–v12` | Light mode utama dengan dark override parsial |
| `v13` | Dual mode yang lebih matang, tetapi masih tidak seimbang |
| `v14–v15` | Dark mode only dan konsisten |

## 5.5 Responsivitas

- `v4` memperkenalkan media query dasar.
- `v5–v7` menambah penyesuaian ukuran KPI dan hero.
- `v10–v13` mengikuti layout native Streamlit untuk stabilitas.
- `v14` mengunci wrapping KPI untuk desktop, tablet, dan mobile.
- `v15` menambahkan wrapping pada navigasi pill serta automargin untuk label state dan produk yang lebih panjang.

## 5.6 Keamanan rendering

Perjalanan sanitasi KPI:

1. `html.escape()` pada title, value, dan note;
2. eksperimen note HTML pada `v5`;
3. `clean_metric_text()` pada `v6`;
4. safe variable eksplisit pada `v7`;
5. pemisahan native caption pada `v8`;
6. migrasi value/delta ke `st.metric()` pada `v10`;
7. KPI native final pada `v13–v15`.

Pelajaran utamanya adalah bahwa HTML custom sebaiknya digunakan hanya untuk dekorasi yang benar-benar diperlukan. Data dinamis dan metric utama lebih aman dirender dengan komponen native Streamlit.


## 5.7 Semantic labeling dan navigasi

| Tahap | Karakteristik |
|---|---|
| `v1–v14` | Tab masih menggunakan tampilan bawaan/menyatu; state banyak ditampilkan sebagai kode; produk memakai ID singkat |
| `v15` | Tab bergaya pill, state menggunakan nama lengkap + kode, sidebar memiliki panduan state, dan produk memakai kategori + ID singkat |

`v15` menunjukkan bahwa kualitas dashboard bukan hanya ditentukan oleh akurasi agregasi, tetapi juga oleh kemampuan label menjelaskan makna data kepada pengguna akhir.

---

# 6. Matriks Perbandingan Versi

Keterangan:

- ✅ tersedia atau sudah stabil;
- ◐ tersedia tetapi parsial/eksperimental;
- — belum tersedia.

| Versi | Plotly kontras | Parent data path | Sparkline | Sanitasi KPI | Native KPI | Responsive | Dual theme | Dark-only | UX final |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `v1` | ✅ | — | — | Dasar | — | — | — | — | — |
| `v2` | ✅ | ✅ | — | Dasar | — | — | — | — | — |
| `v3` | ✅ | ✅ | — | Dasar | — | — | — | — | — |
| `v4` | ✅ | ✅ | SVG | ◐ | — | ✅ | ◐ | — | — |
| `v5` | ✅ | ✅ | SVG | ◐ | — | ✅ | ◐ | — | — |
| `v6` | ✅ | ✅ | SVG | ✅ | — | ✅ | ◐ | — | — |
| `v7` | ✅ | ✅ | SVG | ✅ | — | ✅ | ◐ | — | — |
| `v8` | ✅ | ✅ | Plotly | ✅ | ◐ | ✅ | ◐ | — | — |
| `v9` | ✅ | ✅ | SVG | ✅ | — | ✅ | ◐ | — | — |
| `v10` | ✅ | ✅ | Plotly | ✅ | ✅ | ✅ | ◐ | — | — |
| `v11` | ✅ | ✅ | Plotly | ◐ | ◐ | ✅ | ◐ | — | — |
| `v12` | ✅ | ✅ | Plotly | ✅ | ✅ | ✅ | ◐ | — | — |
| `v13` | ✅ | ✅ | Plotly | ✅ | ✅ | ✅ | ✅ | — | — |
| `v14` | ✅ | ✅ | Plotly | ✅ | ✅ | ✅ | — | ✅ | — |
| `v15` | ✅ | ✅ | Plotly | ✅ | ✅ | ✅ | — | ✅ | ✅ |

---

# 7. Komponen Utama pada Versi Final

## 7.1 Data layer

Versi final `v15` mempertahankan arsitektur data berikut:

```text
CSV sources
   ↓
Source discovery / upload fallback
   ↓
File and column validation
   ↓
Cached CSV loading
   ↓
Data cleaning and type conversion
   ↓
Data mart construction
   ↓
Interactive filters
   ↓
KPI, charts, map, table, and export
```

## 7.2 Data mart

Tabel fakta utama dibangun dari:

```text
order_items
   + products
   + sellers
   + orders
   + customers
   + reviews
   + geolocation summary
```

Kolom turunan utama mencakup:

- `gmv`;
- kategori produk berbahasa Inggris;
- koordinat customer;
- `delivery_days`;
- `delivery_delay_days`;
- `is_on_time`;
- informasi customer dan seller;
- review score.

## 7.3 Filter layer

Filter diterapkan pada tabel fakta level item, kemudian data order-level dibuat melalui deduplikasi `order_id`. Pendekatan ini memungkinkan:

- GMV dihitung pada level item;
- jumlah pesanan dihitung sebagai `nunique(order_id)`;
- customer dihitung sebagai `nunique(customer_unique_id)`;
- rating dan pengiriman dianalisis pada level order.

## 7.4 Presentation layer

Versi final menggunakan:

- **native Streamlit** untuk metric, input, caption, table, dan download;
- **Plotly** untuk chart utama dan sparkline;
- **Folium** untuk peta customer;
- **CSS custom** untuk design system dark mode, responsive behavior, dan navigasi pill;
- **semantic formatter** untuk nama state dan label produk;
- **HTML terbatas** untuk hero, panduan state, dan elemen dekoratif yang tidak menerima input bebas.

---

# 8. Perubahan yang Tidak Mengubah Logika Analitik

Sebagian besar revisi `v4–v15` berfokus pada presentasi. Hal-hal berikut pada dasarnya tetap dipertahankan:

- definisi GMV sebagai `price + freight_value`;
- jumlah pesanan berdasarkan `order_id` unik;
- customer unik berdasarkan `customer_unique_id`;
- average order value sebagai GMV dibagi pesanan;
- agregasi review pada level pesanan;
- filter status default `delivered` jika tersedia;
- pembanding periode sebelumnya dengan panjang periode yang sama;
- analisis geospasial berdasarkan koordinat ZIP prefix;
- ekspor hasil filter pada level pesanan;
- struktur empat tab analisis;
- segmentasi customer menjadi one-time dan repeat customer.

Dengan kata lain, iterasi panjang tidak mengubah tujuan bisnis dashboard. Perubahan terutama dilakukan untuk meningkatkan:

- keterbacaan;
- stabilitas rendering;
- portabilitas struktur folder;
- konsistensi tema;
- pengalaman pengguna pada desktop dan mobile;
- interpretabilitas label untuk pengguna nonteknis.

---

# 9. Pelajaran Pengembangan

## 9.1 Gunakan komponen native untuk data dinamis

`st.metric()`, `st.caption()`, dan `st.container()` lebih stabil untuk nilai KPI daripada membangun seluruh card melalui nested HTML.

## 9.2 Pisahkan data, presentation helper, dan layout

Dashboard lebih mudah dipelihara ketika fungsi dibagi menjadi:

- loader dan validator;
- data model builder;
- formatter;
- filter;
- chart styling;
- KPI renderer;
- map builder;
- main layout.

## 9.3 Tema harus diterapkan secara menyeluruh

Mengubah background halaman saja tidak cukup. Tema harus mencakup:

- komponen Streamlit;
- input dan popover;
- table;
- Plotly;
- tooltip;
- legend;
- annotation;
- colorbar;
- peta bila diperlukan.

## 9.4 Satu tema berkualitas lebih baik daripada dua tema setengah selesai

Keputusan dark-only pada `v14` menyederhanakan:

- CSS;
- testing;
- maintenance;
- konsistensi screenshot portfolio;
- perilaku deployment.

## 9.5 Struktur repository harus diperhitungkan sejak awal

Perbaikan pada `v2` menunjukkan bahwa aplikasi sebaiknya tidak mengasumsikan dataset selalu berada di folder yang sama. Pencarian relatif terhadap `__file__`, parent folder, dan working directory membuat aplikasi lebih portable.

## 9.6 Label teknis perlu diberi konteks bisnis

Kode state dan `product_id` valid secara teknis, tetapi belum tentu bermakna bagi pengguna. `v15` mempertahankan nilai asli untuk filtering dan traceability, kemudian menambahkan nama lengkap atau kategori pada presentation layer.

## 9.7 Kurangi kepadatan chart pada sumber masalahnya

Untuk diagram retensi, memperkecil font saja tidak cukup. Solusi yang lebih tepat adalah memindahkan informasi sekunder ke legend dan tooltip, lalu menggunakan area tengah donut untuk satu angka utama.

---

# 10. Kesimpulan

Pengembangan `app_2.py` dari `v1` hingga `v15` dapat dibagi menjadi lima fase utama:

1. **stabilisasi visual dan deployment (`v1–v3`)** — memperjelas grafik dan membuat pencarian dataset lebih fleksibel;
2. **redesign dan eksperimen KPI (`v4–v9`)** — memperkenalkan sparkline, dark mode, responsivitas, serta berbagai pendekatan HTML/SVG;
3. **migrasi ke komponen native (`v10–v13`)** — mengganti KPI custom yang rapuh dengan `st.metric()`, `st.caption()`, dan Plotly;
4. **konsolidasi dark-only (`v14`)** — menyatukan seluruh dashboard dalam design system gelap yang konsisten;
5. **final UI polish (`v15`)** — memperjelas navigasi, menerjemahkan kode state menjadi nama yang mudah dipahami, memberi konteks pada produk, dan menghilangkan tabrakan teks pada retensi customer.

Versi final mempertahankan kemampuan analitik dashboard awal, tetapi meningkatkan portabilitas, stabilitas rendering, keterbacaan, responsivitas, interpretabilitas, dan kualitas visual secara signifikan. Untuk penggunaan produksi dan portfolio GitHub, `app_2_v15.py` merupakan baseline yang direkomendasikan.

---

**Dokumen terakhir diperbarui:** 19 Juli 2026  
**Status:** Final documentation updated through `app_2_v15.py`
