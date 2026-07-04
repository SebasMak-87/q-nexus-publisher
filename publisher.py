import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import warnings
import sqlite3
import requests
import os
import json

warnings.filterwarnings("ignore")

# === 1. НАЛАШТУВАННЯ ТЕЛЕГРАМ ===
BOT_TOKEN = "token"  # Токен бота Telegram
CHANNELS = {
    "ru": "@qpulse_daily", 
    "en": "@qpulse_en",    
    "es": "@qpulse_es"     
}

NEWS_FILE = "ready_posts.json"

# === 2. ТИКЕРИ ТА ЛОКАЛІЗАЦІЯ ===
TICKERS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "S&P 500": "SPY", 
    "DXY": "DX-Y.NYB",
    "Treasuries 10Y": "^TNX",
    "Gold": "GC=F",
    "Oil": "CL=F",
    "NVIDIA": "NVDA",
    "AMD": "AMD"
}

LOCALIZATION = {
    "ru": {
        "header": "📊 **ДАЙДЖЕСТ ШТАБА | {time} (Киев)**",
        "crypto": "🌐 **КРИПТОРЫНОК:**",
        "macro": "🇺🇸 **МАКРО И ИНДЕКСЫ:**",
        "resources": "✨ **РЕСУРСЫ:**",
        "hardware": "💻 **ТЕХНО-ГИГАНТЫ (ЖЕЛЕЗО):**",
        "day": "Сутки", "month": "Месяц",
        "footer": "🧠 *Штаб: Формируем аналитический фокус перед стартом основных торгов.*"
    },
    "en": {
        "header": "📊 **MARKET DIGEST | {time} (Kyiv)**",
        "crypto": "🌐 **CRYPTO MARKET:**",
        "macro": "🇺🇸 **MACRO & INDICES:**",
        "resources": "✨ **RESOURCES:**",
        "hardware": "💻 **TECH GIANTS (HARDWARE):**",
        "day": "24h", "month": "30d",
        "footer": "🧠 *HQ: Forming analytical focus before the main session starts.*"
    },
    "es": {
        "header": "📊 **RESUMEN DEL MERCADO | {time} (Kyiv)**",
        "crypto": "🌐 **MERCADO CRIPTO:**",
        "macro": "🇺🇸 **MACRO E ÍNDICES:**",
        "resources": "✨ **RECURSOS:**",
        "hardware": "💻 **GIGANTES TECNOLÓGICOS:**",
        "day": "24h", "month": "30d",
        "footer": "🧠 *HQ: Formando enfoque analítico antes de la sesión principal.*"
    }
}

# === 3. БАЗА ДАНИХ (АРХІВАРІУС) ===
def init_db():
    conn = sqlite3.connect('market_archive.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            asset TEXT,
            price REAL,
            daily_change REAL,
            monthly_change REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_to_archive(date_str, asset, price, d_change, m_change):
    conn = sqlite3.connect('market_archive.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO daily_stats (date, asset, price, daily_change, monthly_change) VALUES (?, ?, ?, ?, ?)',
                   (date_str, asset, price, d_change, m_change))
    conn.commit()
    conn.close()

# === 4. ЛОГІКА ЗБОРУ ТА ПАБЛІШИНГУ ===
def get_emoji(val):
    return "🟢 +" if val >= 0 else "🔴 "

def send_to_telegram(text, channel_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": channel_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def process_markets(is_weekly_summary=False):
    init_db()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=45)
    time_str = end_date.strftime('%H:%M')
    today_str = end_date.strftime('%Y-%m-%d')
    
    print("\n📊 --- ЗАПУСК МОНІТОРИНГУ РИНКІВ ---")
    
    market_data = {}
    sections = {
        "crypto": ["BTC", "ETH"],
        "macro": ["S&P 500", "DXY", "Treasuries 10Y"],
        "resources": ["Gold", "Oil"],
        "hardware": ["NVIDIA", "AMD"]
    }

    for category, assets in sections.items():
        for asset in assets:
            print(f"⏳ Парсинг: {asset}...")
            try:
                ticker = yf.Ticker(TICKERS[asset])
                hist = ticker.history(start=start_date, end=end_date)
                
                if hist.empty or len(hist) < 6:
                    market_data[asset] = {"status": "error"}
                    time.sleep(2)
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                # ЛОГИКА НЕДЕЛИ vs СУТОК
                if is_weekly_summary:
                    # Для недельного итога берем цену 5 торговых дней назад
                    prev_price = hist['Close'].iloc[-6]
                else:
                    prev_price = hist['Close'].iloc[-2]
                    
                target_change = ((current_price - prev_price) / prev_price) * 100
                monthly_avg = hist['Close'].tail(30).mean()
                avg_change = ((current_price - monthly_avg) / monthly_avg) * 100
                
                market_data[asset] = {"status": "ok", "price": current_price, "target_change": target_change, "m": avg_change}
                
                # В архив пишем всегда суточные данные для истории
                daily_for_archive = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                save_to_archive(today_str, asset, current_price, daily_for_archive, avg_change)
                
                time.sleep(2)
            except Exception:
                market_data[asset] = {"status": "error"}
                time.sleep(2)

    for lang, channel_id in CHANNELS.items():
        loc = LOCALIZATION[lang]
        
        # Меняем заголовок, если это итог недели
        header_text = loc["header"].format(time=time_str)
        if is_weekly_summary:
            header_text = header_text.replace("ДАЙДЖЕСТ", "ИТОГИ НЕДЕЛИ").replace("DIGEST", "WEEKLY SUMMARY").replace("RESUMEN", "RESUMEN SEMANAL")
            
        lines = [header_text, "_" * 30, ""]
        
        # Динамические подписи для периода
        period_label = "Неделя" if is_weekly_summary and lang == "ru" else "7d" if is_weekly_summary else loc['day']
        
        for category, assets in sections.items():
            lines.append(loc[category])
            for asset in assets:
                data = market_data[asset]
                if data["status"] == "error":
                    lines.append(f"• **{asset}**: ⚠️ Немає даних")
                    continue
                
                p = data["price"]
                p_str = f"${p:,.2f}" if p >= 1000 and asset not in ["S&P 500", "DXY", "Treasuries 10Y"] else f"${p:.2f}" if asset not in ["S&P 500", "DXY", "Treasuries 10Y"] else f"{p:.2f}"
                if asset == "Treasuries 10Y": p_str += "%"
                
                lines.append(
                    f"• **{asset}**: {p_str} | "
                    f"{period_label}: {get_emoji(data['target_change'])}{data['target_change']:.2f}% | "
                    f"{loc['month']}: {get_emoji(data['m'])}{data['m']:.2f}%"
                )
            lines.append("")
            
        lines.append("_" * 30)
        lines.append(loc["footer"])
        
        final_text = "\n".join(lines)
        
        res = send_to_telegram(final_text, channel_id)
        if res.get("ok"): print(f"   ✅ {lang.upper()} Опубліковано!")
        else: print(f"   ❌ {lang.upper()} Помилка: {res}")
        time.sleep(2)

# === 5. ПУБЛІКАЦІЯ СТРІЧКИ НОВИН ===
def process_news():
    print("\n📰 --- ЗАПУСК ПУБЛІКАЦІЇ НОВИН ---")
    if not os.path.exists(NEWS_FILE):
        print(f"📭 Файл {NEWS_FILE} не знайдено. Поки що немає новин для публікації.")
        return

    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)
        
        if not posts:
            print("📭 Файл новин порожній.")
            return

        print(f"📦 Завантажено {len(posts)} мультиязичних новин. Починаємо розсилку...")

        for idx, post in enumerate(posts, 1):
            print(f"\nОбробка новини №{idx}...")
            
            for lang, channel_id in CHANNELS.items():
                text_to_send = None
                
                # Забираємо текст із правильного рівня вкладеності
                if "posts" in post and lang in post["posts"]:
                    text_to_send = post["posts"][lang]
                elif lang in post:
                    text_to_send = post[lang]
                elif f"text_{lang}" in post:
                    text_to_send = post[f"text_{lang}"]
                
                if text_to_send:
                    print(f"  📤 Відправка в {channel_id} ({lang.upper()})...")
                    res = send_to_telegram(text_to_send, channel_id)
                    if res.get("ok"):
                        print("    ✅ Опубліковано!")
                    else:
                        print(f"    ❌ Помилка відправки: {res}")
                    time.sleep(2) 
                else:
                    print(f"  ⚠️ Не знайдено тексту для мови {lang.upper()} у цій новині.")
                    
        os.remove(NEWS_FILE)
        print(f"\n🧹 Транзитний файл {NEWS_FILE} успішно видалено. Конвеєр чистий.")

    except Exception as e:
        print(f"❌ Критична помилка в блоці публікації новин: {e}")

if __name__ == "__main__":
    print("🚀 Старт новостного конвейера Штаба...")
    while True:
        process_markets()  
        process_news()
        
        # Усыпляем скрипт, чтобы Docker его не перезапускал
        # 3600 секунд = 1 час. 
        # Если сводки нужны раз в сутки (24 часа), ставь 86400
        print("⏳ Такт завершен. Уходим в спящий режим...")
        time.sleep(3600)