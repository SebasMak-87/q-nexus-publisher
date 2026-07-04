import feedparser
import json
import os
import re
import sqlite3
from datetime import datetime

# 1. МАТРИЦЯ ДЖЕРЕЛ
SOURCES = {
    "ai_and_soft": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.technologyreview.com/feed/"
    ],
    "robotics": [
        "https://spectrum.ieee.org/feeds/feed.rss?query=robotics",
        "https://techcrunch.com/category/robotics/feed/"
    ],
    "hardware": [
        "https://www.servethehome.com/feed/",
        "https://www.tomshardware.com/feeds/all"
    ],
    "science_and_quantum": [
        "https://phys.org/rss-feed/physics-news/quantum-physics/",
        "https://www.sciencedaily.com/rss/computers_math/quantum_computers.xml"
    ],
    "tech_giants": [
        "https://www.theverge.com/rss/index.xml",
        "https://blogs.microsoft.com/feed/"
    ],
    "crypto": [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/"
    ],
    "space": [
        "https://spacenews.com/feed/",
        "https://www.space.com/feeds/all"
    ]
}

OUTPUT_FILE = "raw_news.json"
HISTORY_FILE = "history_urls.txt"
DB_FILE = "qpulse_data.db"

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return re.sub(r'\s+', ' ', cleantext).strip()

def get_active_categories(hour):
    if 0 <= hour < 13:
        return ["ai_and_soft", "robotics"]
    elif 13 <= hour < 17:
        return ["hardware", "science_and_quantum"]
    elif 17 <= hour < 20:
        return ["tech_giants", "crypto"]
    else:
        return ["space"]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def save_to_history(new_urls):
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        for url in new_urls:
            f.write(url + '\n')

def archive_to_db(news_list):
    """Зберігає сирі новини у вічний SQL-архів"""
    if not news_list:
        return
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Знаки питання (?) - це захист від SQL-ін'єкцій. База сама підставить дані безпечно.
    sql_query = """
    INSERT OR IGNORE INTO news_archive 
    (publish_date, category, source, title, content, url) 
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    db_records = []
    for item in news_list:
        db_records.append((
            item['published'],
            item['category'],
            item['source'],
            item['title'],
            item['summary'],
            item['link']
        ))
        
    cursor.executemany(sql_query, db_records)
    conn.commit()
    conn.close()
    print("🗄  Дані успішно завантажено у вічний SQL-архів.")

def fetch_news(active_categories):
    exact_time = datetime.now().strftime("%H:%M") 
    
    print(f"⚡️ Запуск Q-Pulse Scraper...")
    print(f"🕒 Поточний час на сервері: {exact_time}")
    print(f"🎯 Активні категорії: {', '.join(active_categories)}")
    
    history = load_history()
    all_news = []
    new_urls = []
    
    for category in active_categories:
        print(f"\n📂 Шукаю новини в категорії: [{category}]")
        for url in SOURCES[category]:
            try:
                feed = feedparser.parse(url)
                added_from_source = 0
                
                for entry in feed.entries:
                    if added_from_source >= 2:
                        break
                        
                    link = str(getattr(entry, 'link', ''))
                    if not link or link in history:
                        continue
                        
                    source_name = str(getattr(feed.feed, 'title', 'News Source'))
                    
                    news_item = {
                        "category": category,
                        "source": source_name,
                        "title": str(getattr(entry, 'title', '')),
                        "link": link,
                        "summary": clean_html(str(getattr(entry, 'summary', ''))),
                        "published": str(getattr(entry, 'published', datetime.now()))
                    }
                    
                    all_news.append(news_item)
                    new_urls.append(link)
                    history.add(link)
                    added_from_source += 1
                    
            except Exception as e:
                print(f"❌ Помилка при читанні {url}: {e}")
                
    if not all_news:
        print("\n📭 Усі останні новини з цих джерел вже були оброблені раніше. Нових даних немає.")
        return

    # Зберігаємо в JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
        
    save_to_history(new_urls)
    archive_to_db(all_news)
        
    print(f"\n✅ Готово! Зібрано {len(all_news)} нових, унікальних новин.")

# Убираем блок if __name__ == "__main__", так как теперь скрейпер вызывается только из ядра.