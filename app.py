"""
Business Intelligence Agent - Streamlit Frontend
Beautiful web interface connecting to Backend API
"""

import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from typing import Dict, List
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .insight-box {
        background-color: #e8f4f8;
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


# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_api_health():
    """Check if backend API is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def analyze_question(question: str):
    """Send question to backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_relevant_charts(question: str, metrics: Dict) -> List[str]:
    """Determine which charts are relevant to the question"""
    question_lower = question.lower()
    charts = []
    
    if any(word in question_lower for word in ["status", "progress", "distribution"]):
        if metrics.get("by_status"):
            charts.append("status")
    
    if any(word in question_lower for word in ["priority", "urgent", "critical"]):
        if metrics.get("by_priority"):
            charts.append("priority")
    
    if any(word in question_lower for word in ["stage", "pipeline", "funnel"]):
        if metrics.get("by_stage"):
            charts.append("stage")
    
    if any(word in question_lower for word in ["win rate", "winning", "success"]):
        if metrics.get("win_rate", 0) > 0:
            charts.append("win_rate")
    
    if any(word in question_lower for word in ["value", "revenue", "financial"]):
        if metrics.get("value_metrics"):
            charts.append("value")
    
    if not charts:
        if metrics.get("by_status"):
            charts.append("status")
        if metrics.get("win_rate", 0) > 0:
            charts.append("win_rate")
    
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
                    "Count": info.get("count", 0)
                })
            
            if status_data:
                df = pd.DataFrame(status_data)
                fig = px.pie(df, values="Count", names="Status", title="📊 Status Distribution", hole=0.4)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Status chart unavailable")


def render_priority_chart(metrics: Dict):
    """Render priority distribution chart"""
    by_priority = metrics.get("by_priority", {})
    if by_priority:
        try:
            priority_data = [{"Priority": str(k), "Count": int(v)} for k, v in by_priority.items()]
            if priority_data:
                df = pd.DataFrame(priority_data)
                fig = px.bar(df, x="Priority", y="Count", title="🎯 Priority Distribution", color="Count", color_continuous_scale="Reds")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Priority chart unavailable")


def render_stage_chart(metrics: Dict):
    """Render pipeline stage chart"""
    by_stage = metrics.get("by_stage", {})
    if by_stage:
        try:
            stage_data = []
            for stage, info in by_stage.items():
                stage_data.append({"Stage": str(stage), "Count": info.get("count", 0)})
            
            if stage_data:
                df = pd.DataFrame(stage_data)
                fig = px.bar(df, x="Stage", y="Count", title="📈 Pipeline by Stage", color="Count", color_continuous_scale="Blues")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Stage chart unavailable")


def render_win_rate_chart(metrics: Dict):
    """Render win rate gauge"""
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
                    ]
                }
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Win rate chart unavailable")


def render_value_chart(metrics: Dict):
    """Render value metrics chart"""
    value_metrics = metrics.get("value_metrics", {})
    if value_metrics:
        try:
            value_data = [{"Metric": k.replace("_", " ").title(), "Value": float(v)} 
                         for k, v in value_metrics.items() if isinstance(v, (int, float)) and v > 0]
            
            if value_data:
                df = pd.DataFrame(value_data).sort_values("Value", ascending=False).head(5)
                fig = px.bar(df, x="Metric", y="Value", title="💰 Value Metrics", color="Value", color_continuous_scale="Viridis")
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Value chart unavailable")


def display_result(response):
    """Display analysis result"""
    
    if response.get("status") == "error":
        st.error(f"❌ Error: {response.get('error', 'Could not process')}")
        return
    
    # AI Status
    if response.get("ai_powered"):
        st.success("🤖 **AI-Powered Analysis** - Insights by Groq")
    
    # Executive Summary
    if response.get("executive_summary"):
        st.markdown(f"""
        <div class="summary-header">
            📊 {response['executive_summary']}
        </div>
        """, unsafe_allow_html=True)
    
    # Key Metrics
    if response.get("key_metrics"):
        st.subheader("📈 Key Metrics")
        metrics = response["key_metrics"]
        
        numeric_metrics = [(k, v) for k, v in metrics.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        
        if numeric_metrics:
            priority_metrics = [(k, v) for k, v in numeric_metrics if k in ["win_rate", "total_deals", "total_value"]]
            other_metrics = [(k, v) for k, v in numeric_metrics if k not in ["win_rate", "total_deals", "total_value"]]
            ordered = priority_metrics + other_metrics
            
            cols = st.columns(3)
            for idx, (key, value) in enumerate(ordered[:6]):
                with cols[idx % 3]:
                    if key == "win_rate":
                        st.metric(key, f"{value}%")
                    elif "value" in key.lower() and value > 100:
                        st.metric(key, f"${value:,.0f}")
                    else:
                        st.metric(key, value)
    
    st.divider()
    
    # Insights
    if response.get("insights"):
        st.subheader("💡 Insights & Recommendations")
        for insight in response["insights"]:
            st.markdown(f"""
            <div class="insight-box">
                {insight}
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Charts
    metrics = response.get("key_metrics", {})
    question = response.get("question", "")
    charts = get_relevant_charts(question, metrics)
    
    if charts:
        st.subheader("📊 Visualizations")
        cols = st.columns(2)
        col_idx = 0
        
        for chart_type in charts:
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


def main():
    st.markdown("# 📊 Business Intelligence Agent")
    st.markdown("Ask questions about your **sales pipeline** and **project execution**")
    
    # Check API health
    if not check_api_health():
        st.error(f"❌ Cannot connect to backend API at {BACKEND_URL}")
        st.info("Make sure the backend is running: `python api.py`")
        st.stop()
    
    st.success(f"✅ Connected to Backend API")
    st.divider()
    
    # Question input
    st.markdown("### 🤔 Ask Your Question")
    question = st.text_area(
        label="Your Question",
        placeholder="Ask about deals, work orders, or business metrics...",
        height=100,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ask_button = st.button("🔍 Analyze", use_container_width=True)
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            try:
                requests.post(f"{BACKEND_URL}/refresh", timeout=10)
                st.success("✅ Data refreshed!")
            except:
                st.error("Failed to refresh data")
    
    # Process question
    if ask_button and question:
        with st.spinner("Analyzing..."):
            response = analyze_question(question)
        
        st.divider()
        display_result(response)
    
    elif ask_button and not question:
        st.warning("⚠️ Please enter a question!")
    
    # Example questions
    if "last_response" not in st.session_state:
        st.divider()
        st.markdown("### 📚 Example Questions")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Sales Pipeline:**
            - What is our win rate?
            - Show me pipeline by stage
            - What's the average deal size?
            """)
        
        with col2:
            st.markdown("""
            **Project Execution:**
            - How are work orders progressing?
            - What projects are at risk?
            - Show me completion status
            """)


if __name__ == "__main__":
    main()
