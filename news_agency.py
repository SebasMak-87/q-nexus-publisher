import os
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool 
from langchain_google_genai import ChatGoogleGenerativeAI # 👈 ИМПОРТ МОСТА К GEMINI
from duckduckgo_search import DDGS 

# ==========================================
# 🔑 НАСТРОЙКА МОЗГА (Внешний API - GEMINI)
# ==========================================
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"

# Инициализируем мозг Gemini (модель 2.5 Flash - идеальна для быстрых Агентов)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# ==========================================
# 🛠 НАШ СОБСТВЕННЫЙ ИНСТРУМЕНТ (БЕЗ LANGCHAIN)
# ==========================================
@tool("Internet News and Image Search")
def search_news_tool(query: str) -> str:
    """Ищет свежие новости и ссылки на картинки к ним. Вход - поисковый запрос (например: crypto news)."""
    try:
        # Используем поиск по новостям (.news), он отдает прямые ссылки на картинки!
        results = DDGS().news(query, max_results=2)
        formatted_results = []
        for r in results:
            title = r.get('title', 'Без заголовка')
            body = r.get('body', '')
            url = r.get('url', '')
            image = r.get('image', 'Картинка не найдена')
            formatted_results.append(f"Заголовок: {title}\nСуть: {body}\nИсточник: {url}\nКартинка: {image}\n")
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Ошибка поиска: {e}"

# ==========================================
# 👨‍💼 ПУНКТ 1: АГЕНТЫ (Наши сотрудники)
# ==========================================
scout = Agent(
    role='Senior Tech News Scout',
    goal='Найти 1 самую свежую и важную новость из мира ИИ, технологий или криптовалют за сегодня.',
    backstory='Ты — опытный журналист-исследователь. Ты умеешь находить бриллианты в куче информационного мусора. Ты ищешь только достоверные факты.',
    verbose=True,
    allow_delegation=False,
    tools=[search_news_tool],
    llm=llm
)

writer = Agent(
    role='Tech Copywriter',
    goal='Написать вовлекающий, понятный и лаконичный пост для Telegram-канала на основе найденных фактов.',
    backstory='Ты крутой копирайтер. Твои тексты читаются на одном дыхании. Ты умеешь объяснять сложные технические вещи простым языком без занудства.',
    verbose=True,
    allow_delegation=False,
    llm=llm
)

editor = Agent(
    role='Editor in Chief',
    goal='Проверить текст райтера и отформатировать его под строгий стиль канала Q-Pulse.',
    backstory='Ты главный редактор. Ты ненавидишь воду в текстах. Твое правило: заголовок, суть в 2-3 предложениях, маркированные списки и немного уместных эмодзи.',
    verbose=True,
    allow_delegation=True,
    llm=llm
)

# ==========================================
# 📋 ПУНКТ 2: ЗАДАЧИ (ТЗ)
# ==========================================
task1 = Task(
    description='Найди самую горячую новость про ИИ или криптовалюты за последние 24 часа. Собери факты, цифры и ключевые имена.',
    expected_output='Краткая выжимка фактов, ссылок и имен в виде текста.',
    agent=scout
)

task2 = Task(
    description='Напиши черновик поста на основе фактов от Скаутера. Обязательно сохрани ссылку на картинку (если Скаутер ее нашел) и передай ее дальше.',
    expected_output='Связный текст черновика поста с URL картинки в самом конце.',
    agent=writer
)

task3 = Task(
    description='Отредактируй черновик. Сделай его идеальным для Telegram. В самом низу поста с новой строки ОБЯЗАТЕЛЬНО напиши "IMG: " и вставь сырую ссылку на картинку.',
    expected_output='Готовый отформатированный пост. В конце с новой строки: IMG: [ссылка на картинку].',
    agent=editor
)

# ==========================================
# 🤝 ПУНКТ 3: КОМАНДА (Crew)
# ==========================================
# === ФОРМИРУЕМ КОМАНДУ И ЗАПУСКАЕМ ===
news_crew = Crew(
        agents=[scout, writer, editor],
        tasks=[task1, task2, task3],
        verbose=True,
        max_rpm=3  # 🛑 <-- Добавляем только эту строчку
    )
# ==========================================
# 🚀 ЗАПУСК БЮРО
# ==========================================
if __name__ == "__main__":
    print("🔥 Цифровая редакция Q-Pulse (на базе Gemini) начинает работу...\n")
    result = news_crew.kickoff()
    
    print("\n==========================================")
    print("📰 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ОТ РЕДАКТОРА:")
    print("==========================================")
    print(result)

    # === НОВЫЙ БЛОК: СОХРАНЕНИЕ В ФАЙЛ ===
    try:
        with open("nexus_draft.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
        print("✅ Пост успешно сохранен в файл nexus_draft.txt")
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")