# Copilot Instructions for Business Intelligence Agent

## Project Overview
Founder-Level Business Intelligence AI Agent for monday.com that analyzes sales pipeline and project execution data, providing executive-level insights while handling data quality issues gracefully.

## Key Architecture
- **monday_api_connector.py**: GraphQL API client with pagination support
- **data_processor.py**: Data normalization and quality detection
- **insight_engine.py**: Analytics and recommendation engine
- **bi_agent.py**: Main orchestrator

## Development Guidelines

### Adding New Insight Types
1. Add analysis method to `InsightEngine` class
2. Implement data quality checks in the method
3. Generate human-readable insights
4. Add to `ask_question()` routing logic

### Supporting New Board Types
1. Extend board detection in `_determine_relevant_boards()`
2. Create analysis method in `InsightEngine`
3. Add question keywords for routing
4. Update documentation

### Data Quality
- All numeric values should go through `normalize_currency()`
- All dates should use `normalize_date()` with fuzzy parsing fallback
- Track missing values percentage for caveat reporting
- Always report >10% missing in caveats

## Configuration
- Copy `config/.env.example` to `.env`
- Must include: MONDAY_API_KEY, DEALS_BOARD_ID, WORK_ORDERS_BOARD_ID
- Use `load_dotenv()` before instantiating agent

## Testing
- Unit tests in `tests/test_bi_agent.py`
- Run with `python -m pytest tests/`
- Test data normalization functions thoroughly
- Mock API calls for CI/CD

## Deployment Considerations
- Never commit actual API keys or board IDs
- Use environment variables for all credentials
- Implement rate limit handling for production
- Log all API errors for debugging
- Consider caching for large datasets

