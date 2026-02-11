"""
Business Intelligence Agent - Streamlit Frontend
Beautiful web interface for the BI Agent
"""

import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from dotenv import load_dotenv
from bi_agent import BusinessIntelligenceAgent

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stColumns {
        gap: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .insight-box {
        background-color: #e8f4f8;
        color: #1a3a52;
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #1f77b4;
    }
    .summary-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        font-size: 1.3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load environment
load_dotenv()


def initialize_agent():
    """Initialize the BI Agent with Groq AI support"""
    api_key = st.session_state.get("api_key") or os.getenv("MONDAY_API_KEY")
    deals_board_id = st.session_state.get("deals_board_id") or os.getenv("DEALS_BOARD_ID")
    work_orders_board_id = st.session_state.get("work_orders_board_id") or os.getenv("WORK_ORDERS_BOARD_ID")
    groq_api_key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    
    if not all([api_key, deals_board_id, work_orders_board_id]):
        return None
    
    # Initialize with optional Groq key
    agent = BusinessIntelligenceAgent(api_key, deals_board_id, work_orders_board_id, groq_api_key)
    return agent


def get_relevant_charts(question: str, metrics: Dict) -> List[str]:
    """
    Determine which charts are most relevant to the question asked
    
    Args:
        question: User's question
        metrics: Available metrics dictionary
        
    Returns:
        List of chart types to display
    """
    question_lower = question.lower()
    charts = []
    
    # Status-related questions
    if any(word in question_lower for word in ["status", "progress", "how are", "distribution"]):
        if metrics.get("by_status"):
            charts.append("status")
    
    # Priority-related questions
    if any(word in question_lower for word in ["priority", "urgent", "critical", "severity"]):
        if metrics.get("by_priority"):
            charts.append("priority")
    
    # Stage/Pipeline questions
    if any(word in question_lower for word in ["stage", "pipeline", "funnel", "stuck", "negotiation"]):
        if metrics.get("by_stage"):
            charts.append("stage")
    
    # Win rate questions
    if any(word in question_lower for word in ["win rate", "winning", "success", "won", "closed"]):
        if metrics.get("win_rate", 0) > 0:
            charts.append("win_rate")
    
    # Value/Financial questions
    if any(word in question_lower for word in ["value", "revenue", "financial", "size", "average", "total", "deal value"]):
        if metrics.get("value_metrics"):
            charts.append("value")
    
    # Work order/Execution questions
    if any(word in question_lower for word in ["work order", "project", "execution", "completion", "active", "delay"]):
        if metrics.get("by_status"):
            charts.append("status")
        if metrics.get("by_priority"):
            charts.append("priority")
    
    # If no specific charts detected, show relevant ones
    if not charts:
        if metrics.get("by_status"):
            charts.append("status")
        if metrics.get("win_rate", 0) > 0:
            charts.append("win_rate")
        if metrics.get("value_metrics"):
            charts.append("value")
    
    return charts


def render_status_chart(metrics: Dict):
    """Render status distribution chart"""
    by_status = metrics.get("by_status", {})
    if by_status:
        try:
            status_data = []
            for status, info in by_status.items():
                status_data.append({
                    "Status": str(status),
                    "Count": info.get("count", 0),
                    "Percentage": info.get("percentage", 0)
                })
            
            if status_data:
                df_status = pd.DataFrame(status_data)
                fig = px.pie(
                    df_status,
                    values="Count",
                    names="Status",
                    title="📊 Status Distribution",
                    hole=0.4
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create status chart: {e}")


def render_priority_chart(metrics: Dict):
    """Render priority distribution chart"""
    by_priority = metrics.get("by_priority", {})
    if by_priority:
        try:
            priority_data = []
            for priority, count in by_priority.items():
                priority_data.append({
                    "Priority": str(priority),
                    "Count": int(count)
                })
            
            if priority_data:
                df_priority = pd.DataFrame(priority_data)
                fig = px.bar(
                    df_priority,
                    x="Priority",
                    y="Count",
                    title="🎯 Priority Distribution",
                    color="Count",
                    color_continuous_scale="Reds"
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create priority chart: {e}")


def render_stage_chart(metrics: Dict):
    """Render pipeline stage chart"""
    by_stage = metrics.get("by_stage", {})
    if by_stage:
        try:
            stage_data = []
            for stage, info in by_stage.items():
                stage_data.append({
                    "Stage": str(stage),
                    "Count": info.get("count", 0),
                    "Percentage": info.get("percentage", 0)
                })
            
            if stage_data:
                df_stage = pd.DataFrame(stage_data)
                fig = px.bar(
                    df_stage,
                    x="Stage",
                    y="Count",
                    title="📈 Pipeline by Stage",
                    color="Percentage",
                    color_continuous_scale="Blues"
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Stage distribution chart not available")


def render_win_rate_chart(metrics: Dict):
    """Render win rate gauge chart"""
    win_rate = metrics.get("win_rate", 0)
    if win_rate > 0:
        try:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=win_rate,
                title={"text": "🏆 Win Rate %"},
                delta={"reference": 28},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 20], "color": "#ff6b6b"},
                        {"range": [20, 50], "color": "#ffd43b"},
                        {"range": [50, 100], "color": "#51cf66"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 28
                    }
                }
            ))
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Win rate gauge not available")


def render_value_chart(metrics: Dict):
    """Render value metrics chart"""
    value_metrics = metrics.get("value_metrics", {})
    if value_metrics and any(value_metrics.values()):
        try:
            value_data = []
            for key, val in value_metrics.items():
                if isinstance(val, (int, float)) and val > 0:
                    value_data.append({
                        "Metric": key.replace("_", " ").title(),
                        "Value": float(val)
                    })
            
            if value_data:
                df_value = pd.DataFrame(value_data)
                df_value = df_value.sort_values("Value", ascending=False).head(5)
                fig = px.bar(
                    df_value,
                    x="Metric",
                    y="Value",
                    title="💰 Value Metrics",
                    color="Value",
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(height=450, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create value chart: {e}")


def display_result(response):
    """Display the analysis result in a beautiful format"""
    
    if response.get("status") == "error":
        st.error(f"❌ Error: {response.get('error', 'Could not process question')}")
        return
    
    # Show AI status badge
    if response.get("ai_powered"):
        st.success("🤖 **AI-Powered Analysis** - Insights powered by Groq AI")
    
    # Executive Summary
    if response.get("executive_summary"):
        st.markdown(f"""
        <div class="summary-header">
            📊 {response['executive_summary']}
        </div>
        """, unsafe_allow_html=True)
    
    # Display details table if this is a details query
    if response.get("is_details_query") and response.get("details_table") is not None:
        st.subheader("📋 Details Table")
        st.dataframe(response["details_table"], use_container_width=True)
        st.divider()
    
    # Key Metrics - Vertical Display
    if response.get("key_metrics"):
        st.subheader("📈 Key Metrics")
        metrics = response["key_metrics"]
        
        # Filter for numeric and simple values
        numeric_metrics = [(k, v) for k, v in metrics.items() 
                         if isinstance(v, (int, float)) and not isinstance(v, bool)]
        dict_metrics = [(k, v) for k, v in metrics.items() 
                       if isinstance(v, dict)]
        
        # Display numeric metrics in 3-column grid
        if numeric_metrics:
            # Prioritize win_rate if it exists
            priority_metrics = []
            other_metrics = []
            
            for k, v in numeric_metrics:
                if k in ["win_rate", "total_deals", "total_orders", "total_value"]:
                    priority_metrics.append((k, v))
                else:
                    other_metrics.append((k, v))
            
            ordered_metrics = priority_metrics + other_metrics
            
            cols = st.columns(3)
            for idx, (key, value) in enumerate(ordered_metrics[:6]):
                with cols[idx % 3]:
                    # Format specific metrics
                    if key == "win_rate":
                        st.metric(key, f"{value}%")
                    elif "value" in key.lower() and isinstance(value, (int, float)) and value > 100:
                        st.metric(key, f"${value:,.0f}")
                    elif "percentage" in key.lower() or key.endswith("_pct"):
                        st.metric(key, f"{value}%")
                    else:
                        st.metric(key, value)
        
        # Display dict metrics as tables
        if dict_metrics:
            st.divider()
            for key, value_dict in dict_metrics:
                if value_dict:  # Only show if not empty
                    with st.expander(f"📊 {key.replace('_', ' ').title()}"):
                        # Convert to DataFrame for better display
                        try:
                            df = pd.DataFrame([
                                {"Category": k, "Count": v.get("count") if isinstance(v, dict) else v, 
                                 "Percentage": f"{v.get('percentage', 0)}%" if isinstance(v, dict) else ""}
                                for k, v in value_dict.items()
                            ])
                            st.dataframe(df, use_container_width=True)
                        except:
                            st.markdown(f"```\n{value_dict}\n```")
    
    st.divider()
    
    # Insights - Vertical Display
    if response.get("insights"):
        st.subheader("💡 Insights & Recommendations")
        for insight in response["insights"]:
            st.markdown(f"""
            <div class="insight-box">
                {insight}
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Dynamic Visualizations - Charts relevant to the question asked
    metrics = response.get("key_metrics", {})
    question = response.get("question", "")
    
    # Get relevant charts for this question
    relevant_charts = get_relevant_charts(question, metrics)
    
    if relevant_charts:
        st.subheader("📊 Data Visualizations (Related to Your Question)")
        
        # Arrange charts in 2-column layout
        cols = st.columns(2)
        col_idx = 0
        
        for chart_type in relevant_charts:
            with cols[col_idx % 2]:
                if chart_type == "status":
                    render_status_chart(metrics)
                elif chart_type == "priority":
                    render_priority_chart(metrics)
                elif chart_type == "stage":
                    render_stage_chart(metrics)
                elif chart_type == "win_rate":
                    render_win_rate_chart(metrics)
                elif chart_type == "value":
                    render_value_chart(metrics)
            
            col_idx += 1
        
        # Move to new row if odd number of charts
        if col_idx % 2 == 1:
            st.empty()
    
    # Data Used
    if response.get("data_used"):
        with st.expander("📋 Data Sources Used"):
            st.write("This analysis uses data from:")
            for source in response["data_used"]:
                st.write(f"• {source}")


def main():
    # Header
    st.markdown("# 📊 Business Intelligence Agent")
    st.markdown("Ask questions about your **sales pipeline** and **project execution**")
    
    # Auto-initialize agent on startup
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
        st.session_state.load_attempted = False
    
    # Attempt to load data on first run
    if not st.session_state.load_attempted:
        st.session_state.load_attempted = True
        
        with st.spinner("🔄 Connecting to monday.com and loading data..."):
            agent = initialize_agent()
            if agent is None:
                st.error("❌ Missing credentials in .env file. Please configure MONDAY_API_KEY, DEALS_BOARD_ID, and WORK_ORDERS_BOARD_ID")
                st.stop()
            
            if agent.refresh_data():
                st.session_state.agent = agent
                st.session_state.agent_initialized = True
                
                # Show success banner
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.success(f"✅ Connected!")
                with col2:
                    st.info(f"📊 {len(agent.deals_data)} Deals")
                with col3:
                    st.info(f"📋 {len(agent.work_orders_data)} Orders")
                
                # Check Groq AI status
                if agent.groq_engine and agent.groq_engine.enabled:
                    st.success("🤖 AI-Powered Groq Engine ENABLED")
                else:
                    st.warning("ℹ️ Groq AI not enabled - using standard analysis")
                
                st.divider()
            else:
                st.error("❌ Failed to connect to monday.com. Check your API key and board IDs in .env")
                st.stop()
    
    # Main content
    st.markdown("### 🤔 Ask Your Question")
    st.markdown("Examples: *'What is our sales pipeline status?'*, *'Show me owner details'*, *'How are work orders progressing?'*")
    
    # Question input
    question = st.text_area(
        label="Your Question",
        placeholder="Ask any question about your deals, work orders, or business health...",
        height=100,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ask_button = st.button("🔍 Ask Question", use_container_width=True)
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            with st.spinner("Refreshing data..."):
                if st.session_state.agent.refresh_data():
                    st.success("✅ Data refreshed!")
                else:
                    st.error("❌ Failed to refresh data")
    
    with col3:
        if st.button("⚙️ Reset", use_container_width=True):
            st.session_state.agent_initialized = False
            st.session_state.load_attempted = False
            st.rerun()
    
    # Process question
    if ask_button and question:
        with st.spinner("Analyzing your question..."):
            response = st.session_state.agent.ask_question(question)
            st.session_state.last_response = response
        
        st.divider()
        display_result(response)
    
    elif ask_button and not question:
        st.warning("⚠️ Please enter a question first!")
    
    # Show example questions
    if "last_response" not in st.session_state:
        st.divider()
        st.markdown("### 📚 Example Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Sales Pipeline:**
            - What is our current sales pipeline worth?
            - What's our win rate?
            - What is the average deal size?
            - Show me deals by stage
            """)
        
        with col2:
            st.markdown("""
            **Project Execution:**
            - How are work orders progressing?
            - What are potential bottlenecks?
            - Show completion rates
            - What projects are at risk?
            """)


if __name__ == "__main__":
    main()
