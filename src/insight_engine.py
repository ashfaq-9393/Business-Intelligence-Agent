"""
Insight Engine Module
Generates business insights, metrics, and strategic recommendations
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import Counter
from .data_processor import DataProcessor

logger = logging.getLogger(__name__)


class InsightEngine:
    """
    Generates business insights and analytics from processed data
    Provides executive-level strategic recommendations
    """
    
    @staticmethod
    def calculate_basic_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate basic metrics from data
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary of basic metrics
        """
        metrics = {
            "total_records": len(df),
            "date_range": None,
            "record_distribution": {}
        }
        
        # Calculate date range
        date_cols = [col for col in df.columns if isinstance(df[col].dtype, type(pd.Timestamp))]
        if date_cols:
            min_date = df[date_cols].min().min()
            max_date = df[date_cols].max().max()
            if pd.notna(min_date) and pd.notna(max_date):
                metrics["date_range"] = {
                    "start": min_date.isoformat(),
                    "end": max_date.isoformat(),
                    "days": (max_date - min_date).days
                }
        
        return metrics
    
    @staticmethod
    def analyze_deals_pipeline(deals_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze deal pipeline metrics
        
        Args:
            deals_df: Deals DataFrame from monday.com
            
        Returns:
            Pipeline analysis with key metrics
        """
        analysis = {
            "total_deals": len(deals_df),
            "by_status": {},
            "by_stage": {},
            "funnel_analysis": {},
            "value_metrics": {},
            "velocity_metrics": {},
            "win_rate": 0.0
        }
        
        # Status analysis
        status_col = None
        for col in deals_df.columns:
            if col.lower() in ["status", "deal status", "state"]:
                status_col = col
                break
        
        if status_col and status_col in deals_df.columns:
            status_counts = deals_df[status_col].value_counts()
            analysis["by_status"] = {
                str(status): {
                    "count": int(count),
                    "percentage": round((count / len(deals_df)) * 100, 2)
                }
                for status, count in status_counts.items()
            }
            
            # Calculate win rate
            total_deals = len(deals_df)
            if total_deals > 0:
                won_deals = 0
                for status, count in status_counts.items():
                    status_lower = str(status).lower()
                    if any(keyword in status_lower for keyword in ["won", "closed won", "closed", "completed"]):
                        won_deals += count
                
                win_rate = (won_deals / total_deals) * 100
                analysis["win_rate"] = round(win_rate, 2)
                analysis["won_deals"] = int(won_deals)
        
        # Deal amount analysis
        amount_col = None
        for col in deals_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ["amount", "deal value", "value", "size", "mrr", "arr"]):
                amount_col = col
                break
        
        if amount_col and amount_col in deals_df.columns:
            # Normalize currency values
            amounts = deals_df[amount_col].apply(
                lambda x: DataProcessor.normalize_currency(x) if pd.notna(x) else None
            )
            
            valid_amounts = amounts.dropna()
            
            analysis["value_metrics"] = {
                "total_value": float(valid_amounts.sum()) if len(valid_amounts) > 0 else 0,
                "average_deal_size": float(valid_amounts.mean()) if len(valid_amounts) > 0 else 0,
                "median_deal_size": float(valid_amounts.median()) if len(valid_amounts) > 0 else 0,
                "largest_deal": float(valid_amounts.max()) if len(valid_amounts) > 0 else 0,
                "smallest_deal": float(valid_amounts.min()) if len(valid_amounts) > 0 else 0,
                "deals_with_value": int(len(valid_amounts))
            }
        
        return analysis
    
    @staticmethod
    def analyze_work_orders(orders_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze work orders and project execution
        
        Args:
            orders_df: Work Orders DataFrame from monday.com
            
        Returns:
            Execution analysis with key metrics
        """
        analysis = {
            "total_orders": len(orders_df),
            "by_status": {},
            "by_priority": {},
            "timeline_metrics": {},
            "capacity_analysis": {}
        }
        
        # Status analysis
        status_col = None
        for col in orders_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ["status", "state", "order status"]):
                status_col = col
                break
        
        if status_col and status_col in orders_df.columns:
            status_counts = orders_df[status_col].value_counts()
            analysis["by_status"] = {
                str(status): {
                    "count": int(count),
                    "percentage": round((count / len(orders_df)) * 100, 2)
                }
                for status, count in status_counts.items()
            }
        
        # Priority analysis
        priority_col = None
        for col in orders_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ["priority", "urgency", "severity"]):
                priority_col = col
                break
        
        if priority_col and priority_col in orders_df.columns:
            priority_counts = orders_df[priority_col].value_counts()
            analysis["by_priority"] = {
                str(priority): int(count)
                for priority, count in priority_counts.items()
            }
        
        return analysis
    
    @staticmethod
    def identify_trends(df: pd.DataFrame, group_by_col: str, 
                       time_col: str = "created_at") -> Dict[str, Any]:
        """
        Identify trends over time
        
        Args:
            df: DataFrame to analyze
            group_by_col: Column to group by
            time_col: Time column for trend analysis
            
        Returns:
            Trend analysis
        """
        trends = {
            "period_analysis": {},
            "growth_rate": None,
            "distribution": {}
        }
        
        # Check if columns exist
        if group_by_col not in df.columns or time_col not in df.columns:
            return trends
        
        # Ensure time column is datetime
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        
        # Remove NaT values
        df_valid = df.dropna(subset=[time_col])
        
        if len(df_valid) == 0:
            return trends
        
        # Create period grouping (by month)
        df_valid["period"] = df_valid[time_col].dt.to_period("M")
        
        periodical = df_valid.groupby("period")[group_by_col].count()
        trends["period_analysis"] = {
            str(period): int(count)
            for period, count in periodical.items()
        }
        
        # Calculate growth rate if enough data
        if len(periodical) >= 2:
            first_value = periodical.iloc[0]
            last_value = periodical.iloc[-1]
            if first_value > 0:
                growth = ((last_value - first_value) / first_value) * 100
                trends["growth_rate"] = round(growth, 2)
        
        # Distribution analysis
        distribution = df_valid[group_by_col].value_counts()
        trends["distribution"] = {
            str(value): int(count)
            for value, count in distribution.items()
        }
        
        return trends
    
    @staticmethod
    def generate_recommendations(
        deals_analysis: Dict[str, Any],
        orders_analysis: Dict[str, Any],
        data_issues: Dict[str, Any]
    ) -> List[str]:
        """
        Generate strategic recommendations based on analysis
        
        Args:
            deals_analysis: Deal pipeline analysis
            orders_analysis: Work orders analysis
            data_issues: Data quality issues
            
        Returns:
            List of strategic recommendations
        """
        recommendations = []
        
        # Deal pipeline recommendations
        if deals_analysis.get("by_status"):
            statuses = deals_analysis["by_status"]
            
            # Check for bottlenecks
            if "won" in statuses:
                win_rate = statuses["won"].get("percentage", 0)
                if win_rate < 20:
                    recommendations.append(
                        "🎯 Low win rate detected. Consider sales process review and improved qualification"
                    )
            
            if "stuck" in statuses or "stalled" in statuses:
                stuck_deals = next(
                    (v.get("count", 0) for k, v in statuses.items() if "stuck" in str(k).lower()),
                    0
                )
                if stuck_deals > 0:
                    recommendations.append(
                        f"⚠️ {stuck_deals} deals appear stalled. Prioritize deal intervention and customer outreach"
                    )
        
        # Work execution recommendations
        if orders_analysis.get("by_status"):
            statuses = orders_analysis["by_status"]
            
            if "done" in statuses:
                completion_rate = statuses["done"].get("percentage", 0)
                if completion_rate < 50:
                    recommendations.append(
                        "📊 Low project completion rate. Investigate blockers and resource constraints"
                    )
        
        # Data quality recommendations
        if data_issues.get("missing_values"):
            missing = data_issues["missing_values"]
            critical_missing = [
                col for col, info in missing.items()
                if info.get("percentage", 0) > 30
            ]
            
            if critical_missing:
                recommendations.append(
                    f"🔧 Data quality issue: {', '.join(critical_missing)} have >30% missing values"
                )
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations.append(
                "✅ Core metrics stable. Focus on continuous monitoring and incremental optimization"
            )
        
        return recommendations
