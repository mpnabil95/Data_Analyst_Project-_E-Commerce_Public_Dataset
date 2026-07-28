# E-Commerce Public Data Analysis Dashboard 🛒

Ini adalah proyek akhir (submission) untuk kelas Belajar Analisis Data dengan Python dari Dicoding. Dashboard ini dibuat menggunakan Streamlit untuk memvisualisasikan data interaktif dari E-Commerce Public Dataset, mencakup analisis performa penjualan, ulasan pelanggan, pemetaan geospasial, dan RFM Analysis.

## Setup Environment

Proyek ini menggunakan Python 3.11. Buat virtual environment dari root
repository agar dependensi proyek tidak bercampur dengan instalasi Python
global.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Gunakan file dependency sesuai kebutuhan:

- `requirements.txt` untuk menjalankan dashboard.
- `requirements-notebook.txt` untuk dashboard dan notebook analisis.
- `requirements-dev.txt` untuk seluruh dependency beserta alat pengujian.

Contoh instalasi environment notebook:

```bash
python -m pip install -r requirements-notebook.txt
```

## Run Streamlit App

```bash
python -m streamlit run app.py
```
