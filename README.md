
# PreFlight AI

PreFlight AI pairs a cinematic airline operations dashboard with a FastAPI backend,
Langflow workflow automation, and an Ollama-powered LLM for explainable insights.
The repository now ships with a unified Docker Compose stack so you can spin up
the entire experience locally with one command.

## Project Layout

```
preflight-ai/
├── backend/                  # FastAPI service + Langflow connector
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── explain.py
│   │   │   └── predictor.py
│   │   ├── schemas/
│   │   │   └── flight.py
│   │   └── services/
│   │       └── langflow_client.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React dashboard (CRA-style setup)
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+ (for local frontend development)
- Docker Desktop (or Docker Engine + Docker Compose plugin)

## Quick Start (Docker)

1. Replace `<FLOW_ID>` in `docker-compose.yml` (or export `LANGFLOW_URL`)
   so the backend can reach your Langflow deployment.
2. From the project root run:

   ```bash
   docker-compose up --build
   ```

3. Visit the services:
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:5000`
   - Langflow: `http://localhost:7860`
   - Ollama API: `http://localhost:11434`

The frontend talks to the backend via `REACT_APP_API_URL`, and the backend
relays explainability requests to Langflow which, in turn, can call Ollama.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Create a `.env` file in `frontend/` (or copy `.env.example`) to point the dashboard at the backend when running locally without Docker:

```
REACT_APP_API_URL=http://localhost:5000
```

## API Overview

| Endpoint      | Method | Description                                      |
|---------------|--------|--------------------------------------------------|
| `/`           | GET    | Health check for the FastAPI service             |
| `/flights`    | GET    | Returns sample flights with delay probabilities  |
| `/score`      | POST   | Scores a single flight, returning SHAP features  |
| `/insights`   | GET    | Retrieves Langflow/Ollama generated insights     |

The frontend `Dashboard` section calls these endpoints through
`frontend/src/utils/api.js` and renders live probabilities, SHAP factors, and
LLM-generated commentary with graceful fallbacks when services are offline.

## Langflow + Ollama

1. Run `langflow run` (if developing outside Docker) and open `http://localhost:7860`.
2. Build a flow: `Input → Python (parse SHAP) → LLM (Ollama) → Output`.
3. Configure the Ollama node to hit `http://ollama:11434` in Docker or
   `http://localhost:11434` when running locally.
4. Copy the Flow ID and update `LANGFLOW_URL` accordingly (either set the
   environment variable or change the default in `backend/app/services/langflow_client.py`).

With the flow configured, the backend will produce natural-language
explanations for each scored flight while still working even if Langflow/Ollama
are offline (fallback messages are returned).

## Testing

- Frontend: `npm test` inside `frontend/`
- Backend: add FastAPI tests under `backend/tests` (pytest recommended)

## Troubleshooting

- **CORS errors:** ensure `REACT_APP_API_URL` points at the FastAPI origin in the current environment.
- **Langflow timeouts:** the backend returns a readable fallback message so the dashboard stays usable even if Langflow or Ollama are down.
- **Docker build failures:** prune previous images or rebuild with `docker-compose build --no-cache`.

Happy flying! 🚀✈️
