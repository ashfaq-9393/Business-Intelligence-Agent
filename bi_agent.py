"""
Business Intelligence Agent - Main Orchestrator
Founder-level business intelligence system for monday.com boards
With Groq AI-powered insights
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import json

from src.monday_api_connector import MondayConnector
from src.data_processor import DataProcessor
from src.insight_engine import InsightEngine
from src.groq_ai_engine import GroqAIEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusinessIntelligenceAgent:
    """
    Founder-Level Business Intelligence Agent
    Analyzes monday.com boards and provides executive insights
    Enhanced with Groq AI for advanced analytics
    """
    
    def __init__(self, api_key: str, deals_board_id: str, work_orders_board_id: str, groq_api_key: Optional[str] = None):
        """
        Initialize BI Agent
        
        Args:
            api_key: Monday.com API key
            deals_board_id: Deals board ID
            work_orders_board_id: Work orders board ID
            groq_api_key: Groq AI API key (optional)
        """
        self.connector = MondayConnector(api_key)
        self.deals_board_id = deals_board_id
        self.work_orders_board_id = work_orders_board_id
        self.processor = DataProcessor()
        self.engine = InsightEngine()
        
        # Initialize Groq AI engine if key provided
        self.groq_engine = None
        if groq_api_key:
            self.groq_engine = GroqAIEngine(groq_api_key)
        else:
            logger.warning("⚠️ Groq API key not provided. AI insights will be disabled.")
        
        # Cache for data
        self.deals_data = None
        self.deals_schema = None
        self.work_orders_data = None
        self.work_orders_schema = None
    
    def refresh_data(self) -> bool:
        """
        Refresh all data from monday.com
        
        Returns:
            Success status
        """
        try:
            logger.info("Refreshing data from monday.com...")
            
            # Get Deals board
            self.deals_schema = self.connector.get_board_schema(self.deals_board_id)
            self.deals_data = self.connector.get_all_board_items(self.deals_board_id)
            
            # Get Work Orders board
            self.work_orders_schema = self.connector.get_board_schema(self.work_orders_board_id)
            self.work_orders_data = self.connector.get_all_board_items(self.work_orders_board_id)
            
            logger.info(f"✅ Data refresh complete: {len(self.deals_data)} deals, {len(self.work_orders_data)} orders")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error refreshing data: {e}")
            return False
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Answer an executive business question
        Intelligently routes to appropriate analysis based on question content
        
        Args:
            question: Business question
            
        Returns:
            Structured answer with executive summary
        """
        question_lower = question.lower()
        
        # Prepare response
        response = {
            "question": question,
            "executive_summary": "",
            "data_used": [],
            "key_metrics": {},
            "insights": [],
            "data_caveats": [],
            "recommended_actions": [],
            "details_table": None,
            "is_details_query": False
        }
        
        try:
            # Check if this is a details/table query
            is_details = self._is_details_query(question)
            response["is_details_query"] = is_details
            
            # Determine what data to analyze based on question content
            analyze_deals = self._should_analyze_deals(question_lower)
            analyze_orders = self._should_analyze_orders(question_lower)
            
            # If uncertain, try both
            if not analyze_deals and not analyze_orders:
                analyze_deals = True
                analyze_orders = True
            
            analyzed_something = False
            
            # Route to appropriate analysis
            if analyze_deals and self.deals_data:
                response = self._analyze_deals_question(question, response)
                response["data_used"].append("Deals (Sales Pipeline)")
                analyzed_something = True
            
            if analyze_orders and self.work_orders_data:
                response = self._analyze_work_orders_question(question, response)
                response["data_used"].append("Work Orders (Project Execution)")
                analyzed_something = True
            
            # If both were analyzed, merge insights for cross-board analysis
            if analyze_deals and analyze_orders and analyzed_something:
                response = self._analyze_cross_board_insights(question, response)
            
            # If nothing analyzed, return error
            if not analyzed_something:
                response["status"] = "error"
                response["message"] = "Could not retrieve data. Please check your configuration."
                
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}", exc_info=True)
            response["status"] = "error"
            response["error"] = str(e)
        
        return response
    
    def _determine_relevant_boards(self, question: str) -> List[str]:
        """Determine which boards are relevant to the question"""
        relevant = []
        question_lower = question.lower()
        
        deal_keywords = ["deal", "sales", "pipeline", "customer", "opportunity", "win rate", "forecast", "average deal", "owner", "sector", "revenue", "pipeline value", "risk", "negotiation", "conversion", "billing"]
        work_keywords = ["work order", "project", "task", "execution", "delivery", "completion", "bottleneck", "duration", "billed", "collected", "efficiency", "active", "delayed", "pending"]
        overall_keywords = ["overall", "health", "business", "assessment", "status", "summary", "monthly", "leadership", "risks", "focus"]
        
        if any(keyword in question_lower for keyword in deal_keywords):
            relevant.append("Deals (Sales Pipeline)")
        
        if any(keyword in question_lower for keyword in work_keywords):
            relevant.append("Work Orders (Project Execution)")
        
        if any(keyword in question_lower for keyword in overall_keywords):
            if not relevant:
                relevant.append("Deals (Sales Pipeline)")
                relevant.append("Work Orders (Project Execution)")
        
        return relevant
    
    def _should_analyze_deals(self, question_lower: str) -> bool:
        """Determine if deals data should be analyzed"""
        deal_keywords = [
            "deal", "sales", "pipeline", "win rate", "open pipeline", "pipeline value",
            "sector", "expected revenue", "risk", "probability", "stuck", "negotiation",
            "conversion rate", "average deal", "closed", "owner", "client", "customer",
            "revenue", "forecast", "billing", "collection", "realization"
        ]
        return any(keyword in question_lower for keyword in deal_keywords)
    
    def _should_analyze_orders(self, question_lower: str) -> bool:
        """Determine if work orders data should be analyzed"""
        order_keywords = [
            "work order", "project", "execution", "active", "delayed", "duration",
            "billed", "collected", "collection", "efficiency", "bottleneck",
            "completion", "capacity", "delivery", "revenue", "billing"
        ]
        return any(keyword in question_lower for keyword in order_keywords)
    
    def _is_details_query(self, question: str) -> bool:
        """Determine if this is a details/table query (vs. summary query)"""
        question_lower = question.lower()
        details_keywords = [
            "details", "list", "table", "show me", "all", "owners", "customers",
            "deals breakdown", "order details", "project details", "give me",
            "what are", "who are", "breakdown", "members", "team"
        ]
        return any(keyword in question_lower for keyword in details_keywords)
    
    def _extract_details_table(self, df, question: str, board_type: str):
        """
        Extract relevant columns for a details query
        
        Args:
            df: DataFrame with data
            question: User question
            board_type: 'deals' or 'work_orders'
            
        Returns:
            DataFrame with relevant columns, or None if no data
        """
        if df.empty:
            return None
        
        question_lower = question.lower()
        
        try:
            # Determine which columns to include based on question
            if board_type == "deals":
                # Priority columns for deals details
                priority_cols = [col for col in df.columns if any(
                    keyword in col.lower() for keyword in 
                    ["deal", "name", "title", "owner", "status", "stage", "value", "amount", "date", "customer", "probability"]
                )]
                
                # If asking for owner details specifically
                if "owner" in question_lower:
                    priority_cols = ["Name", "Owner", "Status", "Stage", "Close Date (A)", "Masked Deal value"]
                    priority_cols = [col for col in priority_cols if col in df.columns]
                
                # Select top 20 records with priority columns, falling back to first columns if needed
                cols_to_show = priority_cols[:8] if priority_cols else list(df.columns[:8])
                result_df = df[cols_to_show].head(20)
                
            elif board_type == "work_orders":
                # Priority columns for work orders details
                priority_cols = [col for col in df.columns if any(
                    keyword in col.lower() for keyword in 
                    ["order", "name", "title", "owner", "status", "progress", "date", "priority", "assignee"]
                )]
                
                # If asking for owner details
                if "owner" in question_lower:
                    priority_cols = ["Name", "Owner", "Status", "Priority", "Start Date", "Target Completion Date"]
                    priority_cols = [col for col in priority_cols if col in df.columns]
                
                cols_to_show = priority_cols[:8] if priority_cols else list(df.columns[:8])
                result_df = df[cols_to_show].head(20)
            
            else:
                return None
            
            return result_df if not result_df.empty else None
            
        except Exception as e:
            logger.warning(f"Error extracting details table: {e}")
            return None
    
    def _analyze_deals_question(self, question: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze deals-related question"""
        if not self.deals_data:
            response["data_caveats"].append("Deals board data not loaded")
            return response
        
        try:
            # Convert to DataFrame
            deals_df = self.processor.items_to_dataframe(self.deals_data, self.deals_schema)
            
            if deals_df.empty:
                response["data_caveats"].append("No deals data available")
                return response
            
            # Check if user wants details table
            if response.get("is_details_query"):
                details_table = self._extract_details_table(deals_df, question, "deals")
                if details_table is not None:
                    response["details_table"] = details_table
            
            # Analyze pipeline
            pipeline_analysis = self.engine.analyze_deals_pipeline(deals_df)
            
            # Identify data quality issues
            data_issues = self.processor.identify_data_quality_issues(deals_df)
            
            # Generate insights
            insights = self.engine.generate_recommendations(pipeline_analysis, {}, data_issues)
            
            # Enhance with Groq AI if available
            if self.groq_engine and self.groq_engine.enabled:
                ai_insights = self.groq_engine.generate_insights(pipeline_analysis, data_issues)
                insights = ai_insights + insights  # AI insights first
                ai_summary = self.groq_engine.generate_executive_summary(pipeline_analysis, question)
                if ai_summary:
                    response["executive_summary"] = f"🤖 AI Analysis: {ai_summary}"
                else:
                    response["executive_summary"] = self._summarize_deals_analysis(pipeline_analysis)
                response["ai_powered"] = True
            else:
                response["executive_summary"] = self._summarize_deals_analysis(pipeline_analysis)
                response["ai_powered"] = False
            
            response["key_metrics"] = pipeline_analysis
            response["insights"] = insights
            
            # Add data caveats
            for caveat in data_issues.get("missing_values", {}).items():
                col, info = caveat
                if info["percentage"] > 10:
                    response["data_caveats"].append(
                        f"⚠️ {col}: {info['percentage']}% missing data ({info['count']} records)"
                    )
            
        except Exception as e:
            logger.error(f"Error in deals analysis: {str(e)}", exc_info=True)
            response["error"] = str(e)
        
        return response
    
    def _analyze_work_orders_question(self, question: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze work orders-related question"""
        if not self.work_orders_data:
            response["data_caveats"].append("Work Orders board data not loaded")
            return response
        
        try:
            # Convert to DataFrame
            orders_df = self.processor.items_to_dataframe(self.work_orders_data, self.work_orders_schema)
            
            if orders_df.empty:
                response["data_caveats"].append("No work orders data available")
                return response
            
            # Check if user wants details table
            if response.get("is_details_query"):
                details_table = self._extract_details_table(orders_df, question, "work_orders")
                if details_table is not None:
                    response["details_table"] = details_table
            
            # Analyze execution
            execution_analysis = self.engine.analyze_work_orders(orders_df)
            
            # Identify data quality issues
            data_issues = self.processor.identify_data_quality_issues(orders_df)
            
            # Generate insights
            insights = self.engine.generate_recommendations({}, execution_analysis, data_issues)
            
            # Enhance with Groq AI if available
            if self.groq_engine and self.groq_engine.enabled:
                ai_insights = self.groq_engine.generate_insights(execution_analysis, data_issues)
                insights = ai_insights + insights  # AI insights first
                ai_summary = self.groq_engine.generate_executive_summary(execution_analysis, question)
                if ai_summary:
                    response["executive_summary"] = f"🤖 AI Analysis: {ai_summary}"
                else:
                    response["executive_summary"] = self._summarize_execution_analysis(execution_analysis)
                response["ai_powered"] = True
            else:
                response["executive_summary"] = self._summarize_execution_analysis(execution_analysis)
                response["ai_powered"] = False
            
            response["key_metrics"] = execution_analysis
            response["insights"] = insights
            
            # Add data caveats
            for caveat in data_issues.get("missing_values", {}).items():
                col, info = caveat
                if info["percentage"] > 10:
                    response["data_caveats"].append(
                        f"⚠️ {col}: {info['percentage']}% missing data ({info['count']} records)"
                    )
            
        except Exception as e:
            logger.error(f"Error in work orders analysis: {str(e)}", exc_info=True)
            response["error"] = str(e)
        
        return response
    
    def _analyze_cross_board_insights(self, question: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze cross-board insights combining sales and operations
        Answers strategic questions requiring both datasets
        """
        try:
            # Get existing metrics from both boards
            deals_metrics = response.get("key_metrics", {})
            
            # Use Groq AI to provide cross-board analysis if available
            if self.groq_engine and self.groq_engine.enabled:
                context = f"""
Question: {question}

Sales Pipeline Metrics:
- Total Deals: {deals_metrics.get('total_deals', 0)}
- Win Rate: {deals_metrics.get('win_rate', 0)}%
- Total Pipeline Value: ${deals_metrics.get('value_metrics', {}).get('total_value', 0):,.0f}

The user is asking a strategic question that combines sales and operations insights.
Provide executive-level insights that show business connections and growth opportunities.
"""
                ai_response = self.groq_engine.analyze_question(question, context)
                if ai_response and "analysis" in ai_response:
                    response["executive_summary"] = f"🤖 Strategic Insight: {ai_response['analysis']}"
                    if "recommendations" in ai_response:
                        response["insights"] = ai_response["recommendations"]
                    response["ai_powered"] = True
            
        except Exception as e:
            logger.warning(f"Error in cross-board analysis: {e}")
        
        return response
    
    def _analyze_overall_health(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall business health"""
        try:
            summary_parts = []
            
            if self.deals_data and self.deals_schema:
                try:
                    deals_df = self.processor.items_to_dataframe(self.deals_data, self.deals_schema)
                    deals_metrics = self.engine.calculate_basic_metrics(deals_df)
                    response["deals_summary"] = deals_metrics
                    
                    if deals_metrics.get("total_records"):
                        summary_parts.append(f"{deals_metrics['total_records']} deals active")
                except Exception as e:
                    logger.warning(f"Error processing deals for overall health: {e}")
            
            if self.work_orders_data and self.work_orders_schema:
                try:
                    orders_df = self.processor.items_to_dataframe(self.work_orders_data, self.work_orders_schema)
                    orders_metrics = self.engine.calculate_basic_metrics(orders_df)
                    response["execution_summary"] = orders_metrics
                    
                    if orders_metrics.get("total_records"):
                        summary_parts.append(f"{orders_metrics['total_records']} work orders in progress")
                except Exception as e:
                    logger.warning(f"Error processing work orders for overall health: {e}")
            
            if summary_parts:
                response["executive_summary"] = "📊 Business Health: " + " | ".join(summary_parts)
            else:
                response["executive_summary"] = "Business health assessment combining sales and execution metrics"
            
            response["insights"] = [
                "✅ Data systems connected and operational",
                "📊 Sales pipeline and project execution tracked",
                "🔍 Data quality issues identified - see caveats for details"
            ]
        
        except Exception as e:
            logger.error(f"Error in overall health analysis: {str(e)}", exc_info=True)
            response["error"] = str(e)
            response["executive_summary"] = "Unable to complete overall health assessment"
        
        return response
    
    @staticmethod
    def _summarize_deals_analysis(analysis: Dict[str, Any]) -> str:
        """Create executive summary for deals analysis"""
        total = analysis.get("total_deals", 0)
        total_value = analysis.get("value_metrics", {}).get("total_value", 0)
        avg_size = analysis.get("value_metrics", {}).get("average_deal_size", 0)
        
        return f"Pipeline Analysis: {total} deals worth ${total_value:,.0f} (avg ${avg_size:,.0f} per deal)"
    
    @staticmethod
    def _summarize_execution_analysis(analysis: Dict[str, Any]) -> str:
        """Create executive summary for work orders analysis"""
        total = analysis.get("total_orders", 0)
        statuses = analysis.get("by_status", {})
        
        return f"Project Status: {total} active work orders across {len(statuses)} status categories"


def main():
    """Main entry point"""
    load_dotenv()
    
    api_key = os.getenv("MONDAY_API_KEY")
    deals_board_id = os.getenv("DEALS_BOARD_ID")
    work_orders_board_id = os.getenv("WORK_ORDERS_BOARD_ID")
    
    if not all([api_key, deals_board_id, work_orders_board_id]):
        print("Missing configuration. Please set MONDAY_API_KEY, DEALS_BOARD_ID, WORK_ORDERS_BOARD_ID in .env")
        return
    
    # Initialize agent
    agent = BusinessIntelligenceAgent(api_key, deals_board_id, work_orders_board_id)
    
    # Refresh data
    if not agent.refresh_data():
        print("Failed to refresh data from monday.com")
        return
    
    # Example questions
    example_questions = [
        "What is our sales pipeline status?",
        "How are our work orders progressing?",
        "What is our win rate and average deal size?",
        "Where are project bottlenecks?",
        "Overall business health assessment"
    ]
    
    print("\n" + "="*80)
    print("BUSINESS INTELLIGENCE AGENT - EXECUTIVE DASHBOARD")
    print("="*80)
    
    for question in example_questions:
        print(f"\nQuestion: {question}")
        print("-"*80)
        
        response = agent.ask_question(question)
        
        # Format response
        if response.get("status") == "error":
            print(f"Error: {response.get('error', 'Unknown error')}")
        else:
            print(f"{response.get('executive_summary', 'Analysis complete')}")
            
            if response.get("insights"):
                print("\nKey Insights:")
                for insight in response["insights"][:3]:
                    print(f"  * {insight}")
            
            if response.get("data_caveats"):
                print("\nData Quality Notes:")
                for caveat in response["data_caveats"]:
                    print(f"  * {caveat}")


if __name__ == "__main__":
    main()
