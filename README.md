# Marine Debris Detection

## Deploy the frontend to Vercel

Create a Vercel project from this repository and set **Root Directory** to `marine-debris-detection/frontend`. Vercel will use `frontend/vercel.json` to serve the React app correctly on direct navigation to routes such as `/history` and `/results/1`.

Set this Vercel environment variable for Production (and Preview if needed):

| Variable | Value |
| --- | --- |
| `VITE_API_BASE_URL` | The public base URL of the deployed FastAPI service, with no trailing slash, for example `https://api.example.com` |

Redeploy after changing environment variables. The frontend alone is not a complete deployment: analysis, history, reports, and stored images require the FastAPI backend.

## Host the backend

Run the FastAPI service on a host that supports the model's PyTorch/Ultralytics dependencies, persistent database access, and durable file storage. Configure:

| Variable | Purpose |
| --- | --- |
| `CORS_ORIGINS` | Comma-separated exact frontend origins, such as `https://your-project.vercel.app,https://your-custom-domain.com` |
| `DATABASE_URL` | A persistent database URL; the default SQLite database is local to the backend and is not suitable for ephemeral serverless filesystems |
| `MODEL_PATH` | Path to the trained YOLO weights on the backend host, if using the trained model |
| `MODEL_MODE` | `real` to require trained inference, or `demo` for prototype detections |

The backend also saves uploaded, processed, annotated images and generated reports under `storage/`. That directory must be on persistent storage, or the API's storage layer must be changed to use object storage. Vercel's function filesystem is ephemeral, and bundling the current model/runtime into a Vercel function is not a practical deployment target.

After deployment, open the Vercel URL and verify `/api/health` on the backend URL returns `{"status":"ok"}`. The frontend uses the configured API URL for both `/api` requests and `/storage` images.
