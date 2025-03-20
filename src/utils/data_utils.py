import json
import os
from datetime import datetime
import pandas as pd

class DataUtils:
    @staticmethod
    def export_stock_data_to_json(ticker, name, price_data, prediction_data, sentiment_score, investment_score):
        """Export stock data to JSON for Vue component consumption"""
        if price_data is None or prediction_data is None:
            print(f"Not enough data to export for {ticker}")
            return
        
        try:
            # Create historical price data
            historical_data = []
            for date, row in price_data.iterrows():
                historical_data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "price": round(row['Close'], 2)
                })
            
            # Create prediction data
            prediction_series = []
            for date, price in prediction_data.iterrows():
                prediction_series.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "price": round(price['Price'], 2)
                })
            
            # Create upper and lower bounds for prediction uncertainty
            upper_bound = []
            lower_bound = []
            for date, price in prediction_data.iterrows():
                upper_bound.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "price": round(price['Price'] * 1.10, 2)  # 10% upper bound
                })
                lower_bound.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "price": round(price['Price'] * 0.90, 2)  # 10% lower bound
                })
            
            # Prepare sentiment category
            sentiment_category = 'Bullish' if sentiment_score > 0.05 else ('Bearish' if sentiment_score < -0.05 else 'Neutral')
            
            # Create JSON data structure
            json_data = {
                "ticker": ticker,
                "name": name,
                "sentiment": {
                    "score": round(sentiment_score, 2),
                    "category": sentiment_category,
                    "investment_score": round(investment_score, 1)
                },
                "historical_data": historical_data,
                "prediction": {
                    "data": prediction_series,
                    "upper_bound": upper_bound,
                    "lower_bound": lower_bound
                },
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save JSON file
            os.makedirs('stock_data', exist_ok=True)
            json_path = os.path.join('stock_data', f'{ticker}_data.json')
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"✓ Successfully exported JSON data for {ticker}")
            
        except Exception as e:
            print(f"Error exporting JSON data for {ticker}: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def generate_master_stocks_json(ranked_stocks):
        """Generate a master JSON file with all analyzed stocks"""
        try:
            stocks_list = []
            
            for _, row in ranked_stocks.iterrows():
                ticker = row['ticker']
                stock_data = {
                    "ticker": ticker,
                    "name": row['name'],
                    "investment_score": round(row['investment_score'], 1),
                    "sentiment_category": row['sentiment_category'],
                    "sentiment_score": round(row['avg_sentiment'], 2),
                    "rank": int(row['rank']),
                    "data_file": f"{ticker}_data.json"
                }
                stocks_list.append(stock_data)
            
            # Create master JSON
            master_data = {
                "stocks": stocks_list,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save master JSON
            os.makedirs('stock_data', exist_ok=True)
            with open('stock_data/master_stocks.json', 'w') as f:
                json.dump(master_data, f, indent=2)
                
            print("✓ Successfully generated master stocks JSON file")
            
        except Exception as e:
            print(f"Error generating master stocks JSON: {e}")