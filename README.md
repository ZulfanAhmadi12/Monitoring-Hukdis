┌─────────────────┐       HTTP API       ┌──────────────────────────┐
│   Streamlit      │ <------------------> │   FastAPI Backend        │
│ (UI Dashboard)   │                      │ (Business Logic & DB IO) │
└─────────────────┘                      └──────────────────────────┘
         │                                             │
         ▼                                             ▼
   File Upload                                   Database Layer
   Filtering                                    Query & Insert
   Visualization                                 Normalization

Streamlit mengelola interaksi pengguna, upload file Excel, dan visualisasi monitoring.
FastAPI menyediakan endpoint untuk insert, update, normalization, dan query data.

| Komponen      | Fungsi Utama                                        |
| ------------- | --------------------------------------------------- |
| **Streamlit** | Upload Excel, filtering data, visualisasi dashboard |
| **FastAPI**   | Validasi data, normalisasi, insert/query database   |
| **Database SQlite**  | Menyimpan data OLD/NEW, metadata, log               |

⚙️ Instalasi
## 1️⃣ Clone Repository
git clone https://github.com/ZulfanAhmadi12/monitoring-hukdis.git

## 2️⃣ Buat Virtual Environment
python -m venv venv

Aktifkan:

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate

## 3️⃣ Install Dependencies

pip install -r requirements.txt

🚀 Menjalankan Aplikasi
## 4️⃣ Jalankan Backend FastAPI
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

Dokumentasi API:

http://localhost:8000/docs

## 5️⃣ Jalankan Frontend Streamlit
streamlit run frontend/main.py

## 🔧 Konfigurasi Environment

### Buat .env pada root:

API_URL=http://localhost:8000
DB_PATH=data/data.db
#### Future-ready (ignored if using SQLite)
DATABASE_URL=sqlite:///./data/data.db
#### BACKEND (FastAPI) CONFIG
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=true
#### FRONTEND (Streamlit) CONFIG
BACKEND_URL=http://127.0.0.1:8000
STREAMLIT_PORT=8501
STREAMLIT_THEME=light
#### DIRECTORY LOCATIONS
UPLOAD_DIR=uploads
LOG_DIR=logs
EXPORT_DIR=exports
BACKUP_DIR=backup
#### APP SETTINGS
APP_NAME=Hukdis Monitoring System
APP_ENV=development  # production / staging
