import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

class ScraperService:
    def __init__(self):
        pass
    
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
            time.sleep(random.uniform(1, 2))
            
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
                        from datetime import datetime
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
            time.sleep(random.uniform(1, 2))
            
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
                    from datetime import datetime
                    news_data.append([datetime.now().strftime('%m/%d/%y'), timestamp, headline, 'Yahoo Finance'])
            
            df = pd.DataFrame(news_data, columns=['date', 'time', 'headline', 'source'])
            return df
        
        except Exception as e:
            print(f"Error scraping Yahoo Finance news for {ticker}: {e}")
            return pd.DataFrame()