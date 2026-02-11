"""
Sample/Demo Mode for BI Agent
Allows testing without live monday.com connection
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any


class SampleDataGenerator:
    """Generates realistic sample data for testing"""
    
    @staticmethod
    def generate_sample_deals() -> tuple:
        """Generate sample deals data"""
        deals_items = [
            {
                "id": "deal_001",
                "name": "Acme Corp - Enterprise Contract",
                "created_at": "2024-01-10T09:00:00Z",
                "updated_at": "2024-02-05T14:30:00Z",
                "column_values": [
                    {"id": "status", "text": "Negotiation"},
                    {"id": "status", "text": "Negotiation"},
                    {"id": "amount", "text": "$125,000"},
                    {"id": "stage", "text": "Proposal"},
                    {"id": "probability", "text": "75%"},
                    {"id": "owner", "text": "John Sales"}
                ]
            },
            {
                "id": "deal_002",
                "name": "Global Industries - Initial Deal",
                "created_at": "2024-02-01T10:15:00Z",
                "updated_at": "2024-02-08T11:45:00Z",
                "column_values": [
                    {"id": "status", "text": "Proposal"},
                    {"id": "amount", "text": "$75,500"},
                    {"id": "stage", "text": "Discovery"},
                    {"id": "probability", "text": "30%"},
                    {"id": "owner", "text": "Sarah Sales"}
                ]
            },
            {
                "id": "deal_003",
                "name": "Tech Startup - Early Stage",
                "created_at": "2024-01-20T13:20:00Z",
                "updated_at": "2024-02-09T09:00:00Z",
                "column_values": [
                    {"id": "status", "text": "Won"},
                    {"id": "amount", "text": "$50,000"},
                    {"id": "stage", "text": "Closed"},
                    {"id": "probability", "text": "100%"},
                    {"id": "owner", "text": "John Sales"}
                ]
            },
            {
                "id": "deal_004",
                "name": "Fortune 500 Company",
                "created_at": "2024-02-03T08:45:00Z",
                "updated_at": "2024-02-06T16:30:00Z",
                "column_values": [
                    {"id": "status", "text": "Stuck"},
                    {"id": "amount", "text": "$250,000"},
                    {"id": "stage", "text": "Legal Review"},
                    {"id": "probability", "text": "50%"},
                    {"id": "owner", "text": "Mike Sales"}
                ]
            },
            {
                "id": "deal_005",
                "name": "Mid-Market Growth Company",
                "created_at": "2024-02-05T11:00:00Z",
                "updated_at": "2024-02-07T15:15:00Z",
                "column_values": [
                    {"id": "status", "text": "Qualification"},
                    {"id": "amount", "text": "$95,000"},
                    {"id": "stage", "text": "Initial Call"},
                    {"id": "probability", "text": "15%"},
                    {"id": "owner", "text": "Sarah Sales"}
                ]
            }
        ]
        
        deals_schema = {
            "id": "board_deals",
            "name": "Deals (Sample)",
            "columns": [
                {"id": "name", "title": "Deal Name", "type": "text"},
                {"id": "status", "title": "Status", "type": "status"},
                {"id": "amount", "title": "Deal Amount", "type": "currency"},
                {"id": "stage", "title": "Sales Stage", "type": "status"},
                {"id": "probability", "title": "Win Probability", "type": "text"},
                {"id": "owner", "title": "Owner", "type": "person"}
            ]
        }
        
        return deals_items, deals_schema
    
    @staticmethod
    def generate_sample_work_orders() -> tuple:
        """Generate sample work orders data"""
        orders_items = [
            {
                "id": "wo_001",
                "name": "Acme Corp - Onboarding",
                "created_at": "2024-01-15T09:00:00Z",
                "updated_at": "2024-02-08T10:30:00Z",
                "column_values": [
                    {"id": "status", "text": "In Progress"},
                    {"id": "priority", "text": "High"},
                    {"id": "start_date", "text": "2024-02-01"},
                    {"id": "target_date", "text": "2024-03-01"},
                    {"id": "owner", "text": "Sarah Dev"}
                ]
            },
            {
                "id": "wo_002",
                "name": "API Integration Setup",
                "created_at": "2024-02-01T11:15:00Z",
                "updated_at": "2024-02-09T09:00:00Z",
                "column_values": [
                    {"id": "status", "text": "Done"},
                    {"id": "priority", "text": "Medium"},
                    {"id": "start_date", "text": "2024-02-01"},
                    {"id": "target_date", "text": "2024-02-15"},
                    {"id": "owner", "text": "John Dev"}
                ]
            },
            {
                "id": "wo_003",
                "name": "Global Industries - Implementation",
                "created_at": "2024-02-02T14:20:00Z",
                "updated_at": "2024-02-08T16:45:00Z",
                "column_values": [
                    {"id": "status", "text": "In Progress"},
                    {"id": "priority", "text": "High"},
                    {"id": "start_date", "text": "2024-02-05"},
                    {"id": "target_date", "text": "2024-03-15"},
                    {"id": "owner", "text": "Sarah Dev"}
                ]
            },
            {
                "id": "wo_004",
                "name": "Data Migration Project",
                "created_at": "2024-02-03T08:00:00Z",
                "updated_at": "2024-02-06T13:30:00Z",
                "column_values": [
                    {"id": "status", "text": "Blocked"},
                    {"id": "priority", "text": "High"},
                    {"id": "start_date", "text": "2024-02-10"},
                    {"id": "target_date", "text": "2024-03-10"},
                    {"id": "owner", "text": "Mike Dev"}
                ]
            },
            {
                "id": "wo_005",
                "name": "Documentation Update",
                "created_at": "2024-02-04T10:00:00Z",
                "updated_at": "2024-02-07T11:00:00Z",
                "column_values": [
                    {"id": "status", "text": "In Backlog"},
                    {"id": "priority", "text": "Low"},
                    {"id": "start_date", "text": "2024-03-01"},
                    {"id": "target_date", "text": "2024-03-30"},
                    {"id": "owner", "text": "Alice Dev"}
                ]
            }
        ]
        
        orders_schema = {
            "id": "board_orders",
            "name": "Work Orders (Sample)",
            "columns": [
                {"id": "name", "title": "Order Name", "type": "text"},
                {"id": "status", "title": "Status", "type": "status"},
                {"id": "priority", "title": "Priority", "type": "status"},
                {"id": "start_date", "title": "Start Date", "type": "date"},
                {"id": "target_date", "title": "Target Date", "type": "date"},
                {"id": "owner", "title": "Owner", "type": "person"}
            ]
        }
        
        return orders_items, orders_schema


class DemoMode:
    """Demo mode for testing without API credentials"""
    
    def __init__(self):
        """Initialize demo mode"""
        self.generator = SampleDataGenerator()
    
    def run_demo_analysis(self):
        """Run demo analysis"""
        from data_processor import DataProcessor
        from insight_engine import InsightEngine
        
        processor = DataProcessor()
        engine = InsightEngine()
        
        print("\n" + "="*80)
        print("BUSINESS INTELLIGENCE AGENT - DEMO MODE")
        print("="*80)
        
        # Generate sample data
        print("\n🔄 Loading sample data...")
        deals_items, deals_schema = self.generator.generate_sample_deals()
        orders_items, orders_schema = self.generator.generate_sample_work_orders()
        
        # Process deals
        print("\n📊 SALES PIPELINE ANALYSIS")
        print("-"*80)
        deals_df = processor.items_to_dataframe(deals_items, deals_schema)
        deals_analysis = engine.analyze_deals_pipeline(deals_df)
        
        print(f"Total Deals: {deals_analysis['total_deals']}")
        print(f"Pipeline Value: ${deals_analysis['value_metrics'].get('total_value', 0):,.0f}")
        print(f"Average Deal Size: ${deals_analysis['value_metrics'].get('average_deal_size', 0):,.0f}")
        
        if deals_analysis['by_status']:
            print("\nStatus Distribution:")
            for status, info in deals_analysis['by_status'].items():
                print(f"  • {status}: {info['count']} ({info['percentage']}%)")
        
        # Process work orders
        print("\n\n📋 PROJECT EXECUTION STATUS")
        print("-"*80)
        orders_df = processor.items_to_dataframe(orders_items, orders_schema)
        orders_analysis = engine.analyze_work_orders(orders_df)
        
        print(f"Total Orders: {orders_analysis['total_orders']}")
        
        if orders_analysis['by_status']:
            print("\nStatus Distribution:")
            for status, count in orders_analysis['by_status'].items():
                pct = (count['count'] / orders_analysis['total_orders']) * 100
                print(f"  • {status}: {count['count']} ({pct:.0f}%)")
        
        # Generate insights
        print("\n\n💡 STRATEGIC INSIGHTS")
        print("-"*80)
        insights = engine.generate_recommendations(deals_analysis, orders_analysis, {})
        for insight in insights:
            print(f"  {insight}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    demo = DemoMode()
    demo.run_demo_analysis()
