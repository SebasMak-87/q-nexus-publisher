import sqlite3

DB_FILE = "qpulse_data.db"

def view_archive():
    print("🗄 Відкриваю аналітичний архів Q-Pulse...\n")
    
    # 1. Підключаємось до бази даних
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 2. Формуємо SQL-запит
    # Вибираємо конкретні стовпці, сортуємо за спаданням ID і беремо 10 останніх
    sql_query = """
    SELECT id, publish_date, category, source, title
    FROM news_archive
    ORDER BY id DESC
    LIMIT 10
    """
    
    # 3. Виконуємо запит і забираємо всі знайдені рядки
    cursor.execute(sql_query)
    records = cursor.fetchall()
    
    if not records:
        print("📭 Архів поки що порожній.")
    else:
        # 4. Малюємо "шапку" таблиці з фіксованою шириною колонок
        print(f"{'ID':<4} | {'ДАТА':<16} | {'КАТЕГОРІЯ':<15} | {'ДЖЕРЕЛО':<15} | {'ЗАГОЛОВОК'}")
        print("-" * 100)
        
        # 5. Перебираємо кожен рядок з бази і виводимо його
        for row in records:
            db_id = row[0]
            date = row[1][:16]        # Беремо тільки перші 16 символів дати (без секунд)
            category = row[2]
            source = row[3][:14]      # Обрізаємо занадто довгі назви сайтів
            title = row[4][:40] + "..." if len(row[4]) > 40 else row[4] # Обрізаємо довгі заголовки
            
            # Виводимо дані, вирівнюючи їх по ширині колонок
            print(f"{db_id:<4} | {date:<16} | {category:<15} | {source:<15} | {title}")

    print("\n✅ Дані успішно прочитані.")
    
    # Закриваємо з'єднання
    conn.close()

if __name__ == "__main__":
    view_archive()