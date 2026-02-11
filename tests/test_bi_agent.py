"""
Unit tests for Business Intelligence Agent
"""

import unittest
from datetime import datetime
import pandas as pd
from src.data_processor import DataProcessor
from src.insight_engine import InsightEngine


class TestDataProcessor(unittest.TestCase):
    """Test data processing functions"""
    
    def test_normalize_date_iso_format(self):
        """Test ISO date parsing"""
        date_str = "2024-01-15T10:30:00Z"
        result = DataProcessor.normalize_date(date_str)
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
    
    def test_normalize_currency_with_symbols(self):
        """Test currency normalization"""
        amount = "$1,234.56"
        result = DataProcessor.normalize_currency(amount)
        self.assertAlmostEqual(result, 1234.56, places=2)
    
    def test_normalize_status(self):
        """Test status normalization"""
        status = "Won"
        result = DataProcessor.normalize_status(status)
        self.assertEqual(result, "won")
    
    def test_items_to_dataframe(self):
        """Test conversion to DataFrame"""
        items = [
            {
                "id": "1",
                "name": "Test Item",
                "created_at": "2024-01-01T00:00:00Z",
                "column_values": [
                    {"id": "col1", "text": "Value1"}
                ]
            }
        ]
        
        schema = {
            "columns": [
                {"id": "col1", "title": "Test Column", "type": "text"}
            ]
        }
        
        df = DataProcessor.items_to_dataframe(items, schema)
        self.assertEqual(len(df), 1)
        self.assertIn("Test Column", df.columns)


class TestInsightEngine(unittest.TestCase):
    """Test insight generation"""
    
    def test_basic_metrics(self):
        """Test basic metrics calculation"""
        data = {
            "id": [1, 2, 3],
            "value": [100, 200, 300]
        }
        df = pd.DataFrame(data)
        
        metrics = InsightEngine.calculate_basic_metrics(df)
        self.assertEqual(metrics["total_records"], 3)
    
    def test_deals_pipeline_analysis(self):
        """Test deals pipeline analysis"""
        data = {
            "id": [1, 2, 3],
            "Status": ["Won", "Won", "Lost"]
        }
        df = pd.DataFrame(data)
        
        analysis = InsightEngine.analyze_deals_pipeline(df)
        self.assertEqual(analysis["total_deals"], 3)
        self.assertIn("by_status", analysis)


if __name__ == "__main__":
    unittest.main()
