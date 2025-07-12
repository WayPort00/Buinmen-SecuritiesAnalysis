import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict, Optional
import json

class IndianStockScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.base_url = "https://query1.finance.yahoo.com"
        self.news_sources = {
            'moneycontrol': 'https://www.moneycontrol.com/news/tags/',
            'livemint': 'https://www.livemint.com/search/'
        }
        
    def search_stock(self, stock_name: str) -> Optional[str]:
        """Search for a stock using Yahoo Finance"""
        try:
            search_url = f"{self.base_url}/v1/finance/search"
            params = {
                'q': stock_name,
                'quotesCount': 1,
                'newsCount': 0
            }
            
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data['quotes']:
                return data['quotes'][0]['symbol']
            return None
        except Exception as e:
            print(f"Yahoo Finance search error: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get basic stock information"""
        try:
            url = f"{self.base_url}/v8/finance/chart/{symbol}?interval=1d"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            meta = data['chart']['result'][0]['meta']
            
            return {
                'stock_name': meta['symbol'],
                'ticker': symbol,
                'current_price': meta['regularMarketPrice'],
                'currency': meta['currency'],
                'exchange': meta['exchangeName']
            }
        except Exception as e:
            print(f"Error getting stock info: {e}")
            return {}
    
    def _parse_moneycontrol_timestamp(self, time_str: str) -> str:
        """Convert Moneycontrol's timestamp to standard format"""
        try:
            now = datetime.now()
            
            if 'ago' in time_str:
                num = int(re.search(r'\d+', time_str).group())
                if 'min' in time_str:
                    dt = now - timedelta(minutes=num)
                elif 'hour' in time_str:
                    dt = now - timedelta(hours=num)
                elif 'day' in time_str:
                    dt = now - timedelta(days=num)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            elif 'Today' in time_str:
                time_part = re.search(r'\d+:\d+ [AP]M', time_str)
                if time_part:
                    dt = datetime.strptime(f"{now.date()} {time_part.group()}", "%Y-%m-%d %I:%M %p")
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            elif 'Yesterday' in time_str:
                time_part = re.search(r'\d+:\d+ [AP]M', time_str)
                if time_part:
                    dt = datetime.strptime(f"{(now - timedelta(days=1)).date()} {time_part.group()}", "%Y-%m-%d %I:%M %p")
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # For month-day format (e.g., "May 21")
            elif re.match(r'[A-Za-z]+ \d+', time_str):
                current_year = now.year
                dt = datetime.strptime(f"{time_str} {current_year}", "%b %d %Y")
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return time_str
        except Exception as e:
            print(f"Error parsing timestamp '{time_str}': {e}")
            return time_str
    
    def get_moneycontrol_news(self, stock_name: str, max_news: int = 10) -> List[Dict]:
        """Get news from Moneycontrol with proper timestamps"""
        try:
            formatted_name = stock_name.lower().replace(' ', '-').replace('.ns', '')
            url = f"{self.news_sources['moneycontrol']}{formatted_name}.html"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('li', {'class': 'clearfix'})[:max_news]
            
            news_data = []
            for item in news_items:
                print(item)
                headline_tag = item.find('h2')
                if not headline_tag:
                    continue
                
                headline = headline_tag.text.strip()
                link = headline_tag.find('a')['href']
                source = "Moneycontrol"
                
                # --- Minimal timestamp fix starts here ---
                time_tag = item.find('span', {'class': 'list_dt'})
                if time_tag and time_tag.text.strip():
                    raw_ts = time_tag.text.strip()
                else:
                    raw_ts = "Recently"
                    for comment in item.find_all(string=lambda text: isinstance(text, Comment)):
                        m = re.search(r'<span>([^<]+IST)</span>', comment)
                        if m:
                            raw_ts = m.group(1).strip()
                            break


                parsed_timestamp = self._parse_moneycontrol_timestamp(raw_ts)
                
                news_data.append({
                    'headline': headline,
                    'source': source,
                    'published_ts': parsed_timestamp,
                    'raw_timestamp': raw_ts,
                    'sentiment': self._analyze_sentiment(headline),
                    'urgency': self._determine_urgency(parsed_timestamp),
                    'url': link
                })
            
            return news_data
        except Exception as e:
            print(f"Error getting Moneycontrol news: {e}")
            return []
    
    def get_livemint_news(self, stock_name: str, max_news: int = 5) -> List[Dict]:
        """Get news from Livemint as alternative to Business Standard"""
        try:
            formatted_name = stock_name.replace('.NS', '').replace(' ', '%20')
            url = f"{self.news_sources['livemint']}list/{formatted_name}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('div', {'class': 'listingNew'})[:max_news]
            
            news_data = []
            for item in news_items:
                headline_tag = item.find('h2', {'class': 'headline'})
                if not headline_tag:
                    continue
                
                headline = headline_tag.text.strip()
                link = headline_tag.find('a')['href']
                source = "Livemint"
                
                # Extract timestamp
                time_tag = item.find('span', {'class': 'date'})
                raw_timestamp = time_tag.text.strip() if time_tag else "Recently"
                
                # Parse Livemint timestamp (e.g., "21 May 2023, 05:30 PM IST")
                try:
                    parsed_timestamp = datetime.strptime(
                        re.sub(r'IST', '', raw_timestamp).strip(),
                        '%d %b %Y, %I:%M %p'
                    ).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    parsed_timestamp = raw_timestamp
                
                news_data.append({
                    'headline': headline,
                    'source': source,
                    'published_ts': parsed_timestamp,
                    'raw_timestamp': raw_timestamp,
                    'sentiment': self._analyze_sentiment(headline),
                    'urgency': self._determine_urgency(parsed_timestamp),
                    'url': link if link.startswith('http') else f'https://www.livemint.com{link}'
                })
            
            return news_data
        except Exception as e:
            print(f"Error getting Livemint news: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """Improved sentiment analysis with more keywords"""
        positive = ['buy', 'bullish', 'growth', 'positive', 'outperform', 'upgrade', 
                   'profit', 'rise', 'gain', 'strong', 'beat', 'surge', 'success',
                   'increase', 'higher', 'win', 'achievement', 'record']
        negative = ['sell', 'bearish', 'decline', 'negative', 'underperform', 'downgrade',
                   'loss', 'fall', 'drop', 'weak', 'miss', 'plunge', 'failure',
                   'decrease', 'lower', 'lose', 'problem', 'issue']
        
        text_lower = text.lower()
        pos = sum(text_lower.count(word) for word in positive)
        neg = sum(text_lower.count(word) for word in negative)
        
        if pos > neg:
            return 'positive'
        elif neg > pos:
            return 'negative'
        return 'neutral'
    
    def _determine_urgency(self, timestamp: str) -> str:
        """Determine urgency based on parsed timestamp"""
        try:
            if not re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestamp):
                return 'low'
            
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            delta = datetime.now() - dt
            
            if delta < timedelta(hours=1):
                return 'high'
            elif delta < timedelta(days=1):
                return 'medium'
            return 'low'
        except:
            return 'low'
    
    def scrape_stock_data(self, stock_name: str) -> Dict:
        """Main scraping function"""
        print(f"\nSearching for stock: {stock_name}")
        
        # Search for the stock symbol
        symbol = self.search_stock(stock_name + '.NS')  # .NS for NSE (Indian market)
        
        if not symbol:
            print("Trying without .NS suffix...")
            symbol = self.search_stock(stock_name)
            if not symbol:
                return {"error": "Stock not found on Yahoo Finance"}
        
        print(f"Found stock with symbol: {symbol}")
        
        # Get stock info and news from multiple sources
        stock_info = self.get_stock_info(symbol)
        
        # Get news from multiple sources
        moneycontrol_news = self.get_moneycontrol_news(stock_name)
        livemint_news = self.get_livemint_news(stock_name)
        
        # Combine all news
        all_news = moneycontrol_news + livemint_news
        
        # Sort news by parsed timestamp (newest first)
        try:
            all_news_sorted = sorted(
                all_news,
                key=lambda x: datetime.strptime(x['published_ts'], '%Y-%m-%d %H:%M:%S') 
                if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', x['published_ts']) 
                else datetime.min,
                reverse=True
            )
        except Exception as e:
            print(f"Error sorting news: {e}")
            all_news_sorted = all_news
        
        return {
            'stock_info': stock_info,
            'news': all_news_sorted[:10]  # Return top 10 news items
        }

def get_user_input():
    """Function to get stock name from user"""
    print("\n" + "="*50)
    print("INDIAN STOCK MARKET SCRAPER".center(50))
    print("="*50)
    print("\nEnter the name of the stock you want to search (e.g., Reliance Industries, TCS, Infosys)")
    print("Or type 'exit' to quit the program")
    
    while True:
        stock_name = input("\nEnter stock name: ").strip()
        if stock_name.lower() == 'exit':
            return None
        if stock_name:
            return stock_name
        print("Please enter a valid stock name")

if __name__ == "__main__":
    scraper = IndianStockScraper()
    
    while True:
        stock_name = get_user_input()
        if not stock_name:
            print("\nExiting program. Goodbye!")
            break
        
        stock_data = scraper.scrape_stock_data(stock_name)
        
        if 'error' in stock_data:
            print(f"\nError: {stock_data['error']}")
        else:
            print("\nStock Information:")
            print(json.dumps(stock_data['stock_info'], indent=2))
            
            if stock_data['news']:
                df = pd.DataFrame(stock_data['news'])
                print("\nLatest News:")
                print(df[['published_ts', 'headline', 'source', 'sentiment', 'urgency']])
            else:
                print("\nNo recent news articles found from our sources. Try checking the company website or other financial news portals.")
        
        print("\n" + "="*50)
        print("Search another stock or type 'exit' to quit")
        print("="*50)