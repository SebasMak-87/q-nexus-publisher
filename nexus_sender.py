import os
import re
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Завантажуємо ключі з сейфа .env
load_dotenv()

# ==========================================
# ⚙️ НАСТРОЙКИ ЛОГИСТИКИ И НОВЫЕ КЛЮЧИ API
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = {
    "ru": "@qpulse_daily",
    "en": "@qpulse_en",
    "es": "@qpulse_es"
}

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ==========================================
# 🛡 КАСКАДНИЙ ПЕРЕКЛАДАЧ (Graceful Degradation)
# ==========================================
def translate_with_cascade(text: str, target_language: str) -> str:
    """
    Пытается перевести текст через Groq, при падении уходит на Gemini.
    Если ложатся оба — вызывает триггер аварии.
    """
    system_prompt = f"Переклади цей новинний текст на {target_language} мову. Збережи оригінальне форматування, абзаци та емодзі. Не додавай жодних своїх коментарів."
    
    # 🟢 TIER 1: GROQ
    if GROQ_API_KEY:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile", 
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}], 
                    "temperature": 0.3
                },
                timeout=20
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            print(f"⚠️ GROQ впав (Код {response.status_code}). Перехід на Tier 2...")
        except Exception as e:
            print(f"⚠️ Помилка GROQ: {e}")

    # 🟡 TIER 2: GEMINI
    if GEMINI_API_KEY:
        try:
            full_prompt = f"{system_prompt}\n\n{text}"
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": full_prompt}]}]},
                timeout=20
            )
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            print(f"⚠️ Gemini впав (Код {response.status_code}).")
        except Exception as e:
            print(f"⚠️ Помилка Gemini: {e}")

    # 🔴 TIER 3: АВАРІЯ ВСІХ ШЛЮЗІВ
    raise Exception("ALL_APIS_DOWN")

# ==========================================
# 🎨 ГРАФИЧЕСКИЙ ДВИЖОК И ОТПРАВКА (Твои старые функции)
# ==========================================
def create_watermarked_image(image_url):
    # ... ТУТ ТВОЙ СТАРЫЙ КОД НАНЕСЕНИЯ ВОДЯНОГО ЗНАКА ...
    pass

def send_to_telegram(text, image_path, channel_id):
    # ... ТУТ ТВОЙ СТАРЫЙ КОД ОТПРАВКИ В ТЕЛЕГРАМ ...
    pass

# ==========================================
# 🚀 ГОЛОВНИЙ ОРКЕСТРАТОР ПУБЛІКАЦІЇ
# ==========================================
def main():
    draft_file = "draft_news.txt"
    if not os.path.exists(draft_file):
        print(f"❌ Файл {draft_file} не знайдено.")
        return

    with open(draft_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Якщо скаутер впав і записав порожній файл або коротку помилку
    if len(content) < 50:
        print("⚠️ Здається, скаутер не зміг зібрати новину. Активуємо резервний протокол.")
        trigger_easter_egg()
        return

    raw_image_url = None
    clean_text = content
    
    img_match = re.search(r'IMG:\s*(https?://[^\s]+)', content)
    if img_match:
        raw_image_url = img_match.group(1)
        clean_text = re.sub(r'IMG:\s*https?://[^\s]+', '', content).strip()

    print("🚀 Q NEXUS Logistics: Починаємо мультимовну публікацію...\n")

    local_image_path = None
    if raw_image_url:
        print("🎨 Створюємо фірмовий водяний знак...")
        local_image_path = create_watermarked_image(raw_image_url)

    try:
        # 1. ПУБЛІКАЦІЯ ОРИГІНАЛУ (RU)
        print(f"➡️ Відправка оригіналу в RU канал ({CHANNELS['ru']})...")
        send_to_telegram(clean_text, local_image_path, CHANNELS["ru"])

        # 2. ПЕРЕКЛАД І ПУБЛІКАЦІЯ (EN)
        print(f"➡️ Переклад на EN та відправка в ({CHANNELS['en']})...")
        en_text = translate_with_cascade(clean_text, "англійську")
        send_to_telegram(en_text, local_image_path, CHANNELS["en"])

        # 3. ПЕРЕКЛАД І ПУБЛІКАЦІЯ (ES)
        print(f"➡️ Переклад на ES та відправка в ({CHANNELS['es']})...")
        es_text = translate_with_cascade(clean_text, "іспанську")
        send_to_telegram(es_text, local_image_path, CHANNELS["es"])
        
        print("✅ Усі публікації успішно завершені!")

    except Exception as e:
        if str(e) == "ALL_APIS_DOWN":
            print("💥 КРИТИЧНИЙ ЗБІЙ API: Перемикаємось на ручне керування (Пасхалка)!")
            trigger_easter_egg()
        else:
            print(f"❌ Невідома помилка під час публікації: {e}")


def trigger_easter_egg():
    """Розсилає хардкодну гумористичну заглушку різними мовами."""
    
    egg_ru = (
        "🤖 **Штучний інтелект Q=NExUS узяв тайм-аут!**\n\n"
        "Ліміти API вичерпано, наші нейромережі п'ють віртуальну каву, але редакція все одно з вами! 🚀\n\n"
        "Поки наші інженери збирають сервери до купи і підливають мастило в алгоритми, "
        "зробимо перекличку. Як проходить ваш день? Діліться в коментарях найдивнішою новиною, яку ви сьогодні чули!\n\n"
        "*P.S. Скоро повернемося з потужною аналітикою. Залишайтеся на зв'язку! 📡*"
    )
    
    egg_en = (
        "🤖 **Q=NExUS AI took a coffee break!**\n\n"
        "API limits have been reached, our neural networks are resting, but we are still online! 🚀\n\n"
        "While our engineers are pouring oil into the algorithms, let's have a quick chat. "
        "How is your day going? Share the weirdest news you've heard today in the comments!\n\n"
        "*P.S. We will be back with powerful analytics soon. Stay tuned! 📡*"
    )
    
    egg_es = (
        "🤖 **¡La IA de Q=NExUS se tomó un descanso!**\n\n"
        "Se han alcanzado los límites de la API, nuestras redes neuronales están tomando café, ¡pero seguimos en línea! 🚀\n\n"
        "Mientras nuestros ingenieros engrasan los algoritmos, cuéntanos: "
        "¿Cómo va tu día? ¡Comparte la noticia más extraña que hayas escuchado hoy en los comentarios!\n\n"
        "*P.S. Volveremos pronto con análisis potentes. ¡Mantente conectado! 📡*"
    )
    
    # Відправляємо пасхалки без картинок (або можеш додати шлях до заготовленої смішної картинки замість None)
    send_to_telegram(egg_ru, None, CHANNELS["ru"])
    send_to_telegram(egg_en, None, CHANNELS["en"])
    send_to_telegram(egg_es, None, CHANNELS["es"])

if __name__ == "__main__":
    main()