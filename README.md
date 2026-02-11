# Business Intelligence Agent

A Founder-Level Business Intelligence System for monday.com

## Overview

This BI Agent interprets high-level business questions and provides executive-level insights by analyzing data from monday.com boards. It intelligently handles data quality issues, normalizes inconsistent formats, and delivers strategic recommendations.

## Features

- **Multi-Board Analysis**: Analyzes Sales Pipeline (Deals) and Project Execution (Work Orders) data
- **Intelligent Question Interpretation**: Understands natural language business questions
- **Data Quality Management**: Automatically detects and reports data quality issues
- **Format Normalization**: Handles inconsistent date formats, currencies, and text values
- **Executive Insights**: Provides strategic recommendations, not just numbers
- **Read-Only Access**: Safe, non-destructive analysis of your monday.com data

## Architecture

```
bi_agent/
├── src/
│   ├── monday_api_connector.py    # Monday.com API client
│   ├── data_processor.py           # Data cleaning & normalization
│   └── insight_engine.py           # Insight generation
├── config/
│   └── .env.example                # Configuration template
├── tests/
│   └── test_bi_agent.py            # Unit tests
├── bi_agent.py                     # Main orchestrator
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Access

1. Copy `.env.example` to `.env`:
   ```bash
   cp config/.env.example .env
   ```

2. Get your monday.com API credentials:
   - Go to https://monday.com/developers
   - Create a new app
   - Generate an API token
   - Find your board IDs

3. Update `.env` with your credentials:
   ```
   MONDAY_API_KEY=your_api_key_here
   DEALS_BOARD_ID=your_deals_board_id
   WORK_ORDERS_BOARD_ID=your_work_orders_board_id
   ```

## Usage

### Quick Start

```python
from bi_agent import BusinessIntelligenceAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = BusinessIntelligenceAgent(
    api_key=os.getenv("MONDAY_API_KEY"),
    deals_board_id=os.getenv("DEALS_BOARD_ID"),
    work_orders_board_id=os.getenv("WORK_ORDERS_BOARD_ID")
)

# Refresh data from monday.com
agent.refresh_data()

# Ask a question
response = agent.ask_question("What is our sales pipeline status?")

print(f"📊 {response['executive_summary']}")
print(f"💡 Key Insights:")
for insight in response['insights']:
    print(f"  • {insight}")
```

### Command Line

```bash
python bi_agent.py
```

## Response Format

The agent returns structured responses:

```
📊 Executive Summary
├─ High-level business insight
├─ Key metrics overview
└─ Strategic context

🔍 Data Used
├─ Boards analyzed
├─ Record counts
└─ Data quality status

📈 Key Metrics
├─ Quantitative measures
├─ Trends and distributions
└─ Comparative analysis

💡 Insights
├─ Pattern identification
├─ Risk indicators
└─ Opportunity highlights

⚠️ Data Caveats
├─ Missing value warnings
├─ Format inconsistencies
└─ Quality concerns

🚀 Recommended Actions
├─ Strategic recommendations
├─ Operational priorities
└─ Monitoring suggestions
```

## Data Quality Handling

The agent automatically:

- **Detects missing data**: Reports columns with >10% missing values
- **Normalizes dates**: Handles ISO, US, EU, and fuzzy date formats
- **Standardizes currencies**: Recognizes symbols, thousand separators, decimals
- **Cleans status values**: Maps variations to standard statuses
- **Identifies duplicates**: Warns about duplicate record IDs
- **Flags unusual values**: Detects future dates, outliers, etc.

## Supported Question Types

### Sales Pipeline Questions
- "What is our sales pipeline status?"
- "What is our win rate and average deal size?"
- "How many deals by stage?"
- "What is our sales forecast?"

### Work Orders/Execution Questions
- "How are our work orders progressing?"
- "What are project bottlenecks?"
- "Show me project completion status"
- "Which projects are at risk?"

### Overall Business Questions
- "Overall business health assessment"
- "What should we focus on?"
- "Key business risks"

## Configuration Options

See `.env.example` for all available configuration:

- `MONDAY_API_KEY`: Your monday.com API token
- `MONDAY_API_URL`: API endpoint (default: https://api.monday.com/v2)
- `DEALS_BOARD_ID`: Your deals/sales pipeline board ID
- `WORK_ORDERS_BOARD_ID`: Your work orders/projects board ID
- `LOG_LEVEL`: Logging verbosity (INFO/DEBUG/WARNING)

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

Or with unittest:

```bash
python -m unittest discover tests/
```

## Modules

### monday_api_connector.py
GraphQL API client for monday.com
- Board schema retrieval
- Item fetching with pagination
- Error handling and retry logic

### data_processor.py
Data cleaning and normalization
- Date format normalization
- Currency value parsing
- Status standardization
- DataFrame conversion
- Data quality issue detection

### insight_engine.py
Strategic insight generation
- Pipeline metrics
- Execution analytics
- Trend identification
- Recommendation generation

## Limitations

- **Read-only**: Cannot create or modify data
- **API Rate Limiting**: Respects monday.com API rate limits
- **Data Freshness**: Uses most recent data from API
- **Column Mapping**: Requires standard column naming conventions

## Troubleshooting

### "Invalid API Key"
- Verify `MONDAY_API_KEY` in `.env`
- Check token hasn't expired in monday.com

### "Board not found"
- Verify board IDs in `.env`
- Ensure account has access to the boards

### "No data returned"
- Check board contains items
- Verify column naming conventions
- Review data quality issues in response

## Future Enhancements

- [ ] Interactive CLI with multi-turn conversations
- [ ] Scheduled reporting and alerts
- [ ] Export to PDF/Excel reports
- [ ] Custom metric definitions
- [ ] Integration with Slack/email
- [ ] Machine learning trend forecasting
- [ ] Anomaly detection
- [ ] ROI and attribution analysis

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review monday.com API documentation
3. Check data quality caveats in responses
4. Verify board and column configurations

## License

Proprietary - Founder-Level Business Intelligence System

---

**Last Updated**: February 2025
**Version**: 1.0.0
