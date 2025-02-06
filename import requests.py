import requests
import time
from datetime import datetime

def get_xmr_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "monero",
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_last_updated_at": "true"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "monero" not in data:
            print("Error: Invalid response from API")
            return None

        xmr_data = data["monero"]
        price = xmr_data.get("usd", "N/A")
        change_24h = xmr_data.get("usd_24h_change", "N/A")
        last_updated = xmr_data.get("last_updated_at", None)

        if last_updated:
            last_updated = datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            "price": price,
            "change_24h": change_24h,
            "last_updated": last_updated
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def display_price(data):
    if not data:
        return
    
    price = data["price"]
    change = data["change_24h"]
    updated = data["last_updated"]
    
    change_str = f"{change:.2f}%"
    if isinstance(change, float):
        change_str = ("▲ " if change >= 0 else "▼ ") + change_str
    
    print("\n" + "="*40)
    print(f"XMR/USD Price: ${price}")
    print(f"24h Change:    {change_str}")
    print(f"Last Updated:  {updated}")
    print("="*40 + "\n")

def main():
    refresh_interval = 10  # 刷新间隔（秒）

    print("Starting XMR Price Tracker (Press Ctrl+C to stop)")
    
    try:
        while True:
            data = get_xmr_price()
            if data:
                display_price(data)
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\nProgram stopped.")

if __name__ == "__main__":
    main()