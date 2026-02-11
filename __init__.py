"""
Business Intelligence Agent Package
"""

__version__ = "1.0.0"
__author__ = "BI Agent Team"

from .src.monday_api_connector import MondayConnector
from .src.data_processor import DataProcessor
from .src.insight_engine import InsightEngine
from .bi_agent import BusinessIntelligenceAgent

__all__ = [
    "MondayConnector",
    "DataProcessor",
    "InsightEngine",
    "BusinessIntelligenceAgent"
]
