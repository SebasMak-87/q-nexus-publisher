import schedule
import time
from datetime import datetime

# Подключаем наши модули
import scraper
import ai_editor
import publisher

def run_tech_news(categories):
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{current_time}] 🚀 СТАРТ КОНВЕЙЕРА НОВОСТЕЙ: {categories}")
    
    # 1. Скрейпер собирает данные по списку тем
    scraper.fetch_news(categories)
    # 2. ИИ-редактор переводит и форматирует
    ai_editor.process_news()
    # 3. Паблишер рассылает по каналам
    publisher.process_news()
    
    print("✅ Конвейер новостей завершил такт.")

def run_market_digest():
    now = datetime.now()
    # Проверяем, пятница ли сегодня (weekday() == 4) и вечерний ли это выпуск (после 20:00)
    is_friday_close = (now.weekday() == 4 and now.hour > 20)
    
    print(f"\n[{now.strftime('%H:%M:%S')}] 📈 СТАРТ МАРКЕТ-ДАЙДЖЕСТА (Итог недели: {is_friday_close})")
    publisher.process_markets(is_weekly_summary=is_friday_close)

# ==========================================
# 🕒 РАСПИСАНИЕ НОВОСТЕЙ (Локальное время)
# ==========================================
schedule.every().day.at("09:00").do(run_tech_news, categories=["ai_and_soft", "robotics"])
schedule.every().day.at("13:00").do(run_tech_news, categories=["hardware", "science_and_quantum"])
schedule.every().day.at("17:00").do(run_tech_news, categories=["tech_giants", "crypto"])
schedule.every().day.at("21:00").do(run_tech_news, categories=["space"])

# ==========================================
# 📈 РАСПИСАНИЕ РЫНКОВ (Нью-Йорк -> Локальное +7 часов)
# ==========================================
# 08:50 NY -> 15:50 (Открытие биржи)
schedule.every().day.at("15:50").do(run_market_digest)
# 16:00 NY -> 23:00 (Закрытие биржи)
schedule.every().day.at("23:00").do(run_market_digest)

if __name__ == "__main__":
    print("🟢 Штаб Quantum Code G&S: Ядро Q-Pulse запущено. Ожидание таймингов...")
    # Чтобы скрипт не отключался, он крутится в бесконечном цикле и проверяет время
    while True:
        schedule.run_pending()
        time.sleep(65)