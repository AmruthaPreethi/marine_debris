# Marine Debris Detection

An AI-assisted prototype for reviewing side-scan sonar imagery, recording potential debris detections, and generating survey reports.

> **Prototype notice:** The Vercel deployment uses deterministic demo detections, not the trained YOLO model. Treat results as demonstration output, not validated scientific or operational findings.

## Live demo

- **Web app:** [marine-debris-weld.vercel.app](https://marine-debris-weld.vercel.app)
- **API health:** [marine-debris-api.vercel.app/api/health](https://marine-debris-api.vercel.app/api/health)
- **API docs:** [marine-debris-api.vercel.app/docs](https://marine-debris-api.vercel.app/docs)

## Features

- Upload PNG, JPG, JPEG, or TIFF side-scan sonar images.
- Review analysis history, detection confidence, risk level, and bounding boxes.
- Add optional survey ID and coordinates.
- Download JSON and PDF reports.
- View dashboard statistics and stored image outputs.

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | React, Vite, React Router |
| Backend | Python, FastAPI |
| Database | SQLAlchemy with SQLite by default; PostgreSQL can be configured with `DATABASE_URL` |
| Detection | Trained YOLO model locally when available; deterministic demo detector as fallback and on Vercel |
| Hosting | Two Vercel projects: static frontend and Python serverless API |

## Repository layout

```text
.
├── README.md
├── DEPLOYMENT.md
└── marine-debris-detection/
    ├── frontend/                 # React/Vite app and frontend Vercel config
    │   └── src/
    ├── backend/                  # FastAPI app and backend Vercel function
    │   ├── api/index.py
    │   └── app/
    │       ├── api/               # Auth, analysis, statistics, reports routes
    │       ├── core/              # Runtime configuration and security helpers
    │       ├── db/                # SQLAlchemy setup
    │       └── services/          # Detection, preprocessing, reports, risk logic
    ├── models/                   # Model documentation
    ├── runs/                     # Training outputs and model weights
    └── training/                 # Dataset preparation and model training scripts
```

## Run locally

### 1. Start the backend

From the repository root:

```bash
cd marine-debris-detection/backend
python -m venv .venv
```

Activate the environment, then install the backend dependencies:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API is at `http://127.0.0.1:8000`; interactive docs are at `/docs`.

### 2. Start the frontend

In a second terminal:

```bash
cd marine-debris-detection/frontend
npm ci
```

Create a local `.env` file from the example and set the Vite proxy target:

```dotenv
BACKEND_DEV_URL=http://127.0.0.1:8000
```

Start Vite:

```bash
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`). Vite proxies `/api` and `/storage` requests to the backend.

### Build the frontend

```bash
cd marine-debris-detection/frontend
npm ci
npm run build
```

Vite writes the production bundle to `frontend/dist`.

## Environment variables

See [`marine-debris-detection/.env.example`](marine-debris-detection/.env.example) for placeholders. Never commit real credentials or `.env` files.

| Variable | Used by | Purpose |
| --- | --- | --- |
| `BACKEND_DEV_URL` | Vite development server | Backend target for local `/api` and `/storage` proxy requests |
| `VITE_API_BASE_URL` | Frontend build | Optional direct API origin when hosting without the configured Vercel rewrites; leave blank for this deployment |
| `DATABASE_URL` | Backend | Optional SQLAlchemy database URL; use managed PostgreSQL for durable Vercel data |
| `MODEL_MODE` | Backend | `auto`, `real`, or `demo`; defaults to `auto` locally and `demo` on Vercel |
| `MODEL_PATH` | Backend | Optional path to trained YOLO weights |
| `MAX_UPLOAD_SIZE` | Backend | Maximum accepted image size in bytes; defaults to 20 MiB |
| `FRONTEND_URL` | Backend | Optional frontend origin for direct cross-origin browser requests |
| `CORS_ORIGINS` | Backend | Optional comma-separated additional origins; Vercel configures this in the project settings |

`SECRET_KEY` is not currently used by the application. The frontend's same-origin Vercel rewrites mean `FRONTEND_URL` and `CORS_ORIGINS` are not needed for normal browser-to-API requests.

## API routes

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/login` | Login endpoint |
| `POST` | `/api/analyze` | Upload and analyze an image |
| `GET` | `/api/analyses` | List analyses |
| `GET` | `/api/analyses/{id}` | Get one analysis |
| `GET` | `/api/statistics` | Dashboard counts and aggregates |
| `GET` | `/api/reports/{id}/pdf` | Download a PDF report |
| `GET` | `/api/reports/{id}/json` | Download a JSON report |
| `GET` | `/storage/{path}` | Retrieve generated or uploaded files |

## Deploy to Vercel

The deployment uses two Vercel projects:

1. **Frontend project:** Root Directory `marine-debris-detection/frontend`; build command `npm run build`; output directory `dist`.
2. **Backend project:** Root Directory `marine-debris-detection/backend`; Python function entry point `api/index.py`.

The frontend's `vercel.json` forwards `/api/*` and `/storage/*` to the backend deployment. Full setup and verification notes are in [`DEPLOYMENT.md`](DEPLOYMENT.md).

### Production limitations

- Vercel's filesystem is temporary. Without `DATABASE_URL`, SQLite data can be lost or differ between serverless instances.
- Uploaded images and generated reports are written to temporary storage on Vercel and are not durable. Use object storage for production persistence.
- The Vercel function uses the demo detector. The trained YOLO stack and weights are intended for a separate suitable inference host.

## Model training

Training scripts, dataset preparation, and training notes are under [`marine-debris-detection/training`](marine-debris-detection/training/). The app's local model path defaults to `marine-debris-detection/runs/detect/five_class/weights/best.pt`; set `MODEL_PATH` to override it.
