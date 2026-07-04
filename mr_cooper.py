import os
import time
import schedule
import subprocess
from datetime import datetime

# ==========================================
# 🐕 MR. COOPER - THE WATCHDOG
# ==========================================
PYTHON_EXEC = ".venv/bin/python"
AGENCY_SCRIPT = "news_agency.py"
SENDER_SCRIPT = "nexus_sender.py"
DRAFT_FILE = "nexus_draft.txt"

MAX_RUNTIME_SECONDS = 600  # 10 минут максимальной работы Агентов

def bulldog_log(message):
    """Фирменный лай мистера Купера (логгирование)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[🐕 MR. COOPER | {timestamp}] {message}")

def run_publishing_cycle():
    bulldog_log("🐾 Время пришло! Выпускаю Отдел Кадров Q NEXUS...")
    
    # Даем максимум 2 попытки (оригинальная + 1 шанс на перезапуск)
    for attempt in range(1, 3):
        bulldog_log(f"🔄 Попытка {attempt} из 2...")
        
        try:
            # Запускаем Издательский Дом и ждем (с таймером)
            subprocess.run(
                [PYTHON_EXEC, AGENCY_SCRIPT],
                timeout=MAX_RUNTIME_SECONDS,
                check=True
            )
            
            # Если скрипт завершился успешно, проверяем наличие черновика
            if os.path.exists(DRAFT_FILE):
                bulldog_log("✅ Черновик найден! Агенты справились. Передаю логистам...")
                subprocess.run([PYTHON_EXEC, SENDER_SCRIPT], check=True)
                bulldog_log("🏁 Цикл публикации полностью и успешно завершен. Иду спать.")
                return  # Успех, выходим из цикла попыток
            else:
                bulldog_log("⚠️ Скрипт отработал, но файл nexus_draft.txt не появился!")
                
        except subprocess.TimeoutExpired:
            bulldog_log("⏳ Агенты зависли в облаках (превышен лимит 10 минут). Жестко завершаю процесс!")
        except subprocess.CalledProcessError as e:
            bulldog_log(f"💥 Произошла системная ошибка в Отделе Кадров: {e}")
            
        # Если мы дошли сюда, значит попытка провалилась
        if attempt == 1:
            bulldog_log("🔁 Даю им второй (и последний) шанс. Перезапуск...")
            time.sleep(5)  # Небольшая пауза перед рестартом
        else:
            bulldog_log("❌ Вторая попытка провалена. Отменяю выпуск. Жду следующего времени по расписанию.")

def setup_schedule():
    # Настраиваем расписание мистера Купера
    schedule.every().day.at("11:00").do(run_publishing_cycle)
    schedule.every().day.at("15:00").do(run_publishing_cycle)
    schedule.every().day.at("20:00").do(run_publishing_cycle)
    
    bulldog_log("Бульдог заступил на пост. Расписание: 11:00, 15:00, 20:00.")
    bulldog_log("Жду своей смены...")

if __name__ == "__main__":
    setup_schedule()
    
    # Бесконечный цикл ожидания (сам скрипт Купера работает всегда и не ест память)
    while True:
        schedule.run_pending()
        time.sleep(30)  # Проверяем часы каждые полминуты