# Business Intelligence Agent - Backend API

FastAPI backend for the BI Agent providing REST endpoints for sales pipeline and project execution analysis.

## Features

- ✅ REST API with FastAPI & Uvicorn
- ✅ Monday.com integration (Deals & Work Orders)
- ✅ AI-powered insights via Groq
- ✅ Data normalization & quality checks
- ✅ CORS enabled for frontend integration
- ✅ Production-ready with health checks

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```
MONDAY_API_KEY=your_api_key
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
GROQ_API_KEY=your_groq_key  # Optional for AI insights
PORT=8000
```

## Run Locally

```bash
# Development
python api.py

# Or with uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`
API Docs at: `http://localhost:8000/docs`

## API Endpoints

### POST `/analyze`
Analyze a business question
```json
{"question": "What is our win rate?"}
```

### GET `/health`
Check API status

### GET `/metrics`
Get current metrics

### POST `/refresh`
Refresh monday.com data

## Project Structure

```
├── api.py                   # FastAPI app
├── bi_agent.py              # Agent orchestrator
├── src/
│   ├── monday_api_connector.py
│   ├── data_processor.py
│   ├── insight_engine.py
│   └── groq_ai_engine.py
├── config/
│   └── .env.example
├── tests/
│   └── test_bi_agent.py
└── requirements.txt
```

## Deployment on Render

1. Push to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn api:app --host 0.0.0.0 --port $PORT`

## License

MIT
