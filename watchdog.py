import os
import time
import subprocess
import signal
import sys
import socket

# ==========================================
# 🛠 НАЛАШТУВАННЯ Q-PULSE WATCHDOG
# ==========================================
TARGET_SCRIPT = "q_pulse.py"
FILES_TO_WATCH = ["q_pulse.py"]
DEBOUNCE_DELAY = 2.0  

# ==========================================
# 📡 БАЗОВА ПЕРЕВІРКА МЕРЕЖІ
# ==========================================
def has_internet():
    """Стукає до Google DNS, щоб перевірити наявність інтернету"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def wait_for_internet():
    """Тримає скрипт на паузі, якщо Мак пішов у сон або зник інтернет"""
    if has_internet(): return True
    
    print("🛑 [Q-PULSE] Немає мережі. Можливо, Мак щойно прокинувся. Чекаю...")
    while not has_internet():
        print("⏳ Мережі немає. Перевірка через 5 сек...")
        time.sleep(5)
    print("✅ [Q-PULSE] Інтернет стабільний! Продовжуємо.")
    return True

# ==========================================
# 🤖 КЕРУВАННЯ КОНВЄЄРОМ
# ==========================================
def get_latest_mtime(files):
    max_mtime = 0
    for f in files:
        if os.path.exists(f):
            mtime = os.path.getmtime(f)
            if mtime > max_mtime: max_mtime = mtime
    return max_mtime

def start_bot():
    print(f"\n🚀 [Q-PULSE] Запуск новинного конвеєра {TARGET_SCRIPT}...")
    # Використовує віртуальне середовище саме з папки qpulse
    return subprocess.Popen([sys.executable, TARGET_SCRIPT])

def stop_bot(process):
    if process and process.poll() is None:
        print(f"\n🛑 [Q-PULSE] М'яка зупинка конвеєра...")
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

# ==========================================
# 🧠 ГОЛОВНИЙ ЦИКЛ
# ==========================================
if __name__ == "__main__":
    print(f"👁️ [Q-PULSE WATCHDOG] Термінал управління новинами запущено.")
    
    wait_for_internet()
    last_mtime = get_latest_mtime(FILES_TO_WATCH)
    bot_process = start_bot()

    try:
        while True:
            time.sleep(1)
            current_mtime = get_latest_mtime(FILES_TO_WATCH)
            
            # 🛡 Перевірка 1: Зміна коду (Гаряче перезавантаження)
            if current_mtime > last_mtime:
                print("\n🔄 [Q-PULSE] Змінено код. Перезапуск...")
                time.sleep(DEBOUNCE_DELAY) 
                last_mtime = get_latest_mtime(FILES_TO_WATCH)
                
                stop_bot(bot_process)
                wait_for_internet() 
                bot_process = start_bot()
                continue
                
            # 🛡 Перевірка 2: Скрипт впав (або Мак вийшов зі сну)
            if bot_process.poll() is not None:
                print("\n⚠️ [Q-PULSE] Конвеєр зупинився. Перевіряю мережу...")
                wait_for_internet() # Не дасть крутити "білку в колесі", якщо немає інету
                
                print("🔄 [Q-PULSE] Роблю рестарт...")
                time.sleep(DEBOUNCE_DELAY)
                bot_process = start_bot()
                
    except KeyboardInterrupt:
        print("\n🚪 [Q-PULSE] Вимкнення новинного штабу...")
        stop_bot(bot_process)
        sys.exit(0)