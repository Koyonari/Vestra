from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from sentiment_analyzer import StockSentimentAnalyzer
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for your Vue.js frontend

# Initialize the analyzer
analyzer = StockSentimentAnalyzer()

@app.route('/api/top-stocks', methods=['GET'])
def get_top_stocks():
    """Get list of top stocks by market cap"""
    try:
        max_stocks = int(request.args.get('limit', 100))
        stocks = analyzer.get_top_100_stocks()
        
        if len(stocks) > max_stocks:
            stocks = stocks.head(max_stocks)
            
        # Convert to dict for JSON response
        result = stocks.to_dict('records')
        return jsonify({"stocks": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-ticker', methods=['GET'])
def analyze_ticker():
    """Analyze sentiment for a specific ticker"""
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker symbol required"}), 400
    
    try:
        # Create stock data dictionary
        stock_data = {
            'ticker': ticker,
            'name': ticker  # Will be updated by the analyzer
        }
        
        # Analyze sentiment
        sentiment_results = analyzer.analyze_ticker_sentiment(stock_data)
        
        # Get price data
        price_data = analyzer.get_stock_price_data(ticker)
        
        # Only generate prediction if we have price data
        prediction_data = None
        if price_data is not None and not price_data.empty:
            prediction_data = analyzer.predict_stock_trend(
                price_data, 
                sentiment_results['avg_sentiment']
            )
            
            # Visualize stock with prediction
            if prediction_data is not None:
                analyzer.visualize_stock_prediction(
                    ticker,
                    sentiment_results['name'],
                    price_data,
                    prediction_data,
                    sentiment_results['avg_sentiment'],
                    sentiment_results['investment_score']
                )
        
        # Convert price data to list for JSON
        price_history = None
        if price_data is not None and not price_data.empty:
            price_history = price_data.reset_index().to_dict('records')
        
        # Convert prediction data to list for JSON
        prediction = None
        if prediction_data is not None and not prediction_data.empty:
            prediction = prediction_data.reset_index().to_dict('records')
        
        # Add to response
        response = {
            "sentiment": sentiment_results,
            "price_history": price_history,
            "prediction": prediction
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stock-chart/<ticker>', methods=['GET'])
def get_stock_chart(ticker):
    """Return the generated chart for a ticker"""
    try:
        chart_path = f'stock_charts/{ticker}_prediction.png'
        if os.path.exists(chart_path):
            return send_file(chart_path, mimetype='image/png')
        else:
            return jsonify({"error": "Chart not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-rankings', methods=['GET'])
def get_top_rankings():
    """Return the current rankings of stocks"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # Check if we have a CSV file with rankings
        if os.path.exists('reports/investment_ranking.csv'):
            df = pd.read_csv('reports/investment_ranking.csv')
            top_stocks = df.head(limit).to_dict('records')
            return jsonify({"rankings": top_stocks})
        else:
            # Generate new rankings
            max_stocks = int(request.args.get('max_stocks', 20))
            ranked_stocks = analyzer.analyze_top_stocks(max_stocks=max_stocks)
            top_stocks = ranked_stocks.head(limit).to_dict('records')
            return jsonify({"rankings": top_stocks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-batch', methods=['POST'])
def analyze_batch():
    """Analyze a batch of stocks"""
    data = request.json
    tickers = data.get('tickers', [])
    
    if not tickers:
        return jsonify({"error": "No tickers provided"}), 400
    
    try:
        results = []
        for ticker in tickers:
            stock_data = {'ticker': ticker, 'name': ticker}
            result = analyzer.analyze_ticker_sentiment(stock_data)
            results.append(result)
        
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/full-report', methods=['GET'])
def get_full_report():
    """Return the full markdown report if available"""
    try:
        if os.path.exists('reports/investment_ranking_report.md'):
            with open('reports/investment_ranking_report.md', 'r') as f:
                report = f.read()
            return jsonify({"report": report})
        else:
            return jsonify({"error": "Report not generated yet"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-report', methods=['GET'])
def generate_report():
    """Generate a new investment report"""
    try:
        max_stocks = int(request.args.get('max_stocks', 20))
        ranked_stocks = analyzer.analyze_top_stocks(max_stocks=max_stocks)
        
        if os.path.exists('reports/investment_ranking_report.md'):
            with open('reports/investment_ranking_report.md', 'r') as f:
                report = f.read()
            
            return jsonify({
                "message": "Report generated successfully",
                "report": report,
                "top_picks": ranked_stocks.head(5).to_dict('records')
            })
        else:
            return jsonify({"error": "Failed to generate report"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('stock_charts', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)