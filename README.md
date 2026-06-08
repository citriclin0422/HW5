# Top 10 Machine Learning Algorithms

An interactive learning website for exploring ten foundational machine learning
algorithms. The project combines a Next.js frontend with a FastAPI backend and
includes an illustrated study report.

![Machine learning algorithms infographic](frontend/public/assets/top10-infographic.png)

## Features

- Browse ten commonly used machine learning algorithms
- Search lessons and filter them by algorithm family or difficulty
- Review summaries, learning steps, strengths, limitations, and examples
- Answer a quiz for each topic
- Mark topics as complete and track learning progress
- Explore the backend through automatically generated FastAPI documentation

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Lucide React
- **Backend:** FastAPI, Pydantic, Uvicorn
- **Deployment:** Docker and Docker Compose

## Quick Start with Docker

### Prerequisites

- Docker Desktop with Docker Compose

### Run the application

```bash
docker compose up --build
```

Open:

- Web application: http://localhost:3000
- API documentation: http://localhost:8000/docs
- API health check: http://localhost:8000/api/health

Stop the application with:

```bash
docker compose down
```

## Local Development

### Backend

Requires Python 3.10 or newer.

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

Requires Node.js and npm.

```bash
cd frontend
npm install
npm run dev
```

The frontend uses `http://localhost:8000` as the API base URL by default. Set
`NEXT_PUBLIC_API_BASE_URL` to use another backend URL.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Check API status |
| `GET` | `/api/topics` | List topics; supports `q`, `family`, and `difficulty` filters |
| `GET` | `/api/topics/{slug}` | Get one topic by slug |
| `GET` | `/api/meta` | Get available families, difficulties, and topic count |

## Project Structure

```text
.
|-- backend/                  # FastAPI service and lesson data
|-- frontend/                 # Next.js interactive learning application
|-- docker-compose.yml        # Local full-stack environment
|-- ML_Top10_Algorithms_研讀報告_圖文版.html
|-- ML_Top10_Algorithms_研讀報告_圖文版.pdf
`-- 陳煥SIR_Top10機器學習資訊圖表.png
```

## Included Study Materials

- [Illustrated HTML report](ML_Top10_Algorithms_研讀報告_圖文版.html)
- [Illustrated PDF report](ML_Top10_Algorithms_研讀報告_圖文版.pdf)
- [Machine learning infographic](陳煥SIR_Top10機器學習資訊圖表.png)
