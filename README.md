# CRITIC-AI — Multilingual Prompt Engineering and Critical Review on NVIDIA DGX Spark

**From a simple idea to a rigorous prompt — with an optional second-pass critical review.**

CRITIC-AI is a lightweight, multilingual web application that helps users turn rough ideas into structured, actionable prompts. It runs on an **NVIDIA DGX Spark GB10** and uses a **locally hosted language model** through an OpenAI-compatible inference API. The application does **not** require the OpenAI cloud API or any other external AI service.

## Highlights

- **12 languages:** Spanish, English, French, Italian, Portuguese, German, Simplified Chinese, Japanese, Russian, Arabic, Hebrew, and Greek.
- **Flag-based language selector** at the top of the web interface, controlling the interface and generated prompt language.
- **10 critical-thinking strategies:** critical diagnosis, devil's advocate, literature review, epistemology, peer review, experimental design, novelty, defense, contradiction analysis, and final audit.
- **Automatic strategy selection** or manual choice.
- **Optional two-pass generation:** draft a prompt, then challenge and refine its assumptions, ambiguities, and success criteria.
- **Adjustable depth:** brief, normal, or deep.
- **Additional context** for goals, hypotheses, experimental conditions, and constraints.
- **Copy and download** the resulting prompt.
- **FastAPI endpoints** for integration with other local applications.

## Architecture

```text
Web browser
    |
    v
CRITIC-AI (FastAPI + HTML/CSS/JavaScript)
    |
    v
Local OpenAI-compatible inference endpoint (vLLM)
    |
    v
Qwen/Qwen2.5-7B-Instruct on NVIDIA DGX Spark GB10
```

The currently deployed Spark configuration uses:

| Component | Configuration |
| --- | --- |
| Host | NVIDIA DGX Spark GB10 |
| Application port | `8050` |
| Local inference API | `http://127.0.0.1:8001/v1` |
| Model | `Qwen/Qwen2.5-7B-Instruct` |
| Backend | FastAPI |
| Frontend | Vanilla HTML, CSS, and JavaScript |

These values describe the current deployment; other compatible local models and endpoints may also work.

## Requirements

- Python 3.10 or newer.
- A running OpenAI-compatible local inference server supporting `GET /v1/models` and `POST /v1/chat/completions`.
- Network access from CRITIC-AI to that inference server.

CRITIC-AI does not download a model or modify existing inference containers.

## Quick start

```bash
git clone https://github.com/LuisAlbertoMunozUbando/CRITIC-AI.git
cd CRITIC-AI

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Configure `.env` for your local inference endpoint. On the DGX Spark deployment:

```dotenv
LLM_BASE_URL=http://127.0.0.1:8001/v1
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
```

Load the environment and start the application:

```bash
set -a
. ./.env
set +a

uvicorn app:app --host 0.0.0.0 --port 8050
```

Open `http://localhost:8050` on the Spark, or use its private network address from an authorized device.

**Security:** The application does not include user authentication. Do not expose port 8050 directly to the public internet. Use a private network, VPN, or an authenticated HTTPS reverse proxy.

## Running as a systemd service

For a persistent Linux deployment, configure a systemd service to run:

```bash
/home/alberto/CRITIC-AI/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8050
```

Set the working directory to `/home/alberto/CRITIC-AI`, load environment variables from `.env`, and enable the service after confirming the port is not already occupied by a manually started Uvicorn process.

## API example

```bash
curl -s http://127.0.0.1:8050/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "idea": "Evaluate the experimental design of my robot",
    "strategy": "auto",
    "depth": "profundo",
    "language": "en",
    "second_pass": true
  }'
```

Other available endpoints include `GET /api/health`, `GET /api/models`, `GET /api/strategies`, and `GET /api/languages`.

## Branding

The web interface supports a CRITIC-AI logo in `static/critic-ai-logo.png` and a compact SVG favicon in `static/logo.svg`. Ensure that the PNG is committed to the repository when deploying the branded interface.

## Docker

```bash
docker build -t critic-ai .
docker run --rm --network host --env-file .env critic-ai
```

With `--network host`, `127.0.0.1` refers to the host network. For isolated Docker networks, configure `LLM_BASE_URL` to point to the reachable inference service.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Design principle

**AI should strengthen critical thinking, not replace it.** CRITIC-AI is designed to surface assumptions, improve questions, and make evaluation criteria explicit. It does not claim to have verified external evidence, read documents, or checked academic references unless that information has actually been provided to the model.

## License

MIT.
