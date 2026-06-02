# MF FAQ — Next.js UI

Dark-themed chat client for the phase **9** FastAPI API (`runtime/phase_9_api`).

## Requirements

- **Node.js 20.9+** (Next.js 16)

## Setup

From the repository root:

```bash
cd web
npm install
cp .env.local.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL to your API (default http://127.0.0.1:8765)
```

In another terminal, start the API (from repo root, with venv and deps installed):

```bash
python -m runtime.phase_9_api
```

Then:

```bash
cd web && npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000). The UI calls the API on `NEXT_PUBLIC_API_URL`; CORS on the FastAPI app allows browser requests from the Next dev origin.

## Production build

```bash
npm run build && npm start
```

Serve the API and the Next app behind the same host or configure `NEXT_PUBLIC_API_URL` to the public API URL at build time.
