import json
import os
import time
import re
from google import genai

# 1. ІНІЦІАЛІЗАЦІЯ API
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"
client = genai.Client(api_key=API_KEY)
MODEL_ID = 'gemini-2.5-flash'

INPUT_FILE = "raw_news.json"
OUTPUT_FILE = "ready_posts.json"

def clean_json_response(text):
    """Очищає відповідь ШІ від маркдауну, щоб залишився чистий JSON"""
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()

def process_news():
    print("🧠 Запуск Мультязичного ІІ-редактора Q-Pulse...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_news = json.load(f)

    ready_posts = []

    for item in raw_news:
        print(f"🔄 Перекладаю та аналізую: {item['title']}...")
        
        prompt = f"""
        You are the Chief Technical Editor of Q-Pulse. Process this news for a Telegram channel.
        Category ID: {item['category']}
        Original Title: {item['title']}
        Summary: {item['summary']}
        
        Provide the output STRICTLY as a valid JSON object with exactly three keys: "en", "ru", "es".
        
        Rules for the text in each language:
        1. Start with an appropriate visual tag (e.g., [🧠 AI & Soft], [⚙️ Hardware], [🚀 Space]).
        2. Write a clear, engineering-style title.
        3. Write a concise summary without filler words.
        4. Include 2-3 relevant emojis in the text.
        5. End the post with a single, clickable hashtag based on the category (e.g., #AISoft, #Hardware, #Space). DO NOT use underscores (_) in hashtags.
        6. IMPORTANT: DO NOT use markdown formatting like **bold** or *italic* anywhere in the text. Output plain text only.
        
        Output ONLY the JSON object. Do not add any conversational text.
        """
        
        # --- ВПРОВАДЖЕНО НОВИЙ АЛГОРИТМ ЗАХИСТУ ТА ЛІМІТІВ ---
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                
                raw_text = response.text if response.text else "{}"
                cleaned_json_string = clean_json_response(raw_text)
                
                # Перетворюємо текст від ШІ у справжній словник Python
                translations = json.loads(cleaned_json_string)
                
                # Додаємо посилання на джерело до кожного перекладу
                for lang in ["en", "ru", "es"]:
                    if lang in translations:
                        translations[lang] = f"{translations[lang]}\n\n🔗 Source: {item['source']} | [Link]({item['link']})"
                
                # Зберігаємо готовий багатомовний пакет
                ready_posts.append({
                    "source": item["source"],
                    "link": item["link"],
                    "posts": translations
                })
                
                print("   ✅ Успішно! Охолодження API (15 сек)...")
                time.sleep(15) # Жорсткий ліміт для безкоштовного тарифу (4 запити на хвилину)
                break # Виходимо з циклу спроб, йдемо до наступної новини
                
            except json.JSONDecodeError:
                print(f"❌ Помилка: ШІ повернув невалідний JSON для {item['title']}")
                break # Немає сенсу повторювати, якщо проблема у форматі
                
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "429" in error_msg:
                    wait_time = 30 * (attempt + 1)
                    print(f"   ⚠️ API перевантажено. Спроба {attempt + 1}/{max_retries}. Чекаємо {wait_time} сек...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Критична помилка API: {e}")
                    break # Якщо помилка інша (наприклад, невірний ключ), йдемо далі
        # --- КІНЕЦЬ БЛОКУ ЗАХИСТУ ---

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(ready_posts, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Готово! Згенеровано {len(ready_posts)} багатомовних постів.")

if __name__ == "__main__":
    process_news()