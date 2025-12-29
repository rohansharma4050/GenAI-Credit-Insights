# 💳 GenAI Credit Card Analytics

A professional, AI-powered Streamlit dashboard for credit card customer insights and risk assessment. This application provides consulting-grade analytics with GenAI-powered natural language querying capabilities.

## 🎯 Features

### 📊 Customer Overview
- **Summary Metrics**: Credit limit, utilization, spending patterns
- **Risk Assessment**: AI-driven risk scoring (High/Medium/Low)
- **Customer Segmentation**: Premium, Standard, and Basic tiers
- **Real-time KPIs**: 90-day spend, average transactions, behavioral flags

### 🧾 Transaction Analytics
- **Interactive Transaction Table**: Filterable by category, amount, date
- **Category Breakdown**: Visual spending analysis by merchant category
- **Trend Analysis**: Monthly and quarterly spending patterns
- **Behavioral Insights**: Day-of-week patterns, online vs in-store

### 🤖 GenAI Query Interface
Ask natural language questions about any customer:
- "Why did this customer's risk score rise in Q2?"
- "What are the main spending patterns for this customer?"
- "Is this customer at risk of default?"
- "Should we offer this customer a credit limit increase?"

**Two Modes:**
1. **AI-Powered** (with OpenAI API): Advanced natural language understanding
2. **Rule-Based** (default): Smart pattern-based insights without API requirements

### ⚠️ Risk Dashboard
- **Risk Score Gauge**: Visual 0-100 risk scoring
- **Risk Factors**: Foreign transactions, large purchases, utilization alerts
- **Quarterly Comparison**: Track spending velocity and pattern changes
- **Fraud Indicators**: Behavioral anomaly detection

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd /Users/rohansharma/Desktop/PoC
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Configure OpenAI API** (for enhanced AI insights)
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   ```

5. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   - The dashboard will automatically open at `http://localhost:8501`
   - Or manually navigate to the URL shown in the terminal

## 📁 Project Structure

```
PoC/
├── app.py                  # Main Streamlit dashboard application
├── data_generator.py       # Synthetic credit card data generator
├── genai_handler.py        # GenAI query handler (OpenAI + rule-based)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔧 Components

### Data Generator (`data_generator.py`)
Generates realistic synthetic credit card data including:
- Customer profiles with credit limits and segments
- Transaction histories across 9+ merchant categories
- Risk metrics and behavioral patterns
- Quarterly and monthly aggregations

**Merchant Categories:**
- Dining, Travel, Shopping, Groceries
- Entertainment, Healthcare, Utilities
- Gas, and Other services

### GenAI Handler (`genai_handler.py`)
Intelligent query processing system:
- **OpenAI Integration**: GPT-4o-mini powered insights
- **Rule-Based Fallback**: Works without API keys
- **Context Generation**: Comprehensive customer profiling
- **Multi-topic Analysis**: Risk, spending, trends, categories

### Dashboard App (`app.py`)
Professional Streamlit interface with:
- Responsive multi-tab layout
- Interactive Plotly visualizations
- Real-time filtering and search
- Custom CSS styling for professional appearance

## 💡 Usage Examples

### Analyzing a High-Risk Customer

1. **Select Customer**: Use sidebar filters to find high-risk customers
2. **Review Overview**: Check utilization and spending metrics
3. **Ask GenAI**: "Why is this customer flagged as high risk?"
4. **Examine Transactions**: Filter for large or foreign transactions
5. **View Risk Dashboard**: Analyze quarterly trends

### Identifying Upsell Opportunities

1. **Filter**: Select "Premium" segment customers with low risk
2. **Query**: "Should we offer this customer a credit limit increase?"
3. **Review Spending**: Check category preferences for targeted offers
4. **Analyze Trends**: Confirm consistent payment behavior

### Fraud Detection

1. **Filter**: High-risk customers with recent spending spikes
2. **Query**: "What are the fraud risk indicators for this customer?"
3. **Check Flags**: Foreign transactions, unusual hours, velocity changes
4. **Review Details**: Examine suspicious transaction patterns

## ⚙️ Configuration

### OpenAI API (Optional)
To enable AI-powered insights:

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. Restart the dashboard

**Note**: The dashboard works perfectly fine without OpenAI using intelligent rule-based insights!

### Data Generation
Modify customer count in `app.py`:
```python
customers_df, transactions_df = load_data(num_customers=100)  # Adjust number
```

### Styling
Custom CSS is in `app.py` under the `st.markdown()` section. Modify colors, fonts, and layouts as needed.

## 📊 Data Model

### Customer Profile
- `customer_id`: Unique identifier
- `credit_limit`: $5K - $50K range
- `segment`: Premium/Standard/Basic
- `risk_score`: 0-100 composite score
- `utilization`: Credit usage percentage
- `member_since`: Account age

### Transaction Record
- `transaction_id`: Unique transaction reference
- `date`: Timestamp
- `merchant`: Business name
- `category`: Spending category
- `amount`: Transaction value
- `is_foreign`: International flag
- `is_online`: Digital purchase flag

## 🎨 Customization

### Adding New Merchant Categories
Edit `MERCHANT_CATEGORIES` in `data_generator.py`:
```python
MERCHANT_CATEGORIES = {
    'YourCategory': ['Merchant 1', 'Merchant 2'],
    ...
}
```

### Custom Risk Scoring
Modify `calculate_risk_metrics()` in `data_generator.py` to adjust risk factors and weights.

### New GenAI Queries
Add sample queries in `genai_handler.py`:
```python
SAMPLE_QUERIES = [
    "Your new question here",
    ...
]
```

## 🤝 Contributing

This is a Proof of Concept dashboard. Feel free to:
- Extend with real data connectors
- Add new visualization types
- Implement additional GenAI capabilities
- Enhance risk scoring algorithms

## 📝 License

This project is open source and available for modification and use.

## 🔒 Privacy & Security

- All data is **synthetically generated**
- No real customer information is used
- OpenAI API calls are made securely (if configured)
- API keys should never be committed to version control

## 📧 Support

For questions or issues:
1. Check the console for error messages
2. Verify all dependencies are installed
3. Ensure Python version compatibility
4. Review the `.env` configuration (if using OpenAI)

## 🚀 Next Steps

**Enhance the Dashboard:**
- Connect to real data sources (databases, APIs)
- Add user authentication
- Implement email alerts for high-risk customers
- Create exportable reports
- Add predictive modeling features

**Scale the Application:**
- Deploy to cloud (Streamlit Cloud, AWS, GCP)
- Add caching for large datasets
- Implement background data refresh
- Multi-tenant support

---

**Built with ❤️ using Streamlit, OpenAI, and Python**

*GenAI-powered analytics for modern credit card customer insights*
