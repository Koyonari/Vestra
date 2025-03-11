import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from datetime import datetime, timedelta
import time as time_module
import random
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import os
import matplotlib

# Set a specific directory for NLTK data
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
# Set matplotlib to use the 'Agg' backend (non-interactive)
# This prevents the "main thread is not in main loop" error
matplotlib.use('TkAgg')

# Create directories for outputs
os.makedirs('stock_charts', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Download VADER lexicon
nltk.download('vader_lexicon', quiet=True, download_dir=nltk_data_dir)

class StockSentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        # Add finance-specific terms to the lexicon to improve accuracy
        self.sia.lexicon.update({
            'bullish': 3.0, 'bearish': -3.0,
            'outperform': 2.0, 'underperform': -2.0,
            'buy': 2.0, 'sell': -2.0,
            'upgrade': 2.5, 'downgrade': -2.5,
            'beat': 2.0, 'miss': -2.0,
            'exceeded': 2.0, 'fell short': -2.0,
            'growth': 1.5, 'decline': -1.5,
            'profit': 1.5, 'loss': -1.5,
            'positive': 1.0, 'negative': -1.0,
            'strong': 1.0, 'weak': -1.0,
            'surge': 2.0, 'plunge': -2.0,
            'rise': 1.0, 'fall': -1.0,
            'above': 1.0, 'below': -1.0,
            'higher': 1.0, 'lower': -1.0,
            'increase': 1.0, 'decrease': -1.0,
            'gain': 1.0, 'lose': -1.0,
            'success': 1.5, 'failure': -1.5,
            'promising': 1.0, 'disappointing': -1.0,
            'optimistic': 1.0, 'pessimistic': -1.0,
            'opportunity': 1.0, 'risk': -0.5,
            'recommend': 1.5, 'avoid': -1.5,
            'dividend': 1.0, 'debt': -0.5,
            'rally': 2.0, 'crash': -2.5,
            'breakthrough': 2.0, 'breakdown': -2.0,
            'outlook': 0.5, 'guidance': 0.5,
            'target': 0.5, 'estimate': 0.5
        })
        
    def get_random_user_agent(self):
        """Return a random user agent to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.184'
        ]
        return random.choice(user_agents)
    
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
                    time_module.sleep(0.5)
                
                results.extend(chunk_data)
                print(f"Processed {len(chunk)} stocks...")
                time_module.sleep(1)  # Pause between chunks
                
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
                
                time_module.sleep(0.5)
                
            fallback_df = pd.DataFrame(results)
            return fallback_df
    
    def scrape_finviz_news(self, ticker):
        """Scrape news headlines for a specific ticker from Finviz"""
        url = f'https://finviz.com/quote.ashx?t={ticker}'
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            # Add a delay to avoid being blocked
            time_module.sleep(random.uniform(1, 2))
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_table = soup.find(id='news-table')
            
            if not news_table:
                print(f"Warning: Could not find news table for {ticker} on Finviz")
                return pd.DataFrame()
                
            news_data = []
            for row in news_table.find_all('tr'):
                if not row.td:
                    continue
                    
                date_cell = row.td.text.strip().split() if row.td and row.td.text else ['', '']
                
                # Handle date format
                date_str = ''
                time_str = ''
                
                if len(date_cell) >= 1:
                    # Check if first element is a date or time
                    if ':' in date_cell[0]:  # It's a time
                        time_str = date_cell[0]
                        date_str = datetime.now().strftime('%m/%d/%y')
                    else:  # It's a date
                        date_str = date_cell[0]
                        if len(date_cell) >= 2:
                            time_str = date_cell[1]
                
                # Check if a tag exists before accessing it
                headline = row.a.text.strip() if row.a else "No headline"
                source = row.span.text.strip() if row.span else "Unknown"
                
                news_data.append([date_str, time_str, headline, source])
            
            df = pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
            
            return df
        
        except Exception as e:
            print(f"Error scraping {ticker} news from Finviz: {e}")
            return pd.DataFrame()
    
    def scrape_yahoo_finance_news(self, ticker):
        """Scrape news from Yahoo Finance for a specific ticker"""
        url = f'https://finance.yahoo.com/quote/{ticker}/news'
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        try:
            # Add a delay to avoid being blocked
            time_module.sleep(random.uniform(1, 2))
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('li.js-stream-content')
            
            news_data = []
            for item in news_items:
                headline_elem = item.select_one('h3')
                time_elem = item.select_one('span[data-reactid]')
                
                if headline_elem and time_elem:
                    headline = headline_elem.text.strip()
                    timestamp = time_elem.text.strip()
                    news_data.append([datetime.now().strftime('%m/%d/%y'), timestamp, headline, 'Yahoo Finance'])
            
            df = pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
            return df
        
        except Exception as e:
            print(f"Error scraping Yahoo Finance news for {ticker}: {e}")
            return pd.DataFrame()
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using VADER"""
        sentiment_scores = self.sia.polarity_scores(text)
        return sentiment_scores
    
    def categorize_sentiment(self, compound_score):
        """Categorize sentiment based on compound score"""
        if compound_score >= 0.3:
            return 'Bullish'
        elif compound_score <= -0.3:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def analyze_ticker_sentiment(self, ticker_data, days_back=5):
        """Analyze sentiment for a specific ticker"""
        ticker = ticker_data['ticker']
        name = ticker_data['name']
        
        print(f"Analyzing sentiment for {ticker} ({name})...")
        
        # Get news from multiple sources
        finviz_df = self.scrape_finviz_news(ticker)
        yahoo_df = self.scrape_yahoo_finance_news(ticker)
        
        # Combine news from different sources
        news_df = pd.concat([finviz_df, yahoo_df]).reset_index(drop=True)
        
        if news_df.empty:
            print(f"No news found for {ticker}")
            # Return a default neutral sentiment
            return {
                'ticker': ticker,
                'name': name,
                'avg_sentiment': 0,
                'sentiment_category': 'Neutral',
                'bullish_count': 0,
                'neutral_count': 1,
                'bearish_count': 0,
                'news_count': 0,
                'sentiment_strength': 0,
                'investment_score': 50  # Neutral score
            }
        
        # Add sentiment analysis
        news_df['sentiment'] = news_df['headline'].apply(self.analyze_sentiment)
        news_df['compound'] = news_df['sentiment'].apply(lambda x: x['compound'])
        news_df['category'] = news_df['compound'].apply(self.categorize_sentiment)
        
        # Convert date columns for filtering
        today = datetime.now()
        cutoff_date = today - timedelta(days=days_back)
        
        # Clean date formats and filter by recency
        def parse_date(row):
            try:
                if row['date'] == '' or (isinstance(row['date'], str) and 'ago' in row['date'].lower()):
                    return today
                
                if isinstance(row['date'], str) and '/' in row['date']:
                    parts = row['date'].split('/')
                    if len(parts) == 3:
                        month, day, year = parts
                        if len(year) == 2:
                            year = '20' + year
                        return datetime(int(year), int(month), int(day))
                elif isinstance(row['date'], str) and '-' in row['date']:
                    try:
                        return datetime.strptime(row['date'], '%b-%d-%y')
                    except:
                        try:
                            return datetime.strptime(row['date'], '%Y-%m-%d')
                        except:
                            return today
                else:
                    # For relative dates
                    if isinstance(row['date'], str) and row['date'].lower() == 'today':
                        return today
                    elif isinstance(row['date'], str) and row['date'].lower() == 'yesterday':
                        return today - timedelta(days=1)
                    else:
                        return today
            except Exception as e:
                print(f"Date parsing error: {e} for date: {row['date']}")
                return today
        
        news_df['parsed_date'] = news_df.apply(parse_date, axis=1)
        filtered_df = news_df[news_df['parsed_date'] >= cutoff_date]
        
        # If we have no news after filtering, use all available news
        if filtered_df.empty and not news_df.empty:
            filtered_df = news_df
        
        # Calculate overall sentiment
        avg_sentiment = filtered_df['compound'].mean()
        sentiment_category = self.categorize_sentiment(avg_sentiment)
        
        # Calculate sentiment strength (magnitude of sentiment)
        sentiment_strength = abs(avg_sentiment)
        
        # Count sentiment categories
        sentiment_counts = filtered_df['category'].value_counts()
        
        # Calculate an investment score (0-100)
        # Formula: base 50 + normalized sentiment * 50
        # Normalized sentiment: scale sentiment from -1 to 1 into 0 to 1
        normalized_sentiment = (avg_sentiment + 1) / 2
        investment_score = 50 + (normalized_sentiment - 0.5) * 100
        
        # Apply sentiment strength as a multiplier - strong sentiments have more impact
        investment_score = min(100, max(0, investment_score * (1 + sentiment_strength)))
        
        # Prepare results
        results = {
            'ticker': ticker,
            'name': name, 
            'avg_sentiment': avg_sentiment,
            'sentiment_category': sentiment_category,
            'bullish_count': sentiment_counts.get('Bullish', 0),
            'neutral_count': sentiment_counts.get('Neutral', 0),
            'bearish_count': sentiment_counts.get('Bearish', 0),
            'news_count': len(filtered_df),
            'sentiment_strength': sentiment_strength,
            'investment_score': investment_score,
            'news_details': filtered_df
        }
        
        return results
    
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
    
    def visualize_stock_prediction(self, ticker, name, price_data, prediction_data, sentiment_score, investment_score):
        """Create a visualization of stock price and prediction"""
        if price_data is None or prediction_data is None:
            print(f"Not enough data to visualize for {ticker}")
            return
        
        try:
            # Create a new figure for this visualization to avoid any shared state
            plt.figure(figsize=(14, 7))
            
            # Plot historical prices
            plt.plot(price_data.index, price_data['Close'], label='Historical Close Price', color='blue')
            
            # Plot prediction
            plt.plot(prediction_data.index, prediction_data['Price'], label='Predicted Price', color='red', linestyle='--')
            
            # Add shaded area for prediction uncertainty
            upper_bound = prediction_data['Price'] * 1.10  # 10% upper bound
            lower_bound = prediction_data['Price'] * 0.90  # 10% lower bound
            plt.fill_between(prediction_data.index, lower_bound, upper_bound, color='red', alpha=0.1)
            
            # Add vertical line for today
            today = datetime.now()
            plt.axvline(x=today, color='green', linestyle='-', alpha=0.5, label='Today')
            
            # Add title and labels
            sentiment_category = 'Bullish' if sentiment_score > 0.05 else ('Bearish' if sentiment_score < -0.05 else 'Neutral')
            title = f"{ticker} ({name}) - Price Prediction with {sentiment_category} Sentiment"
            plt.title(title, fontsize=16)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Price ($)', fontsize=12)
            
            # Add sentiment and investment score annotation
            sentiment_text = f"Sentiment Score: {sentiment_score:.2f} ({sentiment_category})"
            investment_text = f"Investment Score: {investment_score:.1f}/100"
            
            # Position the text
            plt.annotate(sentiment_text, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=12, 
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
            plt.annotate(investment_text, xy=(0.02, 0.12), xycoords='axes fraction', fontsize=12,
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
            
            # Add grid and legend
            plt.grid(True, alpha=0.3)
            plt.legend(loc='upper left')
            
            # Format date ticks
            plt.gcf().autofmt_xdate()
            
            # Add tight layout
            plt.tight_layout()
            
            # Save figure
            # Get the script's directory
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Create directories for outputs relative to the script location
            os.makedirs(os.path.join(script_dir, 'stock_charts'), exist_ok=True)
            os.makedirs(os.path.join(script_dir, 'reports'), exist_ok=True)

            # When saving files, use the full path
            plt.savefig(os.path.join(script_dir, f'stock_charts/{ticker}_prediction.png'))
            plt.close()
            
            print(f"✓ Successfully created chart for {ticker}")
            
        except Exception as e:
            print(f"Error visualizing prediction for {ticker}: {e}")
    
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
        
        # Add sector analysis
        report += "\n## Sector Analysis\n\n"
        
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
    
    def analyze_top_stocks(self, max_stocks=100, parallel_workers=10):
        """Analyze sentiment for top stocks and generate rankings"""
        # Get top stocks
        print("Getting list of top stocks by market cap...")
        top_stocks = self.get_top_100_stocks()
        
        if len(top_stocks) > max_stocks:
            top_stocks = top_stocks.head(max_stocks)
        
        print(f"Analyzing sentiment for {len(top_stocks)} stocks...")
        
        # Process stocks sequentially to avoid threading issues with matplotlib
        results = []
        stock_data_list = top_stocks.to_dict('records')
        
        for i, stock_data in enumerate(stock_data_list):
            try:
                ticker = stock_data['ticker']
                
                # Analyze sentiment
                sentiment_results = self.analyze_ticker_sentiment(stock_data)
                
                if sentiment_results:
                    # Get price data
                    price_data = self.get_stock_price_data(ticker)
                    
                    if price_data is not None and not price_data.empty:
                        # Generate prediction
                        prediction_data = self.predict_stock_trend(
                            price_data, 
                            sentiment_results['avg_sentiment']
                        )
                        
                        # Visualize stock with prediction
                        if prediction_data is not None:
                            self.visualize_stock_prediction(
                                ticker,
                                sentiment_results['name'],
                                price_data,
                                prediction_data,
                                sentiment_results['avg_sentiment'],
                                sentiment_results['investment_score']
                            )
                
                results.append(sentiment_results)
                print(f"Processed {i+1}/{len(stock_data_list)} stocks")
                
            except Exception as e:
                print(f"Error processing stock {ticker if 'ticker' in locals() else 'unknown'}: {e}")
        
        # Rank stocks and create report
        ranked_stocks = self.rank_stocks_by_investment_potential(results)
        
        print(f"Analysis complete. Results saved to 'reports/investment_ranking_report.md'")
        print("Top 5 investment opportunities:")
        print(ranked_stocks[['rank', 'ticker', 'name', 'investment_score', 'sentiment_category']].head())
        
        return ranked_stocks


# Main execution
if __name__ == "__main__":
    analyzer = StockSentimentAnalyzer()
    
    # You can adjust these parameters
    max_stocks = 100  # How many stocks to analyze (up to 100)
    parallel_workers = 10  # Number of parallel workers (adjust based on your machine)
    
    # Run the analysis
    ranked_stocks = analyzer.analyze_top_stocks(max_stocks=max_stocks, parallel_workers=parallel_workers)
    
    # The results will be saved to:
    # - reports/investment_ranking_report.md (main report with rankings)
    # - stock_charts/TICKER_prediction.png (individual stock charts with predictions)