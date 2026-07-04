import os
import re
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from langchain_google_genai import ChatGoogleGenerativeAI

# ==========================================
# ⚙️ НАСТРОЙКИ ЛОГИСТИКИ
# ==========================================
BOT_TOKEN = "token"  # Токен бота Telegram
CHANNELS = {
    "ru": "@qpulse_daily",
    "en": "@qpulse_en",
    "es": "@qpulse_es"
}

os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# ==========================================
# 🎨 ГРАФИЧЕСКИЙ ДВИЖОК Q NEXUS
# ==========================================
def create_watermarked_image(image_url):
    """Скачивает картинку и накладывает цветной водяной знак"""
    try:
        # 1. Скачиваем оригинальную картинку
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # 2. Подключаем шрифты macOS (или берем дефолтные, если не найдено)
        try:
            font_main = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
            font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Italic.ttf", 30)
        except:
            font_main = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        # 3. Настройки текста
        x, y = 30, 30 # Отступ от левого верхнего края
        # Формула: (Текст, Цвет RGB)
        parts = [
            ("Q", (255, 50, 50, 255)),     # Красный
            ("=", (255, 165, 0, 255)),     # Оранжевый
            ("NE", (50, 205, 50, 255)),    # Зеленый
            ("x", (255, 255, 255, 255)),   # Белый
            ("US", (65, 105, 225, 255))    # Синий
        ]

        # 4. Рисуем главную формулу буква за буквой (чтобы менять цвета)
        current_x = x
        for text, color in parts:
            # Рисуем букву с черной обводкой для читаемости на светлом фоне
            draw.text((current_x, y), text, font=font_main, fill=color, stroke_width=3, stroke_fill=(0,0,0,255))
            # Вычисляем ширину нарисованного текста и сдвигаем "курсор"
            bbox = draw.textbbox((current_x, y), text, font=font_main)
            current_x = bbox[2] + 2 

        # 5. Рисуем подзаголовок ниже (косой шрифт)
        draw.text((x + 5, y + 70), "- Издательский Дом -", font=font_sub, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0,0,0,255))

        # 6. Сохраняем результат
        output_path = "watermarked_nexus.jpg"
        img.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path

    except Exception as e:
        print(f"⚠️ Ошибка графического движка: {e}")
        return None

# ==========================================
# 🚀 ОТПРАВКА И ПЕРЕВОД
# ==========================================
def send_to_telegram(text, image_path, channel_id):
    """Отправляет готовый пост в Telegram"""
    header = "**Q=NExUS**\n_Издательский Дом_\n\n"
    final_text = header + text

    if image_path and os.path.exists(image_path):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        data = {"chat_id": channel_id, "caption": final_text, "parse_mode": "Markdown"}
        with open(image_path, "rb") as photo:
            response = requests.post(url, data=data, files={"photo": photo})
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": channel_id, "text": final_text, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        
    if response.status_code != 200:
        print(f"⚠️ Ошибка отправки в {channel_id}: {response.text}")
    return response.json()

def translate_text(text, target_lang):
    prompt = f"Переведи этот текст для Telegram-канала на {target_lang} язык. Сохрани всё форматирование. Без комментариев:\n\n{text}"
    response = llm.invoke(prompt)
    return str(response.content).strip()

def main():
    draft_file = "nexus_draft.txt"
    if not os.path.exists(draft_file):
        print(f"❌ Файл {draft_file} не найден.")
        return

    with open(draft_file, "r", encoding="utf-8") as f:
        content = f.read()

    raw_image_url = None
    clean_text = content
    
    img_match = re.search(r'IMG:\s*(https?://[^\s]+)', content)
    if img_match:
        raw_image_url = img_match.group(1)
        clean_text = re.sub(r'IMG:\s*https?://[^\s]+', '', content).strip()

    print("🚀 Q NEXUS Logistics: Начинаем мультиязычную публикацию...\n")

    # Включаем графический движок
    local_image_path = None
    if raw_image_url:
        print("🎨 Создаем фирменный водяной знак...")
        local_image_path = create_watermarked_image(raw_image_url)

    print(f"➡️ Отправка оригинала в RU канал ({CHANNELS['ru']})...")
    send_to_telegram(clean_text, local_image_path, CHANNELS["ru"])

    print(f"➡️ Перевод на EN и отправка в ({CHANNELS['en']})...")
    en_text = translate_text(clean_text, "английский")
    send_to_telegram(en_text, local_image_path, CHANNELS["en"])

    print(f"➡️ Перевод на ES и отправка в ({CHANNELS['es']})...")
    es_text = translate_text(clean_text, "испанский")
    send_to_telegram(es_text, local_image_path, CHANNELS["es"])

    # Убираем рабочее место (удаляем черновик и картинку)
    os.remove(draft_file)
    if local_image_path and os.path.exists(local_image_path):
        os.remove(local_image_path)
    print("\n✅ Цикл логистики успешно завершен!")

if __name__ == "__main__":
    main()