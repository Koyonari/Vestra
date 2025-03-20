from flask import Blueprint, jsonify, request
from model.sentiment_model import SentimentModel
from view.scraper_service import ScraperService
import pandas as pd

# Initialize sentiment model and scraper service
sentiment_model = SentimentModel()
scraper_service = ScraperService()

# Create Blueprint for sentiment routes
sentiment_routes = Blueprint('sentiment', __name__)

@sentiment_routes.route('/analyze', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment for a given text"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    sentiment_scores = sentiment_model.analyze_sentiment(text)
    category = sentiment_model.categorize_sentiment(sentiment_scores['compound'])
    
    return jsonify({
        'sentiment': sentiment_scores,
        'category': category
    })

@sentiment_routes.route('/analyze-ticker', methods=['GET'])
def analyze_ticker_sentiment():
    """Analyze sentiment for a specific ticker"""
    ticker = request.args.get('ticker')
    
    if not ticker:
        return jsonify({'error': 'No ticker provided'}), 400
    
    # Get news from multiple sources
    finviz_df = scraper_service.scrape_finviz_news(ticker)
    yahoo_df = scraper_service.scrape_yahoo_finance_news(ticker)
    
    # Combine news from different sources
    news_df = pd.concat([finviz_df, yahoo_df]).reset_index(drop=True)
    
    if news_df.empty:
        return jsonify({
            'error': f'No news found for {ticker}',
            'sentiment': {
                'avg_sentiment': 0,
                'sentiment_category': 'Neutral',
                'investment_score': 50
            }
        }), 404
    
    # Analyze sentiment
    sentiment_results = sentiment_model.analyze_ticker_news_sentiment(news_df)
    
    return jsonify({
        'ticker': ticker,
        'sentiment': sentiment_results
    })
