# Business Intelligence Agent - Frontend

Streamlit frontend for the Business Intelligence Agent that connects to a backend API.

## Features

- ✅ Beautiful Streamlit interface
- ✅ Real-time question analysis
- ✅ Dynamic, context-aware visualizations
- ✅ Interactive charts with Plotly
- ✅ Connected to Backend API

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file:
```
BACKEND_URL=http://localhost:8000
```

For production:
```
BACKEND_URL=https://your-backend-url.onrender.com
```

## Run Locally

```bash
streamlit run app.py
```

Frontend will open at: `http://localhost:8501`

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `BACKEND_URL` | No | `http://localhost:8000` | Backend API URL |

## Deployment on Vercel

Frontend cannot be deployed directly on Vercel (Streamlit requires Python runtime). Use alternatives:

### Option 1: Streamlit Cloud (Recommended)
1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add secrets in Settings:
   ```
   BACKEND_URL=https://your-backend.onrender.com
   ```

### Option 2: Railway, Heroku, or Render
1. Push to GitHub
2. Create Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `streamlit run app.py --server.port=$PORT`
5. Add environment variables

## Project Structure

```
├── app.py              # Streamlit frontend
├── requirements.txt    # Dependencies (Streamlit, Plotly, Pandas)
├── .env               # Configuration
└── README.md          # This file
```

## Features

- **Question Input**: Ask natural language questions
- **Dynamic Charts**: Visualizations adapt to your question
- **Real-time Analysis**: Connects to backend API
- **Data Refresh**: Manual refresh button
- **Responsive Layout**: Works on desktop and tablet

## License

MIT
