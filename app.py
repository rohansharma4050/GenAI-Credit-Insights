"""
GenAI Credit Card Analytics
Professional GenAI-powered Streamlit dashboard for customer insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

from data_generator import CreditCardDataGenerator, get_quarterly_comparison
from genai_handler import GenAIInsightsHandler, SAMPLE_QUERIES


# Page configuration
st.set_page_config(
    page_title="GenAI Credit Card Analytics",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-high {
        background: linear-gradient(135deg, #f56565 0%, #c53030 100%);
    }
    .risk-medium {
        background: linear-gradient(135deg, #f6ad55 0%, #dd6b20 100%);
    }
    .risk-low {
        background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%);
    }
    .insight-box {
        background-color: #f9fafb;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #667eea;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #5568d3;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(num_customers=100):
    """Load or generate synthetic data"""
    generator = CreditCardDataGenerator(seed=42)
    customers_df, transactions_df = generator.generate_complete_dataset(num_customers)
    return customers_df, transactions_df


@st.cache_resource
def initialize_genai_handler():
    """Initialize GenAI handler (checks for OpenAI API key)"""
    use_openai = bool(os.getenv('OPENAI_API_KEY'))
    return GenAIInsightsHandler(use_openai=use_openai)


def render_customer_overview(customer_data, transactions):
    """Render customer overview section"""
    st.markdown("### Customer Overview")
    
    # Create 4 columns for key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Credit Limit",
            value=f"${customer_data['credit_limit']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="90-Day Spend",
            value=f"${customer_data['total_spend_3m']:,.2f}",
            delta=None
        )
    
    with col3:
        utilization = customer_data['utilization']
        st.metric(
            label="Utilization",
            value=f"{utilization:.1f}%",
            delta=f"{'High' if utilization > 70 else 'Normal'}",
            delta_color="inverse" if utilization > 70 else "off"
        )
    
    with col4:
        risk = customer_data['risk_category']
        st.metric(
            label="Risk Level",
            value=f"{risk}",
            delta=f"Score: {customer_data['risk_score']}/100"
        )
    
    # Customer details
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"**Customer ID:** {customer_data['customer_id']}")
    with col2:
        st.markdown(f"**Segment:** {customer_data['segment']}")
    with col3:
        st.markdown(f"**Member Since:** {customer_data['member_since'].strftime('%Y-%m-%d')}")
    with col4:
        st.markdown(f"**Annual Fee:** ${customer_data['annual_fee']}")


def render_spending_visualizations(transactions):
    """Render spending charts and visualizations"""
    st.markdown("### Spending Analytics")
    
    # Prepare data
    transactions = transactions.copy()
    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions['month'] = transactions['date'].dt.to_period('M').astype(str)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly spending trend
        monthly_spend = transactions.groupby('month')['amount'].sum().reset_index()
        monthly_spend.columns = ['Month', 'Total Spend']
        
        fig_trend = px.line(
            monthly_spend,
            x='Month',
            y='Total Spend',
            title='Monthly Spending Trend',
            markers=True
        )
        fig_trend.update_layout(
            plot_bgcolor='white',
            yaxis_title='Amount ($)',
            xaxis_title='Month'
        )
        fig_trend.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Category breakdown
        category_spend = transactions.groupby('category')['amount'].sum().reset_index()
        category_spend = category_spend.sort_values('amount', ascending=False)
        
        fig_category = px.pie(
            category_spend,
            values='amount',
            names='category',
            title='Spending by Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Transaction volume by day of week
    transactions['day_of_week'] = transactions['date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_spend = transactions.groupby('day_of_week')['amount'].sum().reindex(day_order).reset_index()
    
    fig_dow = px.bar(
        dow_spend,
        x='day_of_week',
        y='amount',
        title='Spending by Day of Week',
        color='amount',
        color_continuous_scale='Purples'
    )
    fig_dow.update_layout(
        plot_bgcolor='white',
        xaxis_title='Day of Week',
        yaxis_title='Total Spend ($)',
        showlegend=False
    )
    st.plotly_chart(fig_dow, use_container_width=True)


def render_transactions_table(transactions):
    """Render transactions table with filtering"""
    st.markdown("### Transaction History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(transactions['category'].unique().tolist())
        selected_category = st.selectbox('Category Filter', categories)
    
    with col2:
        min_amount = st.number_input('Min Amount ($)', min_value=0.0, value=0.0, step=10.0)
    
    with col3:
        max_amount = st.number_input('Max Amount ($)', min_value=0.0, value=10000.0, step=10.0)
    
    # Apply filters
    filtered_txns = transactions.copy()
    if selected_category != 'All':
        filtered_txns = filtered_txns[filtered_txns['category'] == selected_category]
    filtered_txns = filtered_txns[
        (filtered_txns['amount'] >= min_amount) & 
        (filtered_txns['amount'] <= max_amount)
    ]
    
    # Display table
    display_cols = ['date', 'merchant', 'category', 'amount', 'is_foreign', 'is_online']
    filtered_txns_display = filtered_txns[display_cols].copy()
    filtered_txns_display['date'] = pd.to_datetime(filtered_txns_display['date']).dt.strftime('%Y-%m-%d %H:%M')
    filtered_txns_display = filtered_txns_display.sort_values('date', ascending=False)
    filtered_txns_display['amount'] = filtered_txns_display['amount'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(
        filtered_txns_display,
        use_container_width=True,
        height=400,
        column_config={
            'date': 'Date',
            'merchant': 'Merchant',
            'category': 'Category',
            'amount': 'Amount',
            'is_foreign': st.column_config.CheckboxColumn('Foreign'),
            'is_online': st.column_config.CheckboxColumn('Online')
        }
    )
    
    st.caption(f"Showing {len(filtered_txns)} of {len(transactions)} transactions")


def render_genai_interface(customer_data, transactions, genai_handler):
    """Render GenAI query interface"""
    st.markdown("### GenAI Customer Insights")
    
    # Check if OpenAI is available
    if genai_handler.use_openai:
        st.success("OpenAI API connected - Enhanced AI insights enabled")
    else:
        st.info("Using rule-based insights (Set OPENAI_API_KEY environment variable for AI-powered analysis)")
    
    # Sample queries
    st.markdown("#### Quick Questions:")
    cols = st.columns(3)
    for i, query in enumerate(SAMPLE_QUERIES[:6]):
        with cols[i % 3]:
            if st.button(query, key=f"sample_{i}", use_container_width=True):
                st.session_state.current_query = query
    
    # Custom query input
    st.markdown("#### Ask Your Own Question:")
    user_query = st.text_area(
        "Type your question about this customer...",
        value=st.session_state.get('current_query', ''),
        height=100,
        placeholder="Example: Why is this customer's utilization high? What spending patterns are concerning?"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_button = st.button("Analyze", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.current_query = ''
            st.rerun()
    
    # Generate insights
    if analyze_button and user_query:
        with st.spinner("Generating insights..."):
            insight = genai_handler.answer_query(user_query, customer_data, transactions)
            
            st.markdown("#### Analysis Results:")
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
            
            # Save to session state
            if 'insight_history' not in st.session_state:
                st.session_state.insight_history = []
            st.session_state.insight_history.append({
                'query': user_query,
                'insight': insight,
                'timestamp': datetime.now()
            })


def render_risk_dashboard(customer_data, transactions):
    """Render risk assessment dashboard"""
    st.markdown("### Risk Assessment Dashboard")
    
    risk_score = customer_data['risk_score']
    risk_category = customer_data['risk_category']
    
    # Risk gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score", 'font': {'size': 24}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#48bb78'},
                {'range': [30, 60], 'color': '#f6ad55'},
                {'range': [60, 100], 'color': '#f56565'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk factors
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Foreign Transactions (90d)", customer_data['foreign_txn_count'])
    with col2:
        st.metric("Large Transactions (90d)", customer_data['large_txn_count'])
    with col3:
        avg_txn = customer_data['avg_transaction']
        st.metric("Avg Transaction", f"${avg_txn:,.2f}")


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<p class="main-header">GenAI Credit Card Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Customer Insights & Risk Assessment Platform</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ''
    
    # Load data
    with st.spinner("Loading customer data..."):
        customers_df, transactions_df = load_data(num_customers=100)
        genai_handler = initialize_genai_handler()
    
    # Sidebar - Customer selection
    st.sidebar.markdown("## Customer Selection")
    
    # Filter options
    segment_filter = st.sidebar.multiselect(
        "Segment",
        options=customers_df['segment'].unique(),
        default=customers_df['segment'].unique()
    )
    
    risk_filter = st.sidebar.multiselect(
        "Risk Level",
        options=['Low', 'Medium', 'High'],
        default=['Low', 'Medium', 'High']
    )
    
    # Apply filters
    filtered_customers = customers_df[
        (customers_df['segment'].isin(segment_filter)) &
        (customers_df['risk_category'].isin(risk_filter))
    ]
    
    # Customer selection
    customer_options = [
        f"{row['customer_id']} - {row['segment']} ({row['risk_category']} Risk)"
        for _, row in filtered_customers.iterrows()
    ]
    
    selected_customer_str = st.sidebar.selectbox(
        "Select Customer",
        customer_options,
        index=0 if customer_options else None
    )
    
    if selected_customer_str:
        # Extract customer ID
        selected_customer_id = selected_customer_str.split(' - ')[0]
        customer_data = customers_df[customers_df['customer_id'] == selected_customer_id].iloc[0].to_dict()
        customer_transactions = transactions_df[transactions_df['customer_id'] == selected_customer_id]
        
        # Sidebar stats
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Quick Stats")
        st.sidebar.metric("Total Customers", len(customers_df))
        st.sidebar.metric("High Risk Customers", len(customers_df[customers_df['risk_category'] == 'High']))
        st.sidebar.metric("Total Transactions", len(transactions_df))
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "Overview",
            "Transactions",
            "GenAI Insights",
            "Risk Analysis"
        ])
        
        with tab1:
            render_customer_overview(customer_data, customer_transactions)
            st.markdown("---")
            render_spending_visualizations(customer_transactions)
        
        with tab2:
            render_transactions_table(customer_transactions)
        
        with tab3:
            render_genai_interface(customer_data, customer_transactions, genai_handler)
        
        with tab4:
            render_risk_dashboard(customer_data, customer_transactions)
            st.markdown("---")
            
            # Quarterly comparison
            st.markdown("### Quarterly Analysis")
            quarterly_data = get_quarterly_comparison(customer_transactions)
            
            if not quarterly_data.empty:
                quarterly_data['quarter'] = quarterly_data['quarter'].astype(str)
                
                fig_quarterly = go.Figure()
                fig_quarterly.add_trace(go.Bar(
                    x=quarterly_data['quarter'],
                    y=quarterly_data['total_spend'],
                    name='Total Spend',
                    marker_color='#667eea'
                ))
                
                fig_quarterly.update_layout(
                    title='Quarterly Spending Comparison',
                    xaxis_title='Quarter',
                    yaxis_title='Total Spend ($)',
                    plot_bgcolor='white',
                    height=400
                )
                
                st.plotly_chart(fig_quarterly, use_container_width=True)
                
                # Show quarterly data table
                st.dataframe(quarterly_data, use_container_width=True)
    
    else:
        st.warning("No customers match the selected filters. Please adjust your filter criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #6b7280; font-size: 0.875rem;">'
        'GenAI Credit Card Analytics | Powered by Streamlit & AI Intelligence'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
