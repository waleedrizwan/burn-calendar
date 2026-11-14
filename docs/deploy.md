# Deploy (BURN-021)

The app is one container: FastAPI serves the API and the static front end, and the processed Parquet data are copied into the image. There are no secrets in the image; `FIRMS_MAP_KEY` is used only on the build machine to fetch 2026 data.

## From a clean checkout

```bash
uv sync
cp .env.example .env                    # add FIRMS_MAP_KEY
uv run python -m burn.fetch_country     # history 2000 to 2025, about 3 GB into data/raw
uv run python -m burn.fetch_api         # 2026 from the FIRMS Area API
uv run python -m burn.ingest            # writes data/processed (about 0.5 GB)
uv run pytest
```

Hosting is **Cloudflare Containers**: a small Worker (`worker/index.ts`, config in `wrangler.jsonc`) forwards every request to one container built from the `Dockerfile` (instance type `basic`: 1 GiB memory, 4 GB disk). The container sleeps after 30 minutes without requests; the first request after that waits a few seconds while it starts (the app is healthy about 3 seconds after start).

Needs: a Cloudflare account on the **Workers Paid** plan ($5/month), Node, and Docker running locally (Wrangler builds the linux/amd64 image).

First time only:

```bash
npm install
npx wrangler login
```

Every deploy:

```bash
npx wrangler deploy
```

The first deploy can take several minutes before the container answers. Then open `https://burn-calendar.<your-subdomain>.workers.dev/` in a private browser window and check that the calendar loads without any login.

Tested locally on 2026-11-14: the amd64 image is 886 MB, starts in about 3 seconds, uses about 450 MB with the grid loaded, and a 32 MB hotspot export ran inside a 1 GB memory limit.

The earlier Fly.io config (`fly.toml`) is kept as a fallback.

## Status

Not deployed yet. Waiting for the owner to log in to Cloudflare (`npx wrangler login`) on an account with Workers Paid.
