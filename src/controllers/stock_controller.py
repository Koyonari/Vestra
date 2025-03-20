from flask import Blueprint, jsonify, request, send_from_directory
from model.stock_model import StockModel
from model.sentiment_model import SentimentModel
from view.scraper_service import ScraperService
from utils.data_utils import DataUtils
import os
import pandas as pd
import json

# Initialize models and services
stock_model = StockModel()
sentiment_model = SentimentModel()
scraper_service = ScraperService()
data_utils = DataUtils()

# Create Blueprint for stock routes
stock_routes = Blueprint('stocks', __name__)

@stock_routes.route('/top', methods=['GET'])
def get_top_stocks():
    """Get top stocks by market cap"""
    limit = request.args.get('limit', default=100, type=int)
    
    top_stocks = stock_model.get_top_100_stocks()
    
    if limit and limit < len(top_stocks):
        top_stocks = top_stocks.head(limit)
    
    return jsonify({
        'stocks': top_stocks.to_dict('records')
    })

@stock_routes.route('/price', methods=['GET'])
def get_stock_price():
    """Get historical price data for a stock"""
    ticker = request.args.get('ticker')
    days = request.args.get('days', default=90, type=int)
    
    if not ticker:
        return jsonify({'error': 'No ticker provided'}), 400
    
    price_data = stock_model.get_stock_price_data(ticker, days)
    
    if price_data is None or price_data.empty:
        return jsonify({'error': f'No price data found for {ticker}'}), 404
    
    # Convert DataFrame to dict for JSON serialization
    price_dict = {
        'dates': [date.strftime('%Y-%m-%d') for date in price_data.index],
        'prices': price_data['Close'].tolist(),
        'volumes': price_data['Volume'].tolist() if 'Volume' in price_data.columns else []
    }
    
    return jsonify({
        'ticker': ticker,
        'price_data': price_dict
    })

@stock_routes.route('/predict', methods=['GET'])
def predict_stock():
    """Predict stock trend based on historical data and sentiment"""
    ticker = request.args.get('ticker')
    days = request.args.get('days', default=90, type=int)
    
    if not ticker:
        return jsonify({'error': 'No ticker provided'}), 400
    
    # Get price data
    price_data = stock_model.get_stock_price_data(ticker, days)
    
    if price_data is None or price_data.empty:
        return jsonify({'error': f'No price data found for {ticker}'}), 404
    
    # Get news and analyze sentiment
    finviz_df = scraper_service.scrape_finviz_news(ticker)
    yahoo_df = scraper_service.scrape_yahoo_finance_news(ticker)
    news_df = pd.concat([finviz_df, yahoo_df]).reset_index(drop=True)
    
    sentiment_results = sentiment_model.analyze_ticker_news_sentiment(news_df)
    avg_sentiment = sentiment_results['avg_sentiment']
    
    # Generate prediction
    prediction_data = stock_model.predict_stock_trend(price_data, avg_sentiment)
    
    if prediction_data is None:
        return jsonify({'error': 'Could not generate prediction'}), 500
    
    # Format prediction data for JSON
    prediction_dict = {
        'dates': [date.strftime('%Y-%m-%d') for date in prediction_data.index],
        'prices': prediction_data['Price'].tolist(),
        'upper_bound': [price * 1.10 for price in prediction_data['Price'].tolist()],
        'lower_bound': [price * 0.90 for price in prediction_data['Price'].tolist()]
    }
    
    return jsonify({
        'ticker': ticker,
        'sentiment': avg_sentiment,
        'prediction': prediction_dict
    })

@stock_routes.route('/analyze-all', methods=['GET'])
def analyze_all_stocks():
    """Analyze all top stocks and generate rankings"""
    limit = request.args.get('limit', default=50, type=int)
    
    # Get top stocks
    top_stocks = stock_model.get_top_100_stocks()
    
    if limit and limit < len(top_stocks):
        top_stocks = top_stocks.head(limit)
    
    results = []
    stock_data_list = top_stocks.to_dict('records')
    
    for stock_data in stock_data_list:
        ticker = stock_data['ticker']
        name = stock_data['name']
        
        # Get news and analyze sentiment
        finviz_df = scraper_service.scrape_finviz_news(ticker)
        yahoo_df = scraper_service.scrape_yahoo_finance_news(ticker)
        news_df = pd.concat([finviz_df, yahoo_df]).reset_index(drop=True)
        
        sentiment_results = sentiment_model.analyze_ticker_news_sentiment(news_df)
        
        # Add ticker and name to results
        sentiment_results['ticker'] = ticker
        sentiment_results['name'] = name
        
        # Get price data
        price_data = stock_model.get_stock_price_data(ticker)
        
        if price_data is not None and not price_data.empty:
            # Generate prediction
            prediction_data = stock_model.predict_stock_trend(
                price_data, 
                sentiment_results['avg_sentiment']
            )
            
            # Export data to JSON
            if prediction_data is not None:
                data_utils.export_stock_data_to_json(
                    ticker,
                    name,
                    price_data,
                    prediction_data,
                    sentiment_results['avg_sentiment'],
                    sentiment_results['investment_score']
                )
        
        results.append(sentiment_results)
    
    # Rank stocks and create report
    ranked_stocks = stock_model.rank_stocks_by_investment_potential(results)
    data_utils.generate_master_stocks_json(ranked_stocks)
    
    return jsonify({
        'message': 'Analysis complete',
        'stocks_analyzed': len(results),
        'top_stocks': ranked_stocks.head(10).to_dict('records')
    })

@stock_routes.route('/data/<path:filename>', methods=['GET'])
def get_stock_data(filename):
    """Serve stock data JSON files"""
    try:
        return send_from_directory('stock_data', filename)
    except Exception as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 404

@stock_routes.route('/master', methods=['GET'])
def get_master_data():
    """Get the master stocks data"""
    try:
        with open('stock_data/master_stocks.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Could not load master data: {str(e)}'}), 500
