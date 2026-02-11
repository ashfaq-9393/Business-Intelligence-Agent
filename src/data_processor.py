"""
Data Processing and Normalization Module
Handles data cleaning, normalization, and transformation
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from dateutil import parser as date_parser
import re

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes and normalizes data from monday.com boards
    Handles inconsistent formats, missing data, and data quality issues
    """
    
    @staticmethod
    def parse_column_value(column_value: Dict[str, Any], column_type: Optional[str] = None) -> Any:
        """
        Parse column value based on type, handling various formats
        
        Args:
            column_value: Column value object from monday API
            column_type: Column type for better parsing
            
        Returns:
            Parsed value
        """
        if not column_value:
            return None
        
        text = column_value.get("text")
        value = column_value.get("value")
        
        # Handle empty values
        if not text and not value:
            return None
        
        # If we have JSON value, try to parse it carefully
        if value:
            try:
                parsed = json.loads(value)
                # If it's a dict with useful data, return it
                if isinstance(parsed, dict):
                    # Try to extract meaningful value
                    if "label" in parsed:
                        return parsed["label"]
                    if "name" in parsed:
                        return parsed["name"]
                    # Return the dict itself if it has useful info
                    if len(parsed) > 0:
                        return parsed
                return parsed
            except (ValueError, TypeError, json.JSONDecodeError):
                # If JSON parsing fails, continue to text
                pass
        
        # Return text as primary value
        return text if text else value
    
    @staticmethod
    def normalize_date(date_input: Any) -> Optional[datetime]:
        """
        Normalize various date formats to datetime object
        
        Args:
            date_input: Date in various formats
            
        Returns:
            Normalized datetime object or None
        """
        if not date_input:
            return None
        
        if isinstance(date_input, datetime):
            return date_input
        
        try:
            # Try to parse as ISO format
            if isinstance(date_input, str):
                return date_parser.isoparse(date_input)
        except (ValueError, TypeError):
            try:
                # Try flexible parsing
                return date_parser.parse(date_input, fuzzy=False)
            except (ValueError, TypeError, OverflowError):
                logger.warning(f"Could not parse date: {date_input}")
                return None
        
        return None
    
    @staticmethod
    def normalize_currency(amount: Any) -> Optional[float]:
        """
        Normalize currency values to float
        
        Args:
            amount: Currency value in various formats
            
        Returns:
            Float value or None
        """
        if amount is None:
            return None
        
        if isinstance(amount, (int, float)):
            return float(amount)
        
        if isinstance(amount, str):
            # Remove currency symbols and common separators
            cleaned = re.sub(r'[^\d.,\-]', '', amount)
            
            try:
                # Handle different thousand/decimal separators
                if ',' in cleaned and '.' in cleaned:
                    # Determine which is thousands, which is decimal
                    if cleaned.rindex(',') > cleaned.rindex('.'):
                        cleaned = cleaned.replace('.', '').replace(',', '.')
                    else:
                        cleaned = cleaned.replace(',', '')
                else:
                    cleaned = cleaned.replace(',', '')
                
                return float(cleaned)
            except ValueError:
                logger.warning(f"Could not parse currency: {amount}")
                return None
        
        return None
    
    @staticmethod
    def normalize_status(status: Any, status_map: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Normalize status values to standardized format
        
        Args:
            status: Status value
            status_map: Optional mapping of values to standard statuses
            
        Returns:
            Normalized status or None
        """
        if not status:
            return None
        
        status_str = str(status).strip().lower()
        
        # Apply custom mapping if provided
        if status_map:
            for key, value in status_map.items():
                if key.lower() in status_str or status_str in key.lower():
                    return value
        
        return status_str
    
    @staticmethod
    def items_to_dataframe(items: List[Dict[str, Any]], schema: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert monday.com items to pandas DataFrame with normalized data
        
        Args:
            items: List of items from monday.com
            schema: Board schema with column definitions
            
        Returns:
            Normalized DataFrame
        """
        records = []
        
        # Build column type map
        columns = schema.get("columns", [])
        column_type_map = {col["id"]: col["type"] for col in columns}
        column_name_map = {col["id"]: col["title"] for col in columns}
        
        for item in items:
            record = {
                "id": item.get("id"),
                "name": item.get("name"),
                "created_at": DataProcessor.normalize_date(item.get("created_at")),
                "updated_at": DataProcessor.normalize_date(item.get("updated_at"))
            }
            
            # Process column values
            for col_value in item.get("column_values", []):
                col_id = col_value.get("id")
                col_type = column_type_map.get(col_id)
                col_name = column_name_map.get(col_id, col_id)
                
                parsed_value = DataProcessor.parse_column_value(col_value, col_type)
                record[col_name] = parsed_value
            
            records.append(record)
        
        df = pd.DataFrame(records)
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        return df
    
    @staticmethod
    def identify_data_quality_issues(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify and report data quality issues
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary of data quality issues
        """
        issues = {
            "missing_values": {},
            "duplicate_ids": [],
            "unusual_values": []
        }
        
        # Check for missing values
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100 if len(df) > 0 else 0
            
            if missing_pct > 0:
                issues["missing_values"][col] = {
                    "count": int(missing_count),
                    "percentage": round(missing_pct, 2)
                }
        
        # Check for duplicate IDs
        if "id" in df.columns:
            duplicates = df[df.duplicated(subset=["id"], keep=False)]["id"].tolist()
            if duplicates:
                issues["duplicate_ids"] = duplicates
        
        # Check for date issues
        try:
            # Use UTC-aware datetime for comparison
            now_utc = pd.Timestamp.utcnow()
            if now_utc.tz is None:
                now_utc = now_utc.tz_localize('UTC')
            
            for col in df.columns:
                if "date" in col.lower() or "at" in col.lower():
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        try:
                            col_data = df[col].copy()
                            # Convert to UTC-aware if it's tz-naive
                            if col_data.dtype.tz is None:
                                col_data = col_data.dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
                            else:
                                # Convert existing tz-aware to UTC
                                col_data = col_data.dt.tz_convert('UTC')
                            
                            future_dates = (col_data > now_utc).sum()
                            if future_dates > 0:
                                issues["unusual_values"].append(
                                    f"Column '{col}' has {int(future_dates)} future dates"
                                )
                        except Exception:
                            # Skip if we can't process this column
                            pass
        except Exception as e:
            logger.warning(f"Could not check for future dates: {e}")
        
        return issues
