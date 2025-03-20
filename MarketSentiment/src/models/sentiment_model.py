from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import nltk
import os
from datetime import datetime, timedelta

# Set a specific directory for NLTK data
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download VADER lexicon
nltk.download('vader_lexicon', quiet=True, download_dir=nltk_data_dir)

class SentimentModel:
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
    
    def analyze_ticker_news_sentiment(self, news_df, days_back=5):
        """Process sentiment for news data"""
        if news_df.empty:
            return {
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
            'avg_sentiment': avg_sentiment,
            'sentiment_category': sentiment_category,
            'bullish_count': sentiment_counts.get('Bullish', 0),
            'neutral_count': sentiment_counts.get('Neutral', 0),
            'bearish_count': sentiment_counts.get('Bearish', 0),
            'news_count': len(filtered_df),
            'sentiment_strength': sentiment_strength,
            'investment_score': investment_score,
            'news_details': filtered_df.to_dict('records')
        }
        
        return results