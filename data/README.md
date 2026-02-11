# Sample Data Files

This directory contains sample/test data files for the BI Agent.

## Usage

For testing without a live monday.com connection, sample data files can be:
1. Loaded directly from JSON
2. Used to populate test DataFrames
3. Used to validate analysis logic

## Example Sample Data Format

```json
{
  "deals": [
    {
      "id": "deal_001",
      "name": "Enterprise Contract - Acme Corp",
      "status": "Negotiation",
      "amount": 125000,
      "stage": "Proposal",
      "close_date": "2024-03-15",
      "probability": 75,
      "owner": "John Sales"
    }
  ],
  "work_orders": [
    {
      "id": "wo_001", 
      "name": "Onboarding - Acme Corp",
      "status": "In Progress",
      "priority": "High",
      "start_date": "2024-02-01",
      "target_date": "2024-03-15",
      "owner": "Sarah Dev"
    }
  ]
}
```

To add sample data:
1. Create `.json` files in this directory
2. Update `data_processor.py` to load from JSON when API unavailable
3. Use for testing without API credentials
