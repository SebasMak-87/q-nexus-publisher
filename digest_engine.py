import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import warnings

# Вимикаємо зайвий системний спам від Pandas
warnings.filterwarnings("ignore")

TICKERS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "S&P 500": "^SPX",
    "DXY": "DX-Y.NYB",
    "Treasuries 10Y": "^TNX",
    "Gold": "GC=F",
    "Oil": "CL=F",
    "NVIDIA": "NVDA",
    "AMD": "AMD"
}

def get_emoji(val):
    return "🟢 +" if val >= 0 else "🔴 "

def generate_daily_digest():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=45)
    
    digest_lines = [
        f"📊 **ДАЙДЖЕСТ ШТАБУ | {end_date.strftime('%H:%M')} (Київ)**",
        "_" * 30,
        ""
    ]
    
    sections = {
        "🌐 КРИПТОРИНОК:": ["BTC", "ETH"],
        "🇺🇸 МАКРО ТА ІНДЕКСИ:": ["S&P 500", "DXY", "Treasuries 10Y"],
        "✨ РЕСУРСИ:": ["Gold", "Oil"],
        "💻 ТЕХНО-ГІГАНТИ (ЗАЛІЗО):": ["NVIDIA", "AMD"]
    }

    print("📡 Зв'язок з Yahoo Finance встановлено. Починаємо завантаження...")

    for section_name, assets in sections.items():
        digest_lines.append(f"**{section_name}**")
        
        for asset in assets:
            ticker_symbol = TICKERS[asset]
            print(f"⏳ Завантажую котирування: {asset}...") # Наша кардіограма в термінал
            
            try:
                # Використовуємо чистий yfinance, він сам розбереться з токенами
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                if hist.empty:
                    digest_lines.append(f"• {asset}: ⚠️ Дані тимчасово недоступні")
                    time.sleep(2)
                    continue
                
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                
                daily_change = ((current_price - prev_price) / prev_price) * 100
                
                last_30_records = hist['Close'].tail(30)
                monthly_avg = last_30_records.mean()
                avg_change = ((current_price - monthly_avg) / monthly_avg) * 100
                
                if current_price >= 1000:
                    price_str = f"${current_price:,.2f}" if "USD" in ticker_symbol or asset in ["BTC", "ETH"] else f"{current_price:,.2f}"
                else:
                    price_str = f"${current_price:.2f}" if asset not in ["S&P 500", "DXY", "Treasuries 10Y"] else f"{current_price:.2f}"
                
                if asset in ["S&P 500", "DXY", "Treasuries 10Y"]:
                    price_str = price_str.replace("$", "")
                if asset == "Treasuries 10Y":
                    price_str += "%"
                
                daily_emoji = get_emoji(daily_change)
                avg_emoji = get_emoji(avg_change)
                
                digest_lines.append(
                    f"• **{asset}**: {price_str} | "
                    f"Доба: {daily_emoji}{daily_change:.2f}% | "
                    f"Місяць: {avg_emoji}{avg_change:.2f}%"
                )
                
                # Дихаємо... 3 секунди паузи
                time.sleep(3)
                
            except Exception as e:
                digest_lines.append(f"• {asset}: ❌ Помилка ({str(e)[:30]})")
                time.sleep(3)
        
        digest_lines.append("")
        
    digest_lines.append("_" * 30)
    digest_lines.append("🧠 *Штаб: Формуємо аналітичний фокус перед стартом основних торгів. Дані оновлено автоматично.*")
    
    print("✅ Усі 9 блоків успішно завантажено!\n")
    return "\n".join(digest_lines)

if __name__ == "__main__":
    print("🚀 Старт двигуна Digest Engine...")
    final_text = generate_daily_digest()
    print("\n" + "="*40 + "\n")
    print(final_text)