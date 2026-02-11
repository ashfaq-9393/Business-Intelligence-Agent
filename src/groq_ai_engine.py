"""
Groq AI Engine Module
Generates advanced business insights using Groq AI (llama2 70b)
"""

import logging
from typing import Dict, Any, Optional, List
from groq import Groq

logger = logging.getLogger(__name__)


class GroqAIEngine:
    """
    Generates advanced business insights using Groq AI
    Uses fast llama2-70b model for executive-level recommendations
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Groq AI Engine
        
        Args:
            api_key: Groq API key
        """
        if not api_key:
            logger.warning("⚠️ Groq API key not provided. AI insights disabled.")
            self.client = None
            self.enabled = False
            return
        
        try:
            self.client = Groq(api_key=api_key)
            self.enabled = True
            logger.info("✅ Groq AI Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq: {e}")
            self.client = None
            self.enabled = False
    
    def generate_executive_summary(self, metrics: Dict[str, Any], question: str) -> str:
        """
        Generate an AI-powered executive summary
        Resilient to messy data and handles any business question
        
        Args:
            metrics: Analysis metrics
            question: Original business question
            
        Returns:
            AI-generated executive summary
        """
        if not self.enabled or not self.client:
            return "Standard analysis (AI not enabled)"
        
        try:
            metrics_text = self._format_metrics(metrics)
            
            prompt = f"""You are a senior business analyst. Provide a SHORT executive summary (2-3 sentences) answering this specific question:

Question: {question}

Available Metrics & Data:
{metrics_text}

INSTRUCTIONS:
- Answer the EXACT question asked
- Use specific numbers and percentages
- Be direct and business-focused
- If data is incomplete, work with what you have
- Maximum 3 sentences
- Include actionable insight if possible

Example formats:
- "Our win rate is 24.86% (86 of 346 deals won). This is below industry average of 28%. Recommend reviewing qualification criteria."
- "76% of our active work orders are on track. 2 high-priority items showing delays. Recommend immediate intervention."

Summary:"""
            
            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=150,
                temperature=0.2
            )
            
            summary = message.choices[0].message.content.strip()
            return summary if summary else "Analysis complete - review metrics below"
        
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return "Data analysis complete - review metrics below"
    
    def generate_insights(self, metrics: Dict[str, Any], data_issues: Dict[str, Any]) -> List[str]:
        """
        Generate AI-powered business insights and recommendations
        Resilient to messy data
        
        Args:
            metrics: Analysis metrics
            data_issues: Data quality issues
            
        Returns:
            List of insights
        """
        if not self.enabled or not self.client:
            # Return smart defaults if AI not available
            return self._generate_default_insights(metrics)
        
        try:
            metrics_text = self._format_metrics(metrics)
            issues_text = self._format_data_issues(data_issues)
            
            prompt = f"""You are a business analyst. Generate 3 specific, actionable insights based on this data.

Metrics:
{metrics_text}

Data Quality:
{issues_text}

RULES:
- Focus on what the numbers tell us
- Be specific with numbers and percentages
- Identify patterns, risks, opportunities
- Acknowledge data limitations without dwelling on them
- Format: Start each with • or > bullet point

Insights:"""
            
            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=350,
                temperature=0.3
            )
            
            response_text = message.choices[0].message.content.strip()
            insights = [line.strip() for line in response_text.split('\n') if line.strip() and (line.strip().startswith('•') or line.strip().startswith('>'))]
            
            # If we got insights, return them
            if insights:
                return insights
            
            # Fallback to defaults if parsing failed
            return self._generate_default_insights(metrics)
        
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            # Graceful fallback to smart defaults
            return self._generate_default_insights(metrics)
    
    def analyze_question(self, question: str, context: str) -> Dict[str, Any]:
        """
        Analyze a business question with AI
        
        Args:
            question: Business question
            context: Context about the business
            
        Returns:
            Analysis with recommendations
        """
        if not self.enabled or not self.client:
            return {"error": "AI analysis unavailable. Please provide GROQ_API_KEY."}
        
        try:
            prompt = f"""
You are a business analyst. Answer this business question concisely.

Question: {question}
Context: {context}

Provide:
1. Direct answer (1 sentence)
2. Key factors to consider (3-4 bullet points)
3. Recommended actions (2-3 bullet points)
"""
            
            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=500,
                temperature=0.4
            )
            
            analysis = message.choices[0].message.content.strip()
            
            return {
                "status": "success",
                "analysis": analysis
            }
        
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _format_metrics(metrics: Dict[str, Any]) -> str:
        """Format metrics for AI prompt - handles nested structures"""
        formatted = []
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                # Format numbers nicely
                if isinstance(value, float):
                    formatted.append(f"- {key}: {value:.2f}")
                else:
                    formatted.append(f"- {key}: {value}")
            elif isinstance(value, dict) and len(value) <= 5:
                # For small dicts, show key top items
                formatted.append(f"- {key}: {', '.join(str(v) for v in list(value.values())[:3])}")
            elif isinstance(value, (list, dict)) and value:
                # For complex structures, just show count
                formatted.append(f"- {key}: {len(value)} items")
        
        return "\n".join(formatted) if formatted else "No numeric metrics available"
    
    @staticmethod
    def _format_data_issues(issues: Dict[str, Any]) -> str:
        """Format data issues for AI prompt"""
        if not issues or not issues.get("missing_values"):
            return "No significant data quality issues"
        
        formatted = []
        for col, info in issues.get("missing_values", {}).items():
            if info.get("percentage", 0) > 10:
                formatted.append(f"- {col}: {info['percentage']}% missing")
        
        return "\n".join(formatted) if formatted else "No significant data quality issues"
    
    def _generate_default_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate smart default insights when AI is unavailable"""
        insights = []
        
        # Extract numeric metrics
        total = metrics.get("total_records", metrics.get("total_orders", metrics.get("total_deals", 0)))
        
        if total > 0:
            insights.append(f"📊 Total records tracked: {total}")
        
        # Look for status/completion metrics
        by_status = metrics.get("by_status", {})
        if by_status:
            for status, count in list(by_status.items())[:3]:
                # Handle case where count might be a dict or non-numeric
                if isinstance(count, dict):
                    count_val = count.get("total", count.get("count", 0))
                else:
                    count_val = count if isinstance(count, (int, float)) else 0
                pct = (count_val / total * 100) if total > 0 else 0
                insights.append(f"• {status}: {count_val} records ({pct:.1f}%)")
        
        # Look for stage/category breakdown
        by_stage = metrics.get("by_stage", {})
        if by_stage:
            insights.append(f"• Pipeline distributed across {len(by_stage)} stages/categories")
        
        # Value metrics
        value = metrics.get("value_metrics", {})
        if value.get("total_value"):
            insights.append(f"• Total value: ${value['total_value']:,.0f}")
        if value.get("average_size"):
            insights.append(f"• Average size: ${value['average_size']:,.0f}")
        
        return insights if insights else ["Data analysis complete - see metrics above"]


# Test the Groq connection
def test_groq_connection(api_key: str) -> bool:
    """Test if Groq connection works"""
    try:
        engine = GroqAIEngine(api_key)
        if not engine.enabled:
            return False
        
        # Simple test message
        message = engine.client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
            model="llama-3.1-8b-instant",
            max_tokens=10
        )
        
        logger.info(f"✅ Groq connection test passed: {message.choices[0].message.content}")
        return True
    except Exception as e:
        logger.error(f"❌ Groq connection test failed: {e}")
        return False
