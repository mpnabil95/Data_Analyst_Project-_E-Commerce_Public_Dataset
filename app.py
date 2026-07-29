"""Dashboard Streamlit dark-only final untuk Brazilian E-Commerce Public Dataset.

Jalankan aplikasi dari folder yang berisi file ini dengan perintah:

    streamlit run app.py

Dependensi utama:

    pip install streamlit pandas numpy plotly folium streamlit-folium

Aplikasi otomatis mencari sembilan CSV Olist di folder yang sama, folder
``data/``, atau ``project_sources/``. Nama dengan prefiks seperti
``01-customers_dataset.csv`` juga dikenali. Jika ada file yang tidak ditemukan,
file tersebut dapat diunggah melalui panel sumber data di sidebar.
"""

from __future__ import annotations

import hashlib
import html
import io
import re
from pathlib import Path
from typing import Any

try:
    import folium
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import streamlit as st
    from folium.plugins import Fullscreen, HeatMap, MiniMap
    from streamlit_folium import st_folium
except ImportError as exc:  # Pesan lebih ramah ketika dependensi belum tersedia.
    raise RuntimeError(
        "Dependensi dashboard belum lengkap. Jalankan: "
        "pip install streamlit pandas numpy plotly folium streamlit-folium"
    ) from exc


# -----------------------------------------------------------------------------
# Konfigurasi halaman dan tema visual
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Olist Commerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Versi rilis menggunakan satu design system yang konsisten: dark mode.
DARK_MODE = True

COLORS = {
    "navy": "#07111F",
    "surface": "#0D1828",
    "surface_2": "#111F32",
    "blue": "#2F6BFF",
    "cyan": "#10BFD6",
    "violet": "#8B5CF6",
    "emerald": "#18B88A",
    "amber": "#F59E0B",
    "rose": "#FF3F68",
    "text": "#F8FAFC",
    "muted": "#9AA9BC",
    "grid": "rgba(148,163,184,.18)",
    "border": "rgba(100,116,139,.38)",
}


STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
    "Unknown": "Tidak diketahui",
}


def format_state_name(code: Any, include_code: bool = True) -> str:
    """Mengubah kode state menjadi nama lengkap yang mudah dipahami."""
    normalized = str(code)
    full_name = STATE_NAMES.get(normalized, normalized)
    if include_code and normalized not in {"Unknown", "nan", "None"}:
        return f"{full_name} ({normalized})"
    return full_name


def shorten_label(value: Any, max_length: int = 26) -> str:
    """Memendekkan label panjang tanpa menghilangkan konteks utamanya."""
    label = str(value)
    return label if len(label) <= max_length else f"{label[: max_length - 1]}…"

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            color-scheme: dark;
            --app-bg: #07111F;
            --app-bg-soft: #091525;
            --surface: #0D1828;
            --surface-raised: #111F32;
            --surface-input: #08111E;
            --border: rgba(100,116,139,.38);
            --border-soft: rgba(100,116,139,.24);
            --text: #F8FAFC;
            --text-secondary: #CBD5E1;
            --muted: #94A3B8;
            --primary: #2F6BFF;
            --cyan: #10BFD6;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        html, body,
        [data-testid="stAppViewContainer"],
        .stApp {
            background:
                radial-gradient(circle at 84% -12%, rgba(47,107,255,.13), transparent 30%),
                radial-gradient(circle at 8% 22%, rgba(16,191,214,.06), transparent 26%),
                linear-gradient(180deg, var(--app-bg) 0%, #07101D 100%) !important;
            color: var(--text) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(5,10,18,.96) !important;
            border-bottom: 1px solid rgba(100,116,139,.14);
        }

        [data-testid="stDecoration"] {
            background: linear-gradient(90deg, #2F6BFF, #10BFD6) !important;
        }

        .block-container {
            padding-top: .7rem;
            padding-bottom: 2.2rem;
            max-width: 1540px;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #07142A 0%, #0A1A36 55%, #0D2347 100%) !important;
            border-right: 1px solid rgba(148,163,184,.18);
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(148,163,184,.20);
        }

        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div,
        [data-testid="stSidebar"] [data-testid="stDateInput"] > div > div,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
        [data-testid="stSidebar"] button[kind="secondary"] {
            background: #08111E !important;
            border-color: rgba(100,116,139,.34) !important;
            color: #F8FAFC !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {
            color: #E2E8F0 !important;
            -webkit-text-fill-color: #E2E8F0 !important;
            caret-color: #E2E8F0 !important;
        }

        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {
            color: #64748B !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] [data-baseweb="tag"] {
            background: rgba(255,63,104,.90) !important;
            color: white !important;
        }

        [data-testid="stSidebar"] .state-guide {
            display: grid;
            grid-template-columns: 1fr;
            gap: .18rem;
            max-height: 330px;
            overflow-y: auto;
            padding-right: .25rem;
        }

        [data-testid="stSidebar"] .state-guide-row {
            display: grid;
            grid-template-columns: 2.15rem 1fr;
            gap: .45rem;
            align-items: baseline;
            padding: .24rem .1rem;
            border-bottom: 1px solid rgba(148,163,184,.10);
            font-size: .76rem;
        }

        [data-testid="stSidebar"] .state-code {
            color: #7DD3FC !important;
            font-weight: 800;
        }

        [data-testid="stSidebar"] .state-name {
            color: #CBD5E1 !important;
        }

        [data-testid="stSidebar"] [data-baseweb="popover"] *,
        [data-baseweb="popover"] * {
            color: #E5E7EB;
        }

        div[role="listbox"] {
            background: #0B1728 !important;
            border: 1px solid rgba(100,116,139,.38) !important;
        }

        div[role="option"] {
            background: #0B1728 !important;
            color: #E5E7EB !important;
        }

        div[role="option"]:hover,
        div[aria-selected="true"] {
            background: #142743 !important;
        }

        /* Hero */
        .hero {
            padding: 1.35rem 1.65rem;
            border-radius: 22px;
            background:
                linear-gradient(120deg, #0C2148 0%, #173F82 58%, #2F6BFF 100%);
            color: #FFFFFF;
            border: 1px solid rgba(96,165,250,.22);
            box-shadow: 0 22px 55px rgba(0,0,0,.27);
            margin-bottom: 1.05rem;
            position: relative;
            overflow: hidden;
        }

        .hero:after {
            content: '';
            position: absolute;
            width: 240px;
            height: 240px;
            right: -68px;
            top: -114px;
            border: 40px solid rgba(255,255,255,.075);
            border-radius: 50%;
        }

        .hero-kicker {
            color: #C8D8F3;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .16em;
        }

        .hero-title {
            color: #FFFFFF;
            font-size: clamp(1.7rem, 3vw, 2.45rem);
            font-weight: 800;
            line-height: 1.12;
            margin: .35rem 0;
        }

        .hero-subtitle {
            color: #E2ECFF;
            font-size: .92rem;
            max-width: 930px;
        }

        /* KPI cards berbasis native Streamlit */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"]) {
            background:
                linear-gradient(180deg, rgba(15,29,48,.98), rgba(10,20,35,.98)) !important;
            border: 1px solid rgba(100,116,139,.42) !important;
            border-radius: 16px !important;
            box-shadow: 0 12px 30px rgba(0,0,0,.20) !important;
            min-height: 210px;
            padding: .9rem .95rem .78rem;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"])
        div[data-testid="stMetric"] {
            padding: 0;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"])
        div[data-testid="stMetricLabel"] {
            color: #B5C2D3 !important;
            font-size: .72rem !important;
            font-weight: 800 !important;
            letter-spacing: .055em !important;
            line-height: 1.22 !important;
            text-transform: uppercase;
            min-height: 1.8rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"])
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: clamp(1.62rem, 2.15vw, 2.1rem) !important;
            font-weight: 800 !important;
            line-height: 1.08 !important;
            margin-top: .16rem;
            white-space: nowrap;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"])
        div[data-testid="stMetricDelta"] {
            font-size: .74rem !important;
            font-weight: 700 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"])
        div[data-testid="stPlotlyChart"] {
            margin-top: -.15rem;
            margin-bottom: -.35rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"])
        div[data-testid="stCaptionContainer"] p {
            color: #9AA9BC !important;
            font-size: .74rem !important;
            line-height: 1.3 !important;
            margin: 0 !important;
        }

        /* Section typography */
        .section-title {
            color: #F8FAFC;
            font-size: 1.08rem;
            font-weight: 800;
            margin: .35rem 0 .1rem;
        }

        .section-note {
            color: #9AA9BC;
            font-size: .80rem;
            margin-bottom: .68rem;
        }

        .insight-box {
            background:
                linear-gradient(100deg, rgba(47,107,255,.12), rgba(16,191,214,.07));
            border: 1px solid rgba(47,107,255,.26);
            border-left: 4px solid #2F6BFF;
            border-radius: 14px;
            padding: .88rem 1.02rem;
            color: #D5DFEC;
            font-size: .84rem;
            margin: .45rem 0 .9rem;
        }

        /* Navigasi bersyarat: hanya bagian aktif yang dihitung pada setiap rerun. */
        .st-key-dashboard_section {
            padding: .28rem 0 .72rem;
            border-bottom: 1px solid rgba(100,116,139,.28);
        }

        .st-key-dashboard_section button {
            min-height: 2.55rem;
            border-color: rgba(100,116,139,.34) !important;
            font-weight: 700 !important;
        }

        /* Inputs di area utama */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-testid="stDateInput"] > div > div {
            background: var(--surface-input) !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
        }

        input, textarea {
            color: #E5E7EB !important;
            -webkit-text-fill-color: #E5E7EB !important;
        }

        /* Expanders, frames, table, map */
        [data-testid="stExpander"] {
            background: rgba(13,24,40,.52);
            border: 1px solid rgba(100,116,139,.30);
            border-radius: 12px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(100,116,139,.34);
            border-radius: 14px;
            overflow: hidden;
        }

        iframe {
            border-radius: 15px;
            border: 1px solid rgba(100,116,139,.30);
        }

        /* Buttons */
        .stDownloadButton button,
        .stButton button {
            background: #10213A !important;
            color: #EAF1FF !important;
            border: 1px solid rgba(96,165,250,.38) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
        }

        .stDownloadButton button:hover,
        .stButton button:hover {
            background: #17345C !important;
            border-color: #4F8CFF !important;
        }

        /* Alerts and captions */
        [data-testid="stCaptionContainer"] p {
            color: #94A3B8;
        }

        [data-testid="stAlert"] {
            background: rgba(17,31,50,.86);
            color: #E2E8F0;
            border-color: rgba(100,116,139,.34);
        }

        hr {
            border-color: rgba(100,116,139,.24) !important;
        }

        footer {
            visibility: hidden;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: .72rem;
                padding-right: .72rem;
            }

            .hero {
                padding: 1.1rem 1.15rem;
            }

            .hero-title {
                font-size: 1.55rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stMetric"]) {
                min-height: 188px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Penemuan dan pembacaan sumber data
# -----------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent

REQUIRED_FILES = {
    "customers": "customers_dataset.csv",
    "sellers": "sellers_dataset.csv",
    "payments": "order_payments_dataset.csv",
    "translation": "product_category_name_translation.csv",
    "products": "products_dataset.csv",
    "geolocation": "geolocation_dataset.csv",
    "reviews": "order_reviews_dataset.csv",
    "items": "order_items_dataset.csv",
    "orders": "orders_dataset.csv",
}

# Ambang minimum mengikuti notebook analisis. Tujuannya menangkap CSV yang
# terpotong atau masih berupa pointer Git LFS, bukan membatasi baris analisis.
EXPECTED_MIN_ROWS = {
    "customers": 99_000,
    "sellers": 3_000,
    "payments": 103_000,
    "translation": 70,
    "products": 32_000,
    "geolocation": 1_000_000,
    "reviews": 99_000,
    "items": 112_000,
    "orders": 99_000,
}

# Bounding box konservatif Brasil, selaras dengan pemeriksaan spasial notebook.
BRAZIL_LATITUDE_BOUNDS = (-34.0, 6.0)
BRAZIL_LONGITUDE_BOUNDS = (-74.0, -34.0)

# Tipe data kompak untuk kolom yang aman dipersempit. Seluruh kolom tetap
# dibaca agar statistik kualitas data tidak berubah.
CSV_DTYPES = {
    "customers": {
        "customer_zip_code_prefix": "int32",
        "customer_city": "category",
        "customer_state": "category",
    },
    "sellers": {
        "seller_zip_code_prefix": "int32",
        "seller_city": "category",
        "seller_state": "category",
    },
    "payments": {
        "payment_sequential": "int8",
        "payment_type": "category",
        "payment_installments": "int16",
    },
    "geolocation": {
        "geolocation_zip_code_prefix": "int32",
        "geolocation_city": "category",
        "geolocation_state": "category",
    },
    "reviews": {"review_score": "int8"},
    "items": {"order_item_id": "int16"},
    "orders": {"order_status": "category"},
}

CSV_PARSE_DATES = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
}


def normalize_filename(name: str) -> str:
    """Menghapus prefiks angka agar file ``01-...`` tetap dikenali."""
    return re.sub(r"^\d+[-_]", "", Path(name).name.lower())


def discover_local_sources() -> dict[str, Path]:
    """Mencari setiap CSV pada beberapa lokasi yang lazim digunakan."""
    # Mencari sumber data secara fleksibel.
    # Mendukung kondisi ketika app berada di subfolder baru (misalnya v2-rewrite)
    # sedangkan folder data/ berada satu tingkat di atasnya.
    parent_dirs = [
        APP_DIR.parent,
        APP_DIR.parent.parent,
    ]

    candidate_dirs = [
        APP_DIR,
        APP_DIR / "data",
        APP_DIR / "project_sources",
        *[parent / "data" for parent in parent_dirs],
        *[parent / "project_sources" for parent in parent_dirs],
        Path.cwd(),
        Path.cwd() / "data",
        Path.cwd() / "project_sources",
    ]
    found: dict[str, Path] = {}
    seen_dirs: set[Path] = set()
    for directory in candidate_dirs:
        resolved = directory.resolve()
        if resolved in seen_dirs or not directory.exists():
            continue
        seen_dirs.add(resolved)
        available = {
            normalize_filename(path.name): path
            for path in directory.glob("*.csv")
            if path.is_file()
        }
        for key, canonical_name in REQUIRED_FILES.items():
            if key not in found and canonical_name in available:
                found[key] = available[canonical_name]
    return found


@st.cache_resource(show_spinner=False, max_entries=32)
def read_csv_path(dataset_key: str, path: str, modified_ns: int) -> pd.DataFrame:
    """Membaca CSV lokal sekali sebagai resource immutable."""
    del modified_ns
    return pd.read_csv(
        path,
        low_memory=False,
        dtype=CSV_DTYPES.get(dataset_key),
        parse_dates=CSV_PARSE_DATES.get(dataset_key),
    )


@st.cache_resource(show_spinner=False, max_entries=18)
def read_csv_bytes(dataset_key: str, file_name: str, payload: bytes) -> pd.DataFrame:
    """Membaca CSV unggahan sekali tanpa menyimpan berkas sementara."""
    del file_name
    return pd.read_csv(
        io.BytesIO(payload),
        low_memory=False,
        dtype=CSV_DTYPES.get(dataset_key),
        parse_dates=CSV_PARSE_DATES.get(dataset_key),
    )


def load_sources(
    local_sources: dict[str, Path], uploaded_files: list[Any]
) -> tuple[dict[str, pd.DataFrame], tuple[str, ...], list[str]]:
    """Menggabungkan sumber lokal dan unggahan menjadi kumpulan DataFrame."""
    uploaded_lookup = {
        normalize_filename(upload.name): upload for upload in (uploaded_files or [])
    }
    datasets: dict[str, pd.DataFrame] = {}
    fingerprints: list[str] = []
    missing: list[str] = []

    for key, canonical_name in REQUIRED_FILES.items():
        if key in local_sources:
            path = local_sources[key]
            stat = path.stat()
            datasets[key] = read_csv_path(key, str(path), stat.st_mtime_ns)
            fingerprints.append(f"{key}:{path}:{stat.st_size}:{stat.st_mtime_ns}")
        elif canonical_name in uploaded_lookup:
            upload = uploaded_lookup[canonical_name]
            payload = upload.getvalue()
            digest = hashlib.sha256(payload).hexdigest()
            datasets[key] = read_csv_bytes(key, upload.name, payload)
            fingerprints.append(f"{key}:{upload.name}:{digest}")
        else:
            missing.append(canonical_name)
    return datasets, tuple(fingerprints), missing


def validate_columns(datasets: dict[str, pd.DataFrame]) -> list[str]:
    """Memastikan kolom kunci tersedia sebelum proses penggabungan data."""
    required_columns = {
        "customers": {"customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"},
        "sellers": {"seller_id", "seller_state"},
        "payments": {"order_id", "payment_type", "payment_value"},
        "translation": {"product_category_name", "product_category_name_english"},
        "products": {"product_id", "product_category_name"},
        "geolocation": {"geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"},
        "reviews": {"order_id", "review_score"},
        "items": {"order_id", "product_id", "seller_id", "price", "freight_value"},
        "orders": {"order_id", "customer_id", "order_status", "order_purchase_timestamp"},
    }
    errors: list[str] = []
    for key, expected in required_columns.items():
        missing = expected.difference(datasets[key].columns)
        if missing:
            errors.append(f"{REQUIRED_FILES[key]}: {', '.join(sorted(missing))}")
    return errors


def validate_dataset_completeness(datasets: dict[str, pd.DataFrame]) -> list[str]:
    """Mendeteksi CSV yang terlalu kecil dan kemungkinan terpotong."""
    errors: list[str] = []
    for key, minimum_rows in EXPECTED_MIN_ROWS.items():
        actual_rows = len(datasets[key])
        if actual_rows < minimum_rows:
            errors.append(
                f"{REQUIRED_FILES[key]}: {actual_rows:,} baris "
                f"(minimum yang diharapkan {minimum_rows:,})"
            )
    return errors


# -----------------------------------------------------------------------------
# Pembuatan data mart
# -----------------------------------------------------------------------------
@st.cache_resource(
    show_spinner="Menyiapkan data mart dan koordinat peta …",
    max_entries=8,
)
def build_data_model(
    fingerprint: tuple[str, ...], _datasets: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    """Membangun resource analitik immutable untuk dashboard."""
    del fingerprint
    data = _datasets

    # Bersihkan duplikasi dan koordinat non-Brasil sebelum mengambil median.
    geo_columns = [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
    ]
    geo = data["geolocation"].dropna(
        subset=["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"]
    ).drop_duplicates()
    geo = geo[geo_columns].copy()
    geo["geolocation_lat"] = pd.to_numeric(geo["geolocation_lat"], errors="coerce")
    geo["geolocation_lng"] = pd.to_numeric(geo["geolocation_lng"], errors="coerce")
    geo = geo.dropna(subset=["geolocation_lat", "geolocation_lng"])
    valid_geo = (
        geo["geolocation_lat"].between(*BRAZIL_LATITUDE_BOUNDS)
        & geo["geolocation_lng"].between(*BRAZIL_LONGITUDE_BOUNDS)
    )
    geo = geo.loc[valid_geo].copy()
    geo_zip = (
        geo.groupby("geolocation_zip_code_prefix", as_index=False, observed=True)
        .agg(customer_lat=("geolocation_lat", "median"), customer_lng=("geolocation_lng", "median"))
    )

    customer_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]
    customers = data["customers"][customer_columns].merge(
        geo_zip,
        left_on="customer_zip_code_prefix",
        right_on="geolocation_zip_code_prefix",
        how="left",
    )
    customers = customers.drop(columns=["geolocation_zip_code_prefix"], errors="ignore")

    order_source_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    orders = data["orders"][order_source_columns].copy()
    date_columns = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for column in date_columns:
        if column in orders.columns:
            orders[column] = pd.to_datetime(orders[column], errors="coerce")

    orders = orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 86_400
    orders["delivery_delay_days"] = (
        orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86_400
    delivered_mask = orders["order_delivered_customer_date"].notna()
    orders["is_on_time"] = pd.Series(pd.NA, index=orders.index, dtype="boolean")
    orders.loc[delivered_mask, "is_on_time"] = (
        orders.loc[delivered_mask, "order_delivered_customer_date"]
        <= orders.loc[delivered_mask, "order_estimated_delivery_date"]
    )

    review_order = (
        data["reviews"].groupby("order_id", as_index=False, observed=True)
        .agg(review_score=("review_score", "mean"))
    )
    orders = orders.merge(review_order, on="order_id", how="left", validate="one_to_one")

    lifetime = (
        orders.loc[orders["order_status"].eq("delivered")]
        .groupby("customer_unique_id", observed=True)["order_id"]
        .nunique()
        .rename("customer_lifetime_delivered_orders")
    )
    orders = orders.merge(lifetime, on="customer_unique_id", how="left")
    orders["customer_lifetime_delivered_orders"] = (
        orders["customer_lifetime_delivered_orders"].fillna(0).astype("int16")
    )
    orders["customer_segment"] = np.select(
        [
            orders["customer_lifetime_delivered_orders"].gt(1),
            orders["customer_lifetime_delivered_orders"].eq(1),
        ],
        ["Repeat customer", "One-time customer"],
        default="Belum ada pesanan selesai",
    )

    product_source = data["products"][["product_id", "product_category_name"]]
    translation_source = data["translation"][
        ["product_category_name", "product_category_name_english"]
    ]
    products = product_source.merge(
        translation_source, on="product_category_name", how="left", validate="many_to_one"
    )
    products["category"] = products["product_category_name_english"].fillna(
        products["product_category_name"]
    )
    products["category"] = (
        products["category"].fillna("unknown").str.replace("_", " ", regex=False).str.title()
    )

    seller_columns = ["seller_id", "seller_state"]
    item_columns = ["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"]
    product_columns = ["product_id", "category"]
    order_fact_columns = [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "customer_unique_id",
        "customer_city",
        "customer_state",
        "customer_lat",
        "customer_lng",
        "delivery_days",
        "delivery_delay_days",
        "is_on_time",
        "review_score",
        "customer_segment",
    ]
    fact = (
        data["items"][item_columns]
        .merge(products[product_columns], on="product_id", how="left", validate="many_to_one")
        .merge(data["sellers"][seller_columns], on="seller_id", how="left", validate="many_to_one")
        .merge(orders[order_fact_columns], on="order_id", how="left", validate="many_to_one")
    )
    fact["category"] = (
        fact["category"].astype("string").fillna("Unknown").astype("category")
    )
    fact["seller_state"] = (
        fact["seller_state"].astype("string").fillna("Unknown").astype("category")
    )
    for column in [
        "product_id",
        "seller_id",
        "order_status",
        "customer_city",
        "customer_state",
        "customer_segment",
    ]:
        fact[column] = fact[column].astype("category")
    fact["price"] = pd.to_numeric(fact["price"], errors="coerce").fillna(0)
    fact["freight_value"] = pd.to_numeric(fact["freight_value"], errors="coerce").fillna(0)
    fact = fact.rename(columns={"price": "gmv"})
    fact["order_value"] = fact["gmv"] + fact["freight_value"]

    payments = data["payments"][["order_id", "payment_type", "payment_value"]].copy()
    payments["payment_value"] = pd.to_numeric(payments["payment_value"], errors="coerce").fillna(0)
    payments["payment_label"] = (
        payments["payment_type"]
        .astype("string")
        .fillna("unknown")
        .str.replace("_", " ", regex=False)
        .str.title()
        .astype("category")
    )
    payments = payments.drop(columns="payment_type")

    quality_rows = []
    for name, frame in data.items():
        used_rows = len(geo) if name == "geolocation" else len(frame)
        quality_rows.append(
            {
                "Dataset": REQUIRED_FILES[name],
                "Baris": len(frame),
                "Baris digunakan": used_rows,
                "Baris dikeluarkan": len(frame) - used_rows,
                "Kolom": len(frame.columns),
                "Sel kosong": int(frame.isna().sum().sum()),
                "Baris duplikat": int(frame.duplicated().sum()),
            }
        )
    quality = pd.DataFrame(quality_rows)

    return {
        "fact": fact,
        "payments": payments,
        "quality": quality,
    }


# -----------------------------------------------------------------------------
# Fungsi presentasi dan visualisasi
# -----------------------------------------------------------------------------
def format_currency(value: float) -> str:
    """Format ringkas Real Brasil dengan istilah Indonesia."""
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:,.2f} jt".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:,.1f} rb".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_integer(value: float | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def percent_delta(current: float, previous: float) -> str | None:
    """Menghasilkan delta ringkas untuk st.metric; None jika pembanding tidak valid."""
    if not np.isfinite(previous) or previous == 0:
        return None
    delta = (current - previous) / abs(previous) * 100
    return f"{delta:+.1f}% vs periode lalu"


def clean_metric_text(text: str) -> str:
    """Membersihkan input agar HTML tidak pernah tampil sebagai teks pada KPI."""
    text = re.sub(r"<[^>]+>", "", str(text))
    return html.escape(text)


def render_kpi_card(
    title: str,
    value: str,
    accent: str,
    *,
    delta: str | None = None,
    note: str | None = None,
    spark: list[float] | None = None,
    key: str,
) -> None:
    """
    KPI card final berbasis komponen native Streamlit.

    - Label, value, dan delta memakai st.metric.
    - Catatan memakai st.caption.
    - Sparkline memakai Plotly dan tidak disisipkan ke string HTML.
    """

    valid_spark = [
        float(item)
        for item in (spark or [])
        if item is not None and np.isfinite(item)
    ]

    with st.container(border=True):
        st.metric(
            label=title.upper(),
            value=str(value),
            delta=delta,
            delta_color="normal",
        )

        if len(valid_spark) >= 2:
            x_values = list(range(len(valid_spark)))
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=x_values,
                    y=valid_spark,
                    mode="lines",
                    line=dict(color=accent, width=2.6, shape="spline"),
                    fill="tozeroy",
                    fillcolor=f"rgba({int(accent[1:3], 16)},{int(accent[3:5], 16)},{int(accent[5:7], 16)},0.10)",
                    hoverinfo="skip",
                )
            )
            fig.update_layout(
                height=42,
                margin=dict(l=0, r=0, t=2, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(visible=False, fixedrange=True),
                yaxis=dict(visible=False, fixedrange=True),
            )
            st.plotly_chart(
                fig,
                width="stretch",
                config={"displayModeBar": False, "staticPlot": True},
                key=f"spark_{key}",
            )
        else:
            # Menjaga tinggi card konsisten ketika trend tidak cukup panjang.
            st.write("")

        if note:
            st.caption(note)


def section_heading(title: str, note: str = "") -> None:
    st.markdown(f'<div class="section-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="section-note">{html.escape(note)}</div>', unsafe_allow_html=True)


def style_figure(fig: go.Figure, height: int = 380) -> go.Figure:
    """Menerapkan satu design system Plotly khusus dark mode."""
    text_color = "#DCE6F3"
    title_color = "#F8FAFC"
    grid_color = "rgba(148,163,184,.17)"
    axis_color = "rgba(148,163,184,.30)"
    hover_bg = "#111F32"
    hover_text = "#F8FAFC"

    fig.update_layout(
        height=height,
        margin=dict(l=25, r=25, t=38, b=30),
        title=dict(text=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=text_color, size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.015,
            xanchor="right",
            x=1,
            font=dict(color=text_color),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=hover_bg,
            bordercolor="rgba(148,163,184,.30)",
            font_color=hover_text,
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color),
            bgcolor="rgba(0,0,0,0)",
            outlinecolor="rgba(148,163,184,.25)",
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=axis_color,
        tickfont=dict(color=text_color),
        title_font=dict(color=text_color),
        zeroline=False,
    )

    fig.update_yaxes(
        gridcolor=grid_color,
        linecolor=axis_color,
        zeroline=False,
        tickfont=dict(color=text_color),
        title_font=dict(color=text_color),
    )

    fig.update_annotations(font=dict(color=title_color))
    fig.update_traces(textfont=dict(color=text_color), selector=dict(type="pie"))
    return fig


def apply_filters(
    fact: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    customer_states: list[str],
    categories: list[str],
    statuses: list[str],
    seller_states: list[str],
) -> pd.DataFrame:
    """Menerapkan seluruh filter pada tabel fakta level item."""
    mask = fact["order_purchase_timestamp"].ge(start_date) & fact["order_purchase_timestamp"].lt(
        end_date + pd.Timedelta(days=1)
    )
    if customer_states:
        mask &= fact["customer_state"].isin(customer_states)
    if categories:
        mask &= fact["category"].isin(categories)
    if statuses:
        mask &= fact["order_status"].isin(statuses)
    if seller_states:
        mask &= fact["seller_state"].isin(seller_states)
    return fact.loc[mask]


def make_customer_map(points: pd.DataFrame, mode: str) -> folium.Map:
    """Membuat peta bubble atau heatmap yang dapat di-zoom dan digeser."""
    center = [points["customer_lat"].median(), points["customer_lng"].median()]
    customer_map = folium.Map(
        location=center,
        zoom_start=4,
        tiles="CartoDB positron",
        control_scale=True,
        prefer_canvas=True,
    )
    Fullscreen(position="topright").add_to(customer_map)
    MiniMap(toggle_display=True, tile_layer="CartoDB positron").add_to(customer_map)

    if mode == "Heatmap":
        heat_data = points[["customer_lat", "customer_lng", "customers"]].values.tolist()
        HeatMap(
            heat_data,
            radius=18,
            blur=14,
            min_opacity=0.28,
            gradient={0.2: "#67E8F9", 0.5: "#2563EB", 0.8: "#7C3AED", 1: "#F43F5E"},
        ).add_to(customer_map)
    else:
        maximum = max(float(points["customers"].max()), 1.0)
        for row in points.itertuples(index=False):
            radius = 4 + 18 * np.sqrt(float(row.customers) / maximum)
            tooltip = (
                f"<b>{html.escape(str(row.customer_city).title())}, "
                f"{html.escape(format_state_name(row.customer_state))}</b><br>"
                f"Customer: {format_integer(row.customers)}<br>"
                f"Pesanan: {format_integer(row.orders)}<br>"
                f"Product GMV: {format_currency(row.gmv)}"
            )
            folium.CircleMarker(
                location=[row.customer_lat, row.customer_lng],
                radius=radius,
                tooltip=folium.Tooltip(tooltip, sticky=True),
                color="#FFFFFF",
                weight=1.2,
                fill=True,
                fill_color=COLORS["blue"],
                fill_opacity=0.68,
            ).add_to(customer_map)

    bounds = points[["customer_lat", "customer_lng"]].agg(["min", "max"])
    customer_map.fit_bounds(
        [
            [bounds.loc["min", "customer_lat"], bounds.loc["min", "customer_lng"]],
            [bounds.loc["max", "customer_lat"], bounds.loc["max", "customer_lng"]],
        ],
        padding=(20, 20),
    )
    return customer_map


def create_order_export(filtered: pd.DataFrame) -> bytes:
    """Meringkas hasil filter menjadi satu baris per pesanan untuk diunduh."""
    if filtered.empty:
        return b""
    dimensions = [
        "order_id",
        "order_purchase_timestamp",
        "order_status",
        "customer_unique_id",
        "customer_city",
        "customer_state",
        "review_score",
        "delivery_days",
        "is_on_time",
    ]
    dimensions = [column for column in dimensions if column in filtered.columns]
    export = (
        filtered.groupby(dimensions, dropna=False, as_index=False, observed=True)
        .agg(
            item_count=("order_item_id", "count"),
            product_gmv=("gmv", "sum"),
            freight_value=("freight_value", "sum"),
            order_value=("order_value", "sum"),
            categories=("category", lambda values: " | ".join(sorted(set(values)))),
        )
        .sort_values("order_purchase_timestamp", ascending=False)
    )
    return export.to_csv(index=False).encode("utf-8-sig")


# -----------------------------------------------------------------------------
# Aplikasi utama
# -----------------------------------------------------------------------------
def main() -> None:
    local_sources = discover_local_sources()

    with st.sidebar:
        st.markdown("## OLIST / BI")
        st.caption("E-commerce performance cockpit")
        st.caption("● Dark workspace")
        with st.expander("Sumber data", expanded=len(local_sources) < len(REQUIRED_FILES)):
            st.caption(
                f"{len(local_sources)}/{len(REQUIRED_FILES)} dataset ditemukan otomatis. "
                "Unggah hanya file yang masih belum ditemukan."
            )
            uploaded_files = st.file_uploader(
                "Tambahkan CSV",
                type=["csv"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )

    datasets, fingerprint, missing = load_sources(local_sources, uploaded_files or [])
    if missing:
        st.error("Dashboard belum dapat dimuat karena sumber data belum lengkap.")
        st.write("File yang belum ditemukan:")
        for name in missing:
            st.write(f"- `{name}`")
        st.info(
            "Letakkan file di folder yang sama dengan app.py, folder data/, "
            "folder project_sources/, atau unggah melalui sidebar."
        )
        st.stop()

    column_errors = validate_columns(datasets)
    if column_errors:
        st.error("Terdapat kolom wajib yang tidak ditemukan:")
        for error in column_errors:
            st.write(f"- {error}")
        st.stop()

    completeness_errors = validate_dataset_completeness(datasets)
    if completeness_errors:
        st.error("Terdapat dataset yang tampaknya tidak lengkap atau terpotong:")
        for error in completeness_errors:
            st.write(f"- {error}")
        st.info(
            "Pastikan Git LFS sudah selesai (`git lfs pull`) atau unggah ulang "
            "CSV Olist yang lengkap sebelum menjalankan dashboard."
        )
        st.stop()

    model = build_data_model(fingerprint, datasets)
    fact = model["fact"]
    payments = model["payments"]

    valid_dates = fact["order_purchase_timestamp"].dropna()
    data_min = valid_dates.min().date()
    data_max = valid_dates.max().date()

    # Filter berada di sidebar agar ruang utama tetap fokus pada insight.
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Filter analisis")
        selected_dates = st.date_input(
            "Periode transaksi",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max,
        )
        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
        else:
            start_date = end_date = selected_dates

        state_options = sorted(fact["customer_state"].dropna().astype(str).unique())
        category_options = sorted(fact["category"].dropna().astype(str).unique())
        status_options = sorted(fact["order_status"].dropna().astype(str).unique())
        seller_state_options = sorted(fact["seller_state"].dropna().astype(str).unique())

        customer_states = st.multiselect(
            "State customer",
            state_options,
            placeholder="Semua state",
            format_func=lambda code: format_state_name(code),
        )
        categories = st.multiselect(
            "Kategori produk", category_options, placeholder="Semua kategori"
        )
        default_status = ["delivered"] if "delivered" in status_options else []
        statuses = st.multiselect(
            "Status pesanan", status_options, default=default_status, placeholder="Semua status"
        )
        seller_states = st.multiselect(
            "State seller",
            seller_state_options,
            placeholder="Semua state seller",
            format_func=lambda code: format_state_name(code),
        )

        with st.expander("Panduan kode state Brasil", expanded=False):
            st.caption("Filter dan visual menggunakan nama lengkap; kode tetap ditampilkan dalam kurung.")
            st.markdown(
                """<div class="state-guide"><div class="state-guide-row"><span class="state-code">AC</span><span class="state-name">Acre</span></div><div class="state-guide-row"><span class="state-code">AL</span><span class="state-name">Alagoas</span></div><div class="state-guide-row"><span class="state-code">AP</span><span class="state-name">Amapá</span></div><div class="state-guide-row"><span class="state-code">AM</span><span class="state-name">Amazonas</span></div><div class="state-guide-row"><span class="state-code">BA</span><span class="state-name">Bahia</span></div><div class="state-guide-row"><span class="state-code">CE</span><span class="state-name">Ceará</span></div><div class="state-guide-row"><span class="state-code">DF</span><span class="state-name">Distrito Federal</span></div><div class="state-guide-row"><span class="state-code">ES</span><span class="state-name">Espírito Santo</span></div><div class="state-guide-row"><span class="state-code">GO</span><span class="state-name">Goiás</span></div><div class="state-guide-row"><span class="state-code">MA</span><span class="state-name">Maranhão</span></div><div class="state-guide-row"><span class="state-code">MT</span><span class="state-name">Mato Grosso</span></div><div class="state-guide-row"><span class="state-code">MS</span><span class="state-name">Mato Grosso do Sul</span></div><div class="state-guide-row"><span class="state-code">MG</span><span class="state-name">Minas Gerais</span></div><div class="state-guide-row"><span class="state-code">PA</span><span class="state-name">Pará</span></div><div class="state-guide-row"><span class="state-code">PB</span><span class="state-name">Paraíba</span></div><div class="state-guide-row"><span class="state-code">PR</span><span class="state-name">Paraná</span></div><div class="state-guide-row"><span class="state-code">PE</span><span class="state-name">Pernambuco</span></div><div class="state-guide-row"><span class="state-code">PI</span><span class="state-name">Piauí</span></div><div class="state-guide-row"><span class="state-code">RJ</span><span class="state-name">Rio de Janeiro</span></div><div class="state-guide-row"><span class="state-code">RN</span><span class="state-name">Rio Grande do Norte</span></div><div class="state-guide-row"><span class="state-code">RS</span><span class="state-name">Rio Grande do Sul</span></div><div class="state-guide-row"><span class="state-code">RO</span><span class="state-name">Rondônia</span></div><div class="state-guide-row"><span class="state-code">RR</span><span class="state-name">Roraima</span></div><div class="state-guide-row"><span class="state-code">SC</span><span class="state-name">Santa Catarina</span></div><div class="state-guide-row"><span class="state-code">SP</span><span class="state-name">São Paulo</span></div><div class="state-guide-row"><span class="state-code">SE</span><span class="state-name">Sergipe</span></div><div class="state-guide-row"><span class="state-code">TO</span><span class="state-name">Tocantins</span></div></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.caption(
            f"Rentang data: {data_min.strftime('%d %b %Y')} — "
            f"{data_max.strftime('%d %b %Y')}"
        )

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    filtered = apply_filters(
        fact, start_ts, end_ts, customer_states, categories, statuses, seller_states
    )

    if filtered.empty:
        st.warning("Tidak ada data yang cocok dengan kombinasi filter saat ini.")
        st.stop()

    order_view = filtered.drop_duplicates("order_id")
    span_days = max((end_ts - start_ts).days + 1, 1)
    previous_end = start_ts - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=span_days - 1)
    previous = apply_filters(
        fact,
        previous_start,
        previous_end,
        customer_states,
        categories,
        statuses,
        seller_states,
    )
    previous_orders = previous["order_id"].nunique()

    current_revenue = float(filtered["gmv"].sum())
    current_order_value = float(filtered["order_value"].sum())
    current_orders = int(filtered["order_id"].nunique())
    current_customers = int(filtered["customer_unique_id"].nunique())
    current_aov = current_order_value / current_orders if current_orders else 0
    current_rating = float(order_view["review_score"].mean())
    previous_revenue = float(previous["gmv"].sum())
    previous_order_value = float(previous["order_value"].sum())
    previous_customers = int(previous["customer_unique_id"].nunique()) if not previous.empty else 0
    previous_aov = previous_order_value / previous_orders if previous_orders else np.nan

    # Trend ringkas untuk sparkline KPI.
    if span_days > 180:
        kpi_period = filtered["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    elif span_days > 60:
        kpi_period = filtered["order_purchase_timestamp"].dt.to_period("W").dt.start_time
    else:
        kpi_period = filtered["order_purchase_timestamp"].dt.normalize()

    kpi_trend = (
        filtered.assign(_kpi_period=kpi_period)
        .groupby("_kpi_period", as_index=False, observed=True)
        .agg(
            GMV=("gmv", "sum"),
            OrderValue=("order_value", "sum"),
            Pesanan=("order_id", "nunique"),
            Customer=("customer_unique_id", "nunique"),
        )
        .sort_values("_kpi_period")
    )
    kpi_trend["AOV"] = (
        kpi_trend["OrderValue"]
        / kpi_trend["Pesanan"].replace(0, np.nan)
    )

    rating_trend = (
        order_view.assign(
            _kpi_period=(
                order_view["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
                if span_days > 180
                else (
                    order_view["order_purchase_timestamp"].dt.to_period("W").dt.start_time
                    if span_days > 60
                    else order_view["order_purchase_timestamp"].dt.normalize()
                )
            )
        )
        .groupby("_kpi_period", as_index=False, observed=True)
        .agg(Rating=("review_score", "mean"))
        .sort_values("_kpi_period")
    )

    spark_limit = 18
    gmv_spark = kpi_trend["GMV"].tail(spark_limit).tolist()
    orders_spark = kpi_trend["Pesanan"].tail(spark_limit).tolist()
    customers_spark = kpi_trend["Customer"].tail(spark_limit).tolist()
    aov_spark = kpi_trend["AOV"].tail(spark_limit).tolist()
    rating_spark = rating_trend["Rating"].tail(spark_limit).tolist()

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">COMMERCE INTELLIGENCE • BRAZIL</div>
            <div class="hero-title">Olist Executive Dashboard</div>
            <div class="hero-subtitle">
                Pantau pertumbuhan, konsentrasi customer, performa produk, dan kualitas layanan
                dalam satu dashboard interaktif. Tampilan aktif mencakup
                <b>{html.escape(pd.Timestamp(start_date).strftime('%d %b %Y'))}</b> hingga
                <b>{html.escape(pd.Timestamp(end_date).strftime('%d %b %Y'))}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(5, gap="small")
    with metric_columns[0]:
        gmv_delta = percent_delta(current_revenue, previous_revenue)
        render_kpi_card(
            "GMV",
            format_currency(current_revenue),
            COLORS["blue"],
            delta=gmv_delta,
            note="Nilai produk, tidak termasuk freight",
            spark=gmv_spark,
            key="gmv",
        )
    with metric_columns[1]:
        orders_delta = percent_delta(current_orders, previous_orders)
        render_kpi_card(
            "Pesanan",
            format_integer(current_orders),
            COLORS["cyan"],
            delta=orders_delta,
            note=None if orders_delta else "Belum ada periode pembanding",
            spark=orders_spark,
            key="orders",
        )
    with metric_columns[2]:
        customers_delta = percent_delta(current_customers, previous_customers)
        render_kpi_card(
            "Customer unik",
            format_integer(current_customers),
            COLORS["violet"],
            delta=customers_delta,
            note=None if customers_delta else "Belum ada periode pembanding",
            spark=customers_spark,
            key="customers",
        )
    with metric_columns[3]:
        aov_delta = percent_delta(current_aov, previous_aov)
        render_kpi_card(
            "Average order value",
            format_currency(current_aov),
            COLORS["emerald"],
            delta=aov_delta,
            note="Harga produk + freight per pesanan",
            spark=aov_spark,
            key="aov",
        )
    with metric_columns[4]:
        rating_text = f"{current_rating:.2f} / 5" if np.isfinite(current_rating) else "N/A"
        reviewed_share = order_view["review_score"].notna().mean() * 100
        render_kpi_card(
            "Rating rata-rata",
            rating_text,
            COLORS["amber"],
            note=f"Cakupan ulasan {reviewed_share:.1f}% pesanan",
            spark=rating_spark,
            key="rating",
        )

    active_section = st.segmented_control(
        "Bagian dashboard",
        ["Ringkasan", "Customer & Peta", "Produk & Seller", "Layanan & Pembayaran"],
        default="Ringkasan",
        selection_mode="single",
        required=True,
        key="dashboard_section",
        label_visibility="collapsed",
        width="stretch",
    )

    # ------------------------------------------------------------------ Ringkasan
    if active_section == "Ringkasan":
        top_category = filtered.groupby("category", observed=True)["gmv"].sum().idxmax()
        top_state = filtered.groupby("customer_state", observed=True)["gmv"].sum().idxmax()
        delivered = order_view.dropna(subset=["is_on_time"])
        on_time_rate = delivered["is_on_time"].mean() * 100 if not delivered.empty else np.nan
        insight = (
            f"Kategori dengan GMV tertinggi adalah {top_category}, sedangkan customer dari "
            f"{format_state_name(top_state)} memberikan kontribusi wilayah terbesar. "
            + (f"Sebanyak {on_time_rate:.1f}% pesanan terkirim tepat waktu." if np.isfinite(on_time_rate) else "Data ketepatan waktu belum tersedia pada filter ini.")
        )
        st.markdown(f'<div class="insight-box"><b>Insight otomatis:</b> {html.escape(insight)}</div>', unsafe_allow_html=True)

        left, right = st.columns([1.65, 1], gap="large")
        with left:
            section_heading(
                "Tren product GMV dan pesanan",
                "GMV hanya mencakup harga produk; granularitas mengikuti periode.",
            )
            period_label = (
                "Bulan" if span_days > 180 else "Minggu" if span_days > 60 else "Tanggal"
            )
            trend = kpi_trend.rename(columns={"_kpi_period": "period"})
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trend["period"], y=trend["GMV"], name="Product GMV", mode="lines", line=dict(color=COLORS["blue"], width=3), fill="tozeroy", fillcolor="rgba(37,99,235,0.16)", hovertemplate="%{x|%d %b %Y}<br>Product GMV R$ %{y:,.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=trend["period"], y=trend["Pesanan"], name="Pesanan", mode="lines+markers", yaxis="y2", line=dict(color=COLORS["cyan"], width=2), marker=dict(size=5), hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f} pesanan<extra></extra>"))
            fig.update_layout(yaxis=dict(title="Product GMV (R$)"), yaxis2=dict(title="Pesanan", overlaying="y", side="right", showgrid=False), xaxis_title=period_label)
            st.plotly_chart(style_figure(fig, 390), width="stretch", config={"displayModeBar": False})

        with right:
            section_heading("Komposisi status", "Jumlah pesanan unik menurut status terakhir.")
            status_summary = (
                order_view["order_status"]
                .value_counts()
                .loc[lambda values: values.gt(0)]
                .rename_axis("Status")
                .reset_index(name="Pesanan")
            )
            fig = px.pie(status_summary, names="Status", values="Pesanan", hole=.67, color_discrete_sequence=[COLORS["blue"], COLORS["cyan"], COLORS["violet"], COLORS["amber"], COLORS["rose"], COLORS["emerald"]])
            fig.update_traces(textposition="outside", textinfo="percent+label", marker=dict(line=dict(color="white", width=3)), hovertemplate="%{label}<br>%{value:,.0f} pesanan<br>%{percent}<extra></extra>")
            fig.add_annotation(text=f"<b>{format_integer(current_orders)}</b><br><span style='font-size:11px'>pesanan</span>", x=.5, y=.5, showarrow=False, font=dict(color=COLORS["text"], size=18))
            st.plotly_chart(style_figure(fig, 390), width="stretch", config={"displayModeBar": False})

        left, right = st.columns(2, gap="large")
        with left:
            section_heading(
                "Kategori penyumbang product GMV",
                "Sepuluh kategori dengan total harga produk tertinggi; freight tidak disertakan.",
            )
            category_revenue = filtered.groupby(
                "category", as_index=False, observed=True
            )["gmv"].sum().nlargest(10, "gmv").sort_values("gmv")
            fig = px.bar(category_revenue, x="gmv", y="category", orientation="h", color="gmv", color_continuous_scale=["#93C5FD", "#1D4ED8"], labels={"gmv": "Product GMV (R$)", "category": ""})
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(hovertemplate="%{y}<br>Product GMV R$ %{x:,.2f}<extra></extra>")
            st.plotly_chart(style_figure(fig, 400), width="stretch", config={"displayModeBar": False})
        with right:
            section_heading("Kontribusi state customer", "Sepuluh state dengan product GMV tertinggi.")
            state_revenue = (
                filtered.groupby("customer_state", as_index=False, observed=True)
                .agg(GMV=("gmv", "sum"), Pesanan=("order_id", "nunique"))
                .nlargest(10, "GMV")
            )
            state_revenue["State"] = state_revenue["customer_state"].map(format_state_name)
            state_revenue = state_revenue.sort_values("GMV")
            fig = px.bar(
                state_revenue,
                x="GMV",
                y="State",
                orientation="h",
                color="Pesanan",
                color_continuous_scale=["#67E8F9", "#0891B2"],
                labels={"State": "", "GMV": "Product GMV (R$)"},
            )
            fig.update_layout(
                coloraxis_colorbar=dict(title="Pesanan"),
                margin=dict(l=145, r=65, t=38, b=35),
            )
            fig.update_yaxes(automargin=True)
            fig.update_traces(
                customdata=state_revenue[["customer_state", "Pesanan"]],
                hovertemplate=(
                    "<b>%{y}</b><br>Kode: %{customdata[0]}<br>"
                    "Product GMV R$ %{x:,.2f}<br>Pesanan %{customdata[1]:,.0f}<extra></extra>"
                ),
            )
            st.plotly_chart(style_figure(fig, 430), width="stretch", config={"displayModeBar": False})

    # ----------------------------------------------------------- Customer dan Peta
    elif active_section == "Customer & Peta":
        map_orders = order_view.dropna(subset=["customer_lat", "customer_lng"])
        map_points = (
            map_orders.groupby(
                ["customer_state", "customer_city", "customer_lat", "customer_lng"],
                as_index=False,
                observed=True,
            )
            .agg(customers=("customer_unique_id", "nunique"), orders=("order_id", "nunique"))
        )
        order_gmv = filtered.groupby("order_id", as_index=False, observed=True)["gmv"].sum()
        map_gmv = map_orders[["order_id", "customer_state", "customer_city", "customer_lat", "customer_lng"]].merge(order_gmv, on="order_id", how="left")
        map_gmv = map_gmv.groupby(
            ["customer_state", "customer_city", "customer_lat", "customer_lng"],
            as_index=False,
            observed=True,
        )["gmv"].sum()
        map_points = map_points.merge(map_gmv, on=["customer_state", "customer_city", "customer_lat", "customer_lng"], how="left")

        control_1, control_2, spacer = st.columns([1, 1.2, 3.4])
        with control_1:
            map_mode = st.selectbox("Mode peta", ["Bubble", "Heatmap"], key="map_mode")
        with control_2:
            max_points = st.slider(
                "Jumlah lokasi",
                50,
                min(800, len(map_points)),
                min(300, len(map_points)),
                1,
                key="map_points",
            ) if len(map_points) >= 50 else len(map_points)

        section_heading("Sebaran customer interaktif", "Peta Folium dapat digeser, diperbesar, diperkecil, dan ditampilkan layar penuh.")
        if map_points.empty:
            st.info("Koordinat customer tidak tersedia untuk kombinasi filter ini.")
        else:
            plotted = map_points.nlargest(int(max_points), "customers")
            customer_map = make_customer_map(plotted, map_mode)
            st_folium(customer_map, height=545, use_container_width=True, returned_objects=[])
            map_coverage = map_orders["customer_unique_id"].nunique() / max(current_customers, 1) * 100
            st.caption(f"Cakupan koordinat: {map_coverage:.1f}% customer pada hasil filter • Menampilkan {format_integer(len(plotted))} lokasi teratas.")

        left, right = st.columns([1.25, 1], gap="large")
        with left:
            section_heading("Profil wilayah", "Product GMV, pesanan, dan customer unik pada setiap state.")
            state_profile = (
                filtered.groupby("customer_state", as_index=False, observed=True)
                .agg(
                    GMV=("gmv", "sum"),
                    NilaiPesanan=("order_value", "sum"),
                    Pesanan=("order_id", "nunique"),
                    Customer=("customer_unique_id", "nunique"),
                )
                .sort_values("GMV", ascending=False)
            )
            state_profile["AOV"] = state_profile["NilaiPesanan"] / state_profile["Pesanan"]
            display_state = state_profile.copy()
            display_state.insert(
                0,
                "State",
                display_state["customer_state"].map(
                    lambda code: format_state_name(code, include_code=False)
                ),
            )
            display_state = display_state.rename(columns={"customer_state": "Kode"})
            display_state["GMV"] = display_state["GMV"].map(format_currency)
            display_state["AOV"] = display_state["AOV"].map(format_currency)
            display_state = display_state[
                ["State", "Kode", "GMV", "Pesanan", "Customer", "AOV"]
            ]
            st.dataframe(display_state, width="stretch", hide_index=True, height=380)
        with right:
            section_heading(
                "Frekuensi pembelian customer",
                "Segmentasi menurut delivered order sepanjang riwayat; bukan cohort retention.",
            )
            customer_segments = (
                order_view.drop_duplicates("customer_unique_id")["customer_segment"]
                .value_counts()
                .loc[lambda values: values.gt(0)]
                .rename_axis("Segmen")
                .reset_index(name="Customer")
            )
            total_segment_customers = int(customer_segments["Customer"].sum())
            customer_segments["Persentase"] = (
                customer_segments["Customer"] / max(total_segment_customers, 1) * 100
            )
            customer_segments["Legenda"] = customer_segments.apply(
                lambda row: f"{row['Segmen']} · {row['Persentase']:.1f}%",
                axis=1,
            )
            fig = px.pie(
                customer_segments,
                names="Legenda",
                values="Customer",
                hole=.64,
                color="Segmen",
                color_discrete_map={
                    "One-time customer": COLORS["blue"],
                    "Repeat customer": COLORS["emerald"],
                    "Belum ada pesanan selesai": COLORS["muted"],
                },
            )
            fig.update_traces(
                textinfo="none",
                marker=dict(line=dict(color=COLORS["surface"], width=3)),
                hovertemplate=(
                    "<b>%{label}</b><br>%{value:,.0f} customer"
                    "<br>%{percent}<extra></extra>"
                ),
            )
            fig.add_annotation(
                text=(
                    f"<b>{format_integer(total_segment_customers)}</b><br>"
                    "<span style='font-size:11px'>customer unik</span>"
                ),
                x=.5,
                y=.5,
                showarrow=False,
                font=dict(color=COLORS["text"], size=18),
            )
            fig = style_figure(fig, 395)
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-.04,
                    xanchor="center",
                    x=.5,
                    font=dict(color=COLORS["text"], size=11),
                ),
                margin=dict(l=20, r=20, t=25, b=75),
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # -------------------------------------------------------------- Produk/Seller
    elif active_section == "Produk & Seller":
        category_rating = (
            filtered.drop_duplicates(["order_id", "category"])
            .groupby("category", as_index=False, observed=True)
            .agg(Rating=("review_score", "mean"))
        )
        category_profile = (
            filtered.groupby("category", as_index=False, observed=True)
            .agg(
                GMV=("gmv", "sum"),
                Unit=("order_item_id", "count"),
                Pesanan=("order_id", "nunique"),
                Customer=("customer_unique_id", "nunique"),
            )
            .merge(category_rating, on="category", how="left", validate="one_to_one")
        )
        category_profile["GMV per Unit"] = category_profile["GMV"] / category_profile["Unit"]

        left, right = st.columns([1.35, 1], gap="large")
        with left:
            section_heading("Matriks portofolio kategori", "Ukuran bubble menunjukkan jumlah pesanan; warna menunjukkan rating.")
            fig = px.scatter(category_profile, x="Unit", y="GMV", size="Pesanan", color="Rating", hover_name="category", color_continuous_scale=[COLORS["rose"], COLORS["amber"], COLORS["emerald"]], size_max=52, labels={"Unit": "Unit terjual", "GMV": "Product GMV (R$)"})
            fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Unit %{x:,.0f}<br>Product GMV R$ %{y:,.2f}<br>Rating %{marker.color:.2f}<extra></extra>")
            st.plotly_chart(style_figure(fig, 450), width="stretch", config={"displayModeBar": False})
        with right:
            section_heading("Kategori bernilai tinggi", "Peringkat berdasarkan product GMV rata-rata per unit.")
            high_value = category_profile[category_profile["Unit"].ge(10)].nlargest(12, "GMV per Unit").sort_values("GMV per Unit")
            fig = px.bar(high_value, x="GMV per Unit", y="category", orientation="h", color="Rating", color_continuous_scale=["#FDE68A", COLORS["emerald"]], labels={"category": "", "GMV per Unit": "Product GMV per unit (R$)"})
            fig.update_traces(hovertemplate="%{y}<br>Product GMV/unit R$ %{x:,.2f}<extra></extra>")
            st.plotly_chart(style_figure(fig, 450), width="stretch", config={"displayModeBar": False})

        left, right = st.columns(2, gap="large")
        with left:
            section_heading(
                "Produk terlaris",
                "Dataset publik Olist tidak menyediakan nama produk; label menggunakan kategori dan ID singkat.",
            )
            product_rating = (
                filtered.drop_duplicates(["order_id", "product_id"])
                .groupby("product_id", as_index=False, observed=True)
                .agg(Rating=("review_score", "mean"))
            )
            product_profile = (
                filtered.groupby(
                    ["product_id", "category"], as_index=False, observed=True
                )
                .agg(
                    GMV=("gmv", "sum"),
                    Unit=("order_item_id", "count"),
                )
                .merge(product_rating, on="product_id", how="left", validate="many_to_one")
                .nlargest(12, "GMV")
                .sort_values("GMV")
            )
            product_profile["Produk"] = product_profile.apply(
                lambda row: (
                    f"{shorten_label(row['category'], 23)} · "
                    f"{str(row['product_id'])[:6].upper()}"
                ),
                axis=1,
            )
            fig = px.bar(
                product_profile,
                x="GMV",
                y="Produk",
                orientation="h",
                color="GMV",
                color_continuous_scale=["#1D4ED8", COLORS["blue"], COLORS["violet"]],
                labels={"GMV": "Product GMV (R$)", "Produk": ""},
            )
            fig.update_layout(
                coloraxis_showscale=False,
                margin=dict(l=175, r=25, t=38, b=35),
            )
            fig.update_yaxes(automargin=True)
            fig.update_traces(
                customdata=product_profile[
                    ["product_id", "category", "Unit", "Rating"]
                ],
                hovertemplate=(
                    "<b>%{y}</b><br>Kategori: %{customdata[1]}"
                    "<br>ID produk: %{customdata[0]}"
                    "<br>Product GMV R$ %{x:,.2f}"
                    "<br>Unit %{customdata[2]:,.0f}"
                    "<br>Rating %{customdata[3]:.2f}<extra></extra>"
                ),
            )
            st.plotly_chart(
                style_figure(fig, 480),
                width="stretch",
                config={"displayModeBar": False},
            )
        with right:
            section_heading("Kekuatan seller per state", "Perbandingan seller aktif, product GMV, dan jumlah pesanan.")
            seller_profile = (
                filtered.groupby("seller_state", as_index=False, observed=True)
                .agg(
                    GMV=("gmv", "sum"),
                    Seller=("seller_id", "nunique"),
                    Pesanan=("order_id", "nunique"),
                )
                .nlargest(12, "GMV")
            )
            seller_profile["State"] = seller_profile["seller_state"].map(format_state_name)
            fig = px.bar(
                seller_profile,
                x="State",
                y="GMV",
                color="Seller",
                color_continuous_scale=["#C4B5FD", "#6D28D9"],
                labels={"State": "State seller", "GMV": "Product GMV (R$)"},
            )
            fig.update_xaxes(tickangle=-32, automargin=True)
            fig.update_traces(
                customdata=seller_profile[["seller_state", "Seller", "Pesanan"]],
                hovertemplate=(
                    "<b>%{x}</b><br>Kode: %{customdata[0]}"
                    "<br>Product GMV R$ %{y:,.2f}"
                    "<br>Seller %{customdata[1]:,.0f}"
                    "<br>Pesanan %{customdata[2]:,.0f}<extra></extra>"
                ),
            )
            st.plotly_chart(
                style_figure(fig, 460),
                width="stretch",
                config={"displayModeBar": False},
            )

    # ---------------------------------------------------- Layanan dan pembayaran
    elif active_section == "Layanan & Pembayaran":
        reviewed = order_view.dropna(subset=["review_score"])
        delivered_orders = order_view.dropna(subset=["delivery_days"])
        valid_delivery = delivered_orders[delivered_orders["delivery_days"].between(0, 90)]

        left, middle, right = st.columns(3, gap="small")
        average_delivery = delivered_orders["delivery_days"].mean()
        late_rate = (delivered_orders["delivery_delay_days"] > 0).mean() * 100 if not delivered_orders.empty else np.nan
        negative_review = (reviewed["review_score"] <= 2).mean() * 100 if not reviewed.empty else np.nan

        if span_days > 180:
            service_period = order_view["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
        elif span_days > 60:
            service_period = order_view["order_purchase_timestamp"].dt.to_period("W").dt.start_time
        else:
            service_period = order_view["order_purchase_timestamp"].dt.normalize()

        service_trend = (
            order_view.assign(_service_period=service_period)
            .groupby("_service_period", as_index=False, observed=True)
            .agg(
                AverageDelivery=("delivery_days", "mean"),
                LateRate=("delivery_delay_days", lambda values: (values > 0).mean() * 100),
                NegativeReview=("review_score", lambda values: (values <= 2).mean() * 100),
            )
            .sort_values("_service_period")
        )

        delivery_spark = service_trend["AverageDelivery"].tail(spark_limit).tolist()
        late_spark = service_trend["LateRate"].tail(spark_limit).tolist()
        negative_spark = service_trend["NegativeReview"].tail(spark_limit).tolist()

        with left:
            render_kpi_card(
                "Waktu kirim rata-rata",
                f"{average_delivery:.1f} hari" if np.isfinite(average_delivery) else "N/A",
                COLORS["cyan"],
                note="Dari pembelian hingga diterima",
                spark=delivery_spark,
                key="delivery",
            )
        with middle:
            render_kpi_card(
                "Keterlambatan",
                f"{late_rate:.1f}%" if np.isfinite(late_rate) else "N/A",
                COLORS["rose"],
                note="Diterima setelah estimasi",
                spark=late_spark,
                key="late",
            )
        with right:
            render_kpi_card(
                "Ulasan negatif",
                f"{negative_review:.1f}%" if np.isfinite(negative_review) else "N/A",
                COLORS["amber"],
                note="Rating 1 atau 2",
                spark=negative_spark,
                key="negative_review",
            )

        left, right = st.columns(2, gap="large")
        with left:
            section_heading("Distribusi rating", "Jumlah pesanan pada setiap skor ulasan.")
            rating_dist = (
                reviewed.assign(Rating=reviewed["review_score"].round().astype(int))
                .groupby("Rating", as_index=False, observed=True)
                .size()
                .rename(columns={"size": "Pesanan"})
            )
            complete_rating = pd.DataFrame({"Rating": [1, 2, 3, 4, 5]}).merge(rating_dist, on="Rating", how="left").fillna(0)
            fig = px.bar(complete_rating, x="Rating", y="Pesanan", color="Rating", color_continuous_scale=[COLORS["rose"], COLORS["amber"], COLORS["emerald"]])
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(hovertemplate="Rating %{x}<br>%{y:,.0f} pesanan<extra></extra>")
            st.plotly_chart(style_figure(fig, 390), width="stretch", config={"displayModeBar": False})
        with right:
            section_heading("Distribusi waktu pengiriman", "Outlier di atas 90 hari dikeluarkan dari grafik, tetapi tetap masuk KPI.")
            fig = px.histogram(valid_delivery, x="delivery_days", nbins=36, color_discrete_sequence=[COLORS["blue"]], labels={"delivery_days": "Waktu pengiriman (hari)", "count": "Pesanan"})
            if np.isfinite(average_delivery):
                fig.add_vline(x=average_delivery, line_dash="dash", line_color=COLORS["rose"], annotation_text=f"Rata-rata {average_delivery:.1f} hari", annotation_position="top right")
            fig.update_traces(hovertemplate="Waktu %{x:.1f} hari<br>%{y:,.0f} pesanan<extra></extra>")
            st.plotly_chart(style_figure(fig, 390), width="stretch", config={"displayModeBar": False})

        selected_order_ids = set(order_view["order_id"])
        filtered_payments = payments[payments["order_id"].isin(selected_order_ids)]
        payment_profile = (
            filtered_payments.groupby("payment_label", as_index=False, observed=True)
            .agg(Nilai=("payment_value", "sum"), Pesanan=("order_id", "nunique"), Transaksi=("payment_value", "size"))
            .sort_values("Nilai", ascending=False)
        )
        left, right = st.columns([1.25, 1], gap="large")
        with left:
            section_heading("Nilai pembayaran menurut metode", "Nilai pembayaran dihitung pada level pesanan yang masuk hasil filter.")
            fig = px.bar(payment_profile.sort_values("Nilai"), x="Nilai", y="payment_label", orientation="h", color="Nilai", color_continuous_scale=["#60A5FA", "#1E40AF"], labels={"payment_label": "", "Nilai": "Nilai pembayaran (R$)"})
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(customdata=payment_profile.sort_values("Nilai")[["Pesanan", "Transaksi"]], hovertemplate="%{y}<br>Nilai R$ %{x:,.2f}<br>Pesanan %{customdata[0]:,.0f}<br>Transaksi %{customdata[1]:,.0f}<extra></extra>")
            st.plotly_chart(style_figure(fig, 400), width="stretch", config={"displayModeBar": False})
        with right:
            section_heading("Porsi metode pembayaran", "Proporsi berdasarkan nilai pembayaran, bukan jumlah transaksi.")
            fig = px.pie(payment_profile, names="payment_label", values="Nilai", hole=.62, color_discrete_sequence=[COLORS["blue"], COLORS["cyan"], COLORS["violet"], COLORS["amber"], COLORS["emerald"]])
            fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="white", width=3)), hovertemplate="%{label}<br>R$ %{value:,.2f}<br>%{percent}<extra></extra>")
            st.plotly_chart(style_figure(fig, 400), width="stretch", config={"displayModeBar": False})
        if categories or seller_states:
            st.caption(
                "Catatan: filter kategori atau state seller memilih order yang cocok; "
                "nilai pembayaran tetap mencakup seluruh pembayaran order tersebut."
            )

    st.markdown("---")
    footer_left, footer_middle, footer_right = st.columns([1.6, 1, 1])
    with footer_left:
        st.caption(
            f"Menampilkan {format_integer(len(filtered))} item dari "
            f"{format_integer(current_orders)} pesanan • Product GMV = harga produk; "
            "AOV = (harga produk + freight) / pesanan"
        )
    with footer_middle:
        with st.expander("Kualitas data"):
            st.dataframe(model["quality"], hide_index=True, width="stretch")
    with footer_right:
        export_signature = (
            fingerprint,
            start_ts.isoformat(),
            end_ts.isoformat(),
            tuple(customer_states),
            tuple(categories),
            tuple(statuses),
            tuple(seller_states),
        )
        if st.session_state.get("export_signature") != export_signature:
            st.session_state.pop("export_data", None)

        export_ready = "export_data" in st.session_state
        if not export_ready and st.button(
            "Siapkan file CSV",
            width="stretch",
            help="File baru dibuat ketika diminta agar rerun filter tetap ringan.",
        ):
            with st.spinner("Menyiapkan file CSV …"):
                st.session_state["export_data"] = create_order_export(filtered)
                st.session_state["export_signature"] = export_signature
            export_ready = True

        if export_ready:
            st.download_button(
                "Unduh hasil filter (.csv)",
                data=st.session_state["export_data"],
                file_name=f"olist_filtered_{start_date}_{end_date}.csv",
                mime="text/csv",
                width="stretch",
            )


if __name__ == "__main__":
    main()
