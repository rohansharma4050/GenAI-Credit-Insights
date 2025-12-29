"""
Synthetic Credit Card Transaction Data Generator
Generates realistic customer profiles and transaction data for analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple


class CreditCardDataGenerator:
    """Generate synthetic credit card customer and transaction data"""
    
    MERCHANT_CATEGORIES = {
        'Dining': ['Fine Dining Restaurant', 'Coffee Shop', 'Fast Food', 'Bar & Lounge'],
        'Travel': ['Airline', 'Hotel', 'Car Rental', 'Travel Agency'],
        'Shopping': ['Department Store', 'Online Retailer', 'Boutique', 'Electronics Store'],
        'Groceries': ['Supermarket', 'Organic Market', 'Convenience Store'],
        'Entertainment': ['Streaming Service', 'Concert Venue', 'Movie Theater', 'Gaming'],
        'Healthcare': ['Pharmacy', 'Medical Clinic', 'Gym Membership'],
        'Utilities': ['Electric Company', 'Internet Provider', 'Phone Service'],
        'Gas': ['Gas Station', 'EV Charging Station'],
        'Other': ['Insurance', 'Subscription Service', 'Professional Services']
    }
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        
    def generate_customer_profile(self, customer_id: str) -> Dict:
        """Generate a single customer profile"""
        credit_limit = np.random.choice([5000, 10000, 15000, 25000, 50000], 
                                       p=[0.2, 0.3, 0.25, 0.15, 0.1])
        
        # Customer segments
        segment = np.random.choice(['Premium', 'Standard', 'Basic'], 
                                  p=[0.2, 0.5, 0.3])
        
        member_since = datetime.now() - timedelta(days=np.random.randint(365, 3650))
        
        return {
            'customer_id': customer_id,
            'credit_limit': credit_limit,
            'segment': segment,
            'member_since': member_since,
            'annual_fee': 0 if segment == 'Basic' else (95 if segment == 'Standard' else 550)
        }
    
    def generate_transactions(self, customer_profile: Dict, 
                            num_months: int = 6) -> pd.DataFrame:
        """Generate transaction history for a customer"""
        transactions = []
        customer_id = customer_profile['customer_id']
        credit_limit = customer_profile['credit_limit']
        segment = customer_profile['segment']
        
        # Spending patterns by segment
        if segment == 'Premium':
            avg_monthly_spend = credit_limit * 0.4
            travel_prob = 0.3
            dining_prob = 0.25
        elif segment == 'Standard':
            avg_monthly_spend = credit_limit * 0.25
            travel_prob = 0.15
            dining_prob = 0.15
        else:
            avg_monthly_spend = credit_limit * 0.15
            travel_prob = 0.05
            dining_prob = 0.10
        
        current_date = datetime.now()
        
        for month_offset in range(num_months):
            # Vary monthly spending with some randomness
            month_start = current_date - timedelta(days=30 * (num_months - month_offset))
            num_transactions = np.random.randint(10, 40)
            
            monthly_spend = avg_monthly_spend * np.random.uniform(0.7, 1.3)
            
            for _ in range(num_transactions):
                # Select category based on probabilities
                rand_val = random.random()
                if rand_val < travel_prob:
                    category = 'Travel'
                elif rand_val < travel_prob + dining_prob:
                    category = 'Dining'
                else:
                    category = random.choice(list(self.MERCHANT_CATEGORIES.keys()))
                
                merchant = random.choice(self.MERCHANT_CATEGORIES[category])
                
                # Transaction amount based on category
                if category == 'Travel':
                    amount = np.random.uniform(200, 2000)
                elif category == 'Dining':
                    amount = np.random.uniform(15, 300)
                elif category == 'Shopping':
                    amount = np.random.uniform(20, 800)
                elif category == 'Groceries':
                    amount = np.random.uniform(30, 200)
                else:
                    amount = np.random.uniform(10, 300)
                
                # Random transaction date within the month
                transaction_date = month_start + timedelta(
                    days=random.randint(0, 29),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                # Add some foreign transactions for risk scoring
                is_foreign = random.random() < 0.05
                
                transactions.append({
                    'customer_id': customer_id,
                    'transaction_id': f'TXN_{customer_id}_{len(transactions):05d}',
                    'date': transaction_date,
                    'category': category,
                    'merchant': merchant,
                    'amount': round(amount, 2),
                    'is_foreign': is_foreign,
                    'is_online': random.random() < 0.4
                })
        
        return pd.DataFrame(transactions)
    
    def calculate_risk_metrics(self, transactions: pd.DataFrame, 
                               customer_profile: Dict) -> Dict:
        """Calculate risk score and related metrics"""
        credit_limit = customer_profile['credit_limit']
        
        # Get last 3 months of data
        recent_date = transactions['date'].max()
        last_3m = transactions[transactions['date'] >= (recent_date - timedelta(days=90))]
        
        # Calculate metrics
        total_spend = last_3m['amount'].sum()
        utilization = (total_spend / (credit_limit * 3)) * 100
        
        # Risk factors
        foreign_transactions = last_3m['is_foreign'].sum()
        large_transactions = (last_3m['amount'] > 1000).sum()
        late_night_txns = sum(1 for d in last_3m['date'] if d.hour >= 23 or d.hour <= 5)
        
        # Calculate risk score (0-100)
        risk_score = 0
        risk_score += min(utilization * 0.3, 30)  # Utilization impact
        risk_score += foreign_transactions * 5  # Foreign transactions
        risk_score += large_transactions * 3  # Large transactions
        risk_score += late_night_txns * 2  # Unusual hours
        
        risk_score = min(risk_score, 100)
        
        # Risk category
        if risk_score < 30:
            risk_category = 'Low'
        elif risk_score < 60:
            risk_category = 'Medium'
        else:
            risk_category = 'High'
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_category': risk_category,
            'utilization': round(utilization, 1),
            'total_spend_3m': round(total_spend, 2),
            'foreign_txn_count': int(foreign_transactions),
            'large_txn_count': int(large_transactions),
            'avg_transaction': round(last_3m['amount'].mean(), 2)
        }
    
    def generate_complete_dataset(self, num_customers: int = 50) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate complete dataset with customers and transactions"""
        all_customers = []
        all_transactions = []
        
        for i in range(num_customers):
            customer_id = f'CUST_{i+1:05d}'
            
            # Generate customer profile
            profile = self.generate_customer_profile(customer_id)
            
            # Generate transactions
            transactions = self.generate_transactions(profile, num_months=6)
            
            # Calculate risk metrics
            risk_metrics = self.calculate_risk_metrics(transactions, profile)
            
            # Combine customer data
            customer_data = {**profile, **risk_metrics}
            all_customers.append(customer_data)
            all_transactions.append(transactions)
        
        customers_df = pd.DataFrame(all_customers)
        transactions_df = pd.concat(all_transactions, ignore_index=True)
        
        return customers_df, transactions_df


def get_quarterly_comparison(transactions: pd.DataFrame) -> pd.DataFrame:
    """Get quarterly spending comparison for risk analysis"""
    transactions = transactions.copy()
    transactions['quarter'] = pd.to_datetime(transactions['date']).dt.to_period('Q')
    
    quarterly = transactions.groupby('quarter').agg({
        'amount': ['sum', 'count', 'mean'],
        'is_foreign': 'sum'
    }).round(2)
    
    quarterly.columns = ['total_spend', 'transaction_count', 'avg_amount', 'foreign_count']
    return quarterly.reset_index()


if __name__ == "__main__":
    # Test the generator
    generator = CreditCardDataGenerator()
    customers, transactions = generator.generate_complete_dataset(num_customers=10)
    
    print("Generated Customers:")
    print(customers.head())
    print("\nGenerated Transactions:")
    print(transactions.head())
    print(f"\nTotal Customers: {len(customers)}")
    print(f"Total Transactions: {len(transactions)}")
