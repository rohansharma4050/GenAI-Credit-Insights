"""
GenAI Query Handler for Credit Card Analytics
Provides natural language insights about customer behavior and risk
"""

import os
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta


class GenAIInsightsHandler:
    """Handle GenAI queries and generate insights about customer data"""
    
    def __init__(self, use_openai: bool = False):
        """
        Initialize GenAI handler
        
        Args:
            use_openai: If True, use OpenAI API (requires OPENAI_API_KEY env var)
                       If False, use rule-based insights
        """
        self.use_openai = use_openai
        
        if use_openai:
            try:
                import openai
                self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except ImportError:
                print("OpenAI package not installed. Falling back to rule-based insights.")
                self.use_openai = False
            except Exception as e:
                print(f"Error initializing OpenAI: {e}. Falling back to rule-based insights.")
                self.use_openai = False
    
    def generate_customer_context(self, customer_data: Dict, 
                                  transactions: pd.DataFrame) -> str:
        """Generate context summary for GenAI prompts"""
        
        # Calculate time-based metrics
        recent_date = transactions['date'].max()
        last_30d = transactions[transactions['date'] >= (recent_date - timedelta(days=30))]
        last_90d = transactions[transactions['date'] >= (recent_date - timedelta(days=90))]
        prev_90d = transactions[
            (transactions['date'] >= (recent_date - timedelta(days=180))) &
            (transactions['date'] < (recent_date - timedelta(days=90)))
        ]
        
        # Category breakdown
        category_spend = last_90d.groupby('category')['amount'].sum().sort_values(ascending=False)
        top_categories = category_spend.head(3)
        
        # Trend analysis
        current_spend = last_90d['amount'].sum()
        previous_spend = prev_90d['amount'].sum()
        spend_change = ((current_spend - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        
        context = f"""
Customer Profile:
- Customer ID: {customer_data['customer_id']}
- Segment: {customer_data['segment']}
- Credit Limit: ${customer_data['credit_limit']:,.2f}
- Member Since: {customer_data['member_since'].strftime('%Y-%m-%d')}

Risk Assessment:
- Risk Score: {customer_data['risk_score']}/100
- Risk Category: {customer_data['risk_category']}
- Utilization: {customer_data['utilization']:.1f}%

Recent Activity (Last 90 Days):
- Total Spend: ${current_spend:,.2f}
- Transaction Count: {len(last_90d)}
- Average Transaction: ${last_90d['amount'].mean():.2f}
- Spend Change vs Previous 90 Days: {spend_change:+.1f}%

Top Spending Categories:
{chr(10).join([f"- {cat}: ${amt:,.2f}" for cat, amt in top_categories.items()])}

Behavioral Flags:
- Foreign Transactions (90d): {last_90d['is_foreign'].sum()}
- Large Transactions >$1000 (90d): {(last_90d['amount'] > 1000).sum()}
- Online Transactions (90d): {last_90d['is_online'].sum()}
"""
        return context
    
    def query_with_openai(self, question: str, context: str) -> str:
        """Query OpenAI with customer context"""
        system_prompt = """You are a financial analyst specializing in credit card customer behavior and risk assessment. 
Provide clear, actionable insights based on the customer data provided. Focus on:
- Identifying patterns and trends
- Explaining risk factors
- Suggesting potential actions
- Using financial and analytical terminology appropriately

Keep responses concise but insightful (2-4 paragraphs)."""

        user_prompt = f"""Customer Data Context:
{context}

Question: {question}

Provide a detailed analytical response."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error querying OpenAI: {str(e)}\n\nFalling back to rule-based insights..."
    
    def generate_rule_based_insight(self, question: str, customer_data: Dict,
                                   transactions: pd.DataFrame) -> str:
        """Generate insights using rule-based logic"""
        question_lower = question.lower()
        
        # Analyze question type
        if any(word in question_lower for word in ['risk', 'score', 'increased', 'rise', 'high']):
            return self._explain_risk(customer_data, transactions)
        elif any(word in question_lower for word in ['spend', 'spending', 'purchases', 'buying']):
            return self._explain_spending(customer_data, transactions)
        elif any(word in question_lower for word in ['category', 'categories', 'what', 'where']):
            return self._explain_categories(customer_data, transactions)
        elif any(word in question_lower for word in ['trend', 'pattern', 'behavior', 'change']):
            return self._explain_trends(customer_data, transactions)
        else:
            return self._general_summary(customer_data, transactions)
    
    def _explain_risk(self, customer_data: Dict, transactions: pd.DataFrame) -> str:
        """Explain risk score factors"""
        risk_score = customer_data['risk_score']
        risk_category = customer_data['risk_category']
        utilization = customer_data['utilization']
        
        recent_date = transactions['date'].max()
        last_90d = transactions[transactions['date'] >= (recent_date - timedelta(days=90))]
        
        insights = [f"**Risk Analysis: {risk_category} Risk ({risk_score}/100)**\n"]
        
        # Utilization factor
        if utilization > 80:
            insights.append(f"**High Utilization Alert**: Credit utilization is at {utilization:.1f}%, "
                          "significantly above the recommended 30% threshold. This is the primary driver of the elevated risk score.")
        elif utilization > 50:
            insights.append(f"**Moderate Utilization**: Current utilization of {utilization:.1f}% is elevated. "
                          "While manageable, this contributes to the risk assessment.")
        else:
            insights.append(f"**Healthy Utilization**: Credit utilization of {utilization:.1f}% is well-managed.")
        
        # Foreign transactions
        foreign_count = last_90d['is_foreign'].sum()
        if foreign_count > 5:
            insights.append(f"\n**International Activity**: {foreign_count} foreign transactions in the last 90 days. "
                          "While this may indicate travel patterns, it adds complexity to fraud detection algorithms.")
        
        # Large transactions
        large_txns = (last_90d['amount'] > 1000).sum()
        if large_txns > 3:
            insights.append(f"\n**Large Transaction Pattern**: {large_txns} transactions over $1,000. "
                          "High-value purchases increase exposure and slightly elevate risk metrics.")
        
        # Quarterly comparison
        prev_90d = transactions[
            (transactions['date'] >= (recent_date - timedelta(days=180))) &
            (transactions['date'] < (recent_date - timedelta(days=90)))
        ]
        current_spend = last_90d['amount'].sum()
        previous_spend = prev_90d['amount'].sum()
        
        if previous_spend > 0:
            change = ((current_spend - previous_spend) / previous_spend) * 100
            if abs(change) > 30:
                insights.append(f"\n**Spending Velocity Change**: Spending has {('increased' if change > 0 else 'decreased')} "
                              f"by {abs(change):.1f}% compared to the previous quarter. Significant changes in spending "
                              "patterns can trigger risk model adjustments.")
        
        insights.append(f"\n**Recommendation**: " + (
            "Consider credit limit review or payment plan options." if risk_score > 60
            else "Monitor for continued pattern stability." if risk_score > 30
            else "Customer exhibits low-risk behavior profile."
        ))
        
        return "\n".join(insights)
    
    def _explain_spending(self, customer_data: Dict, transactions: pd.DataFrame) -> str:
        """Explain spending patterns"""
        recent_date = transactions['date'].max()
        last_90d = transactions[transactions['date'] >= (recent_date - timedelta(days=90))]
        
        total_spend = last_90d['amount'].sum()
        avg_txn = last_90d['amount'].mean()
        txn_count = len(last_90d)
        
        category_spend = last_90d.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        insights = [f"**Spending Analysis: ${total_spend:,.2f} (Last 90 Days)**\n"]
        insights.append(f"This customer has made {txn_count} transactions with an average value of ${avg_txn:.2f}.\n")
        
        insights.append("**Top Spending Categories:**")
        for i, (cat, amount) in enumerate(category_spend.head(3).items(), 1):
            pct = (amount / total_spend) * 100
            insights.append(f"{i}. **{cat}**: ${amount:,.2f} ({pct:.1f}% of total)")
        
        # Identify if premium customer
        if customer_data['segment'] == 'Premium':
            insights.append("\n**Premium Cardholder**: Spending patterns align with premium segment expectations, "
                          "with emphasis on travel and dining categories typically associated with rewards optimization.")
        
        return "\n".join(insights)
    
    def _explain_categories(self, customer_data: Dict, transactions: pd.DataFrame) -> str:
        """Explain category breakdown"""
        recent_date = transactions['date'].max()
        last_90d = transactions[transactions['date'] >= (recent_date - timedelta(days=90))]
        
        category_breakdown = last_90d.groupby('category').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        category_breakdown.columns = ['total', 'count', 'avg']
        category_breakdown = category_breakdown.sort_values('total', ascending=False)
        
        insights = ["**Category Spending Breakdown (Last 90 Days)**\n"]
        
        for cat, row in category_breakdown.iterrows():
            insights.append(f"**{cat}**: ${row['total']:,.2f} across {int(row['count'])} transactions "
                          f"(avg: ${row['avg']:.2f})")
        
        return "\n".join(insights)
    
    def _explain_trends(self, customer_data: Dict, transactions: pd.DataFrame) -> str:
        """Explain behavioral trends"""
        # Monthly trend
        transactions_copy = transactions.copy()
        transactions_copy['month'] = pd.to_datetime(transactions_copy['date']).dt.to_period('M')
        monthly = transactions_copy.groupby('month')['amount'].sum().tail(6)
        
        insights = ["**Behavioral Trends Analysis**\n"]
        insights.append("**Monthly Spending Trend:**")
        
        for month, amount in monthly.items():
            insights.append(f"- {month}: ${amount:,.2f}")
        
        # Calculate trend
        if len(monthly) >= 2:
            recent_avg = monthly.tail(2).mean()
            older_avg = monthly.head(2).mean()
            if recent_avg > older_avg * 1.2:
                insights.append("\n**Trend: Increasing** - Spending has accelerated in recent months.")
            elif recent_avg < older_avg * 0.8:
                insights.append("\n**Trend: Decreasing** - Spending has declined in recent months.")
            else:
                insights.append("\n**Trend: Stable** - Spending patterns remain consistent.")
        
        return "\n".join(insights)
    
    def _general_summary(self, customer_data: Dict, transactions: pd.DataFrame) -> str:
        """General customer summary"""
        return f"""**Customer Summary for {customer_data['customer_id']}**

**Profile:**
- Segment: {customer_data['segment']}
- Risk Level: {customer_data['risk_category']} ({customer_data['risk_score']}/100)
- Credit Utilization: {customer_data['utilization']:.1f}%

**Recent Activity:**
- 90-Day Spend: ${customer_data['total_spend_3m']:,.2f}
- Average Transaction: ${customer_data['avg_transaction']:.2f}

This customer demonstrates {'elevated risk factors requiring monitoring' if customer_data['risk_score'] > 60 else 'stable behavior patterns' if customer_data['risk_score'] > 30 else 'low-risk characteristics'}.
"""
    
    def answer_query(self, question: str, customer_data: Dict, 
                    transactions: pd.DataFrame) -> str:
        """
        Answer a natural language query about customer data
        
        Args:
            question: Natural language question
            customer_data: Customer profile dictionary
            transactions: Transaction DataFrame
            
        Returns:
            Generated insight/answer
        """
        context = self.generate_customer_context(customer_data, transactions)
        
        if self.use_openai:
            try:
                return self.query_with_openai(question, context)
            except:
                pass
        
        # Fallback to rule-based
        return self.generate_rule_based_insight(question, customer_data, transactions)


# Predefined query templates for quick access
SAMPLE_QUERIES = [
    "Why did this customer's risk score rise in Q2?",
    "What are the main spending patterns for this customer?",
    "Is this customer at risk of default?",
    "What categories does this customer spend the most on?",
    "How has spending behavior changed over time?",
    "Should we offer this customer a credit limit increase?",
    "What are the fraud risk indicators for this customer?",
]
