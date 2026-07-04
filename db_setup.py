import sqlite3

def create_database():
    print("🛠 Починаю збірку бази даних Q-Pulse...")
    
    # 1. Створюємо файл бази (або підключаємось, якщо він вже є)
    conn = sqlite3.connect('qpulse_data.db')
    
    # 2. Створюємо курсор - це наш "робітник", який виконує SQL-команди
    cursor = conn.cursor()
    
    # 3. Пишемо чистий SQL-запит на створення таблиці
    sql_query = """
    CREATE TABLE IF NOT EXISTS news_archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        publish_date TEXT NOT NULL,
        category TEXT,
        source TEXT,
        title TEXT,
        content TEXT,
        url TEXT UNIQUE
    )
    """
    
    # 4. Виконуємо запит
    cursor.execute(sql_query)
    
    # 5. Зберігаємо зміни та закриваємо з'єднання
    conn.commit()
    conn.close()
    
    print("✅ Базу успішно створено! Таблиця 'news_archive' готова до роботи.")
    print("📁 Файл: qpulse_data.db")

if __name__ == "__main__":
    create_database()