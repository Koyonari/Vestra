import pandas as pd
import numpy as np
import yfinance as yf
import os
import json
from datetime import datetime, timedelta

class StockModel:
    def __init__(self):
        pass
        
    def get_top_100_stocks(self):
        """Get the list of top 100 stocks by market cap"""
        try:
            # Use yfinance to get S&P 500 components as a starting point
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_table = pd.read_html(sp500_url)
            sp500_df = sp500_table[0]
            
            # Get tickers and get market cap data
            tickers = sp500_df['Symbol'].tolist()
            
            print(f"Fetching market cap data for {len(tickers)} stocks...")
            
            # Get market cap data in chunks to avoid overloading
            results = []
            chunk_size = 20
            ticker_chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
            
            for chunk in ticker_chunks:
                chunk_data = []
                for ticker in chunk:
                    try:
                        stock = yf.Ticker(ticker)
                        info = stock.info
                        market_cap = info.get('marketCap', 0)
                        name = info.get('shortName', ticker)
                        sector = info.get('sector', 'Unknown')
                        chunk_data.append({
                            'ticker': ticker,
                            'name': name,
                            'market_cap': market_cap,
                            'sector': sector
                        })
                    except Exception as e:
                        print(f"Error fetching data for {ticker}: {e}")
                    
                    # Be gentle with API requests
                    import time
                    time.sleep(0.5)
                
                results.extend(chunk_data)
                print(f"Processed {len(chunk)} stocks...")
                time.sleep(1)  # Pause between chunks
                
            # Convert to DataFrame and sort by market cap
            stocks_df = pd.DataFrame(results)
            stocks_df = stocks_df.sort_values('market_cap', ascending=False).reset_index(drop=True)
            
            # Take top 100
            top_100 = stocks_df.head(100)
            return top_100
        
        except Exception as e:
            print(f"Error getting top 100 stocks: {e}")
            # Fallback to a manual list of major stocks
            fallback_tickers = [
                "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "BRK-B", "JPM", "V",
                "JNJ", "UNH", "PG", "MA", "HD", "BAC", "XOM", "AVGO", "CVX", "COST",
                "ABBV", "MRK", "PEP", "KO", "LLY", "TMO", "CSCO", "ABT", "CRM", "MCD",
                "ACN", "WMT", "NKE", "DHR", "TXN", "UPS", "NEE", "PM", "ORCL", "IBM",
                "QCOM", "INTC", "NFLX", "ADBE", "AMD", "CMCSA", "HON", "PFE", "CAT", "UNP"
            ]
            
            results = []
            for ticker in fallback_tickers[:100]:  # Limit to top 50 in fallback
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    market_cap = info.get('marketCap', 0)
                    name = info.get('shortName', ticker)
                    sector = info.get('sector', 'Unknown')
                    results.append({
                        'ticker': ticker,
                        'name': name,
                        'market_cap': market_cap,
                        'sector': sector
                    })
                except Exception as e:
                    print(f"Error in fallback list for {ticker}: {e}")
                    results.append({
                        'ticker': ticker,
                        'name': ticker,
                        'market_cap': 0,
                        'sector': 'Unknown'
                    })
                
                time.sleep(0.5)
                
            fallback_df = pd.DataFrame(results)
            return fallback_df
    
    def get_stock_price_data(self, ticker, days=90):
        """Get historical stock price data using yfinance"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                print(f"No price data found for {ticker}")
                return None
                
            return hist
        except Exception as e:
            print(f"Error getting price data for {ticker}: {e}")
            return None
    
    def predict_stock_trend(self, price_data, sentiment_score):
        """Generate a simple prediction based on historical prices and sentiment"""
        if price_data is None or len(price_data) < 5:
            return None
        
        # Get the last closing price
        last_close = price_data['Close'].iloc[-1]
        
        # Calculate a simple moving average for the last 10 days
        # Handle case where there are fewer than 10 days of data
        short_ma = price_data['Close'].rolling(window=min(10, len(price_data))).mean().iloc[-1]
        
        # Calculate a simple moving average for the last 30 days
        # Handle case where there are fewer than 30 days of data
        long_ma = price_data['Close'].rolling(window=min(30, len(price_data))).mean().iloc[-1]
        
        # Calculate average daily price change over last 30 days
        avg_daily_change = price_data['Close'].pct_change().mean()
        
        # Convert sentiment to a price adjustment factor
        # Scale from -1 to 1 into a price multiplier (0.9 to 1.1)
        sentiment_factor = 1 + (sentiment_score / 10)
        
        # Get price momentum - compare recent vs longer-term average
        momentum = short_ma / long_ma - 1
        
        # Generate 30 days of predictions
        prediction_days = 30
        dates = pd.date_range(start=price_data.index[-1] + pd.Timedelta(days=1), periods=prediction_days)
        
        # Start with the last closing price
        predicted_prices = [last_close]
        
        # Generate future prices with a blend of momentum, average change and sentiment
        for i in range(1, prediction_days):
            # Calculate predicted change
            daily_change = (avg_daily_change + momentum/10) * sentiment_factor
            
            # Calculate next day's price based on previous predicted price
            next_price = predicted_prices[-1] * (1 + daily_change)
            
            # Add some random noise
            noise = np.random.normal(0, 0.005)  # 0.5% standard deviation
            next_price = next_price * (1 + noise)
            
            predicted_prices.append(next_price)
        
        prediction_df = pd.DataFrame({
            'Date': dates,
            'Price': predicted_prices
        })
        prediction_df.set_index('Date', inplace=True)
        
        return prediction_df
        
    def rank_stocks_by_investment_potential(self, results_list):
        """Rank stocks by investment potential and generate summary report"""
        # Create DataFrame from results
        columns = ['ticker', 'name', 'avg_sentiment', 'sentiment_category', 
                  'investment_score', 'news_count']
        
        data = []
        for result in results_list:
            if result:  # Skip None results
                row = [result.get(col, None) for col in columns]
                data.append(row)
        
        df = pd.DataFrame(data, columns=columns)
        
        # Sort by investment score (highest first)
        ranked_df = df.sort_values('investment_score', ascending=False).reset_index(drop=True)
        
        # Add rank column
        ranked_df['rank'] = ranked_df.index + 1
        
        # Prepare report
        report = "# Investment Potential Ranking Based on Sentiment Analysis\n\n"
        report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Add top 10 recommendations
        report += "## Top 10 Investment Recommendations\n\n"
        top10 = ranked_df.head(10)
        
        for i, row in top10.iterrows():
            report += f"{row['rank']}. **{row['ticker']}** ({row['name']})\n"
            report += f"   - Investment Score: {row['investment_score']:.1f}/100\n"
            report += f"   - Sentiment: {row['sentiment_category']} ({row['avg_sentiment']:.2f})\n"
            report += f"   - Based on {row['news_count']} news articles\n\n"
        
        # Add full ranking table
        report += "## Complete Ranking\n\n"
        
        # Convert DataFrame to Markdown table
        table_df = ranked_df[['rank', 'ticker', 'name', 'investment_score', 'sentiment_category', 'news_count']].copy()
        table_df['investment_score'] = table_df['investment_score'].round(1)
        
        # Create markdown table header
        table = "| Rank | Ticker | Company | Investment Score | Sentiment | News Count |\n"
        table += "|------|--------|---------|-----------------|-----------|------------|\n"
        
        # Add each row
        for _, row in table_df.iterrows():
            table += f"| {row['rank']} | {row['ticker']} | {row['name']} | {row['investment_score']} | {row['sentiment_category']} | {row['news_count']} |\n"
        
        report += table
        
        # Add methodology note
        report += "\n## Methodology\n\n"
        report += "This ranking is based on sentiment analysis of recent news articles for each stock. "
        report += "The investment score (0-100) combines sentiment analysis with price momentum indicators. "
        report += "A higher score suggests a more favorable investment opportunity based on current market sentiment and momentum.\n\n"
        report += "**Note**: This analysis should be used as one factor in investment decisions, not as a sole determining factor. "
        report += "Always conduct thorough research and consider consulting with a financial advisor before making investment decisions.\n"
        
        # Save report to file
        with open('reports/investment_ranking_report.md', 'w') as f:
            f.write(report)
            
        # Also save as CSV for easier data analysis
        ranked_df.to_csv('reports/investment_ranking.csv', index=False)
        
        return ranked_df