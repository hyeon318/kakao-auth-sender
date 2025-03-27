import pygetwindow as gw
import pyautogui
import pyperclip
import time
import threading
import json
import os
import sys
import msvcrt
import random
from datetime import datetime

stop_flag = False
SAVE_FILE = "stop_index.json"
MESSAGE_FILE = "message.txt"
init_pos = None  # ✅ 초기 마우스 위치 글로벌 변수로 선언

# ✅ 사용자 개입 감지 (ESC, 키보드, 마우스)
def user_interrupt_monitor():
    global stop_flag
    global init_pos
    tolerance = 3  # 좌표 변화 허용 범위 (픽셀 수)

    while True:
        if init_pos is None:
            time.sleep(0.1)
            continue

        current_pos = pyautogui.position()
        dx = abs(current_pos.x - init_pos.x)
        dy = abs(current_pos.y - init_pos.y)
        if dx > tolerance or dy > tolerance:
            print("\n🛑 [중단] 마우스 움직임 감지 → 자동화 중단")
            stop_flag = True
            break

        if msvcrt.kbhit():
            key = msvcrt.getch()
            print(f"\n🛑 [중단] 키보드 입력 감지 ({key}) → 자동화 중단")
            stop_flag = True
            break

        time.sleep(0.1)

# ✅ 메시지 한 번에 복사/붙여넣기
def send_multiline_message(message):
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')

# ✅ 카카오톡 창 포커스
def activate_kakao():
    kakao = gw.getWindowsWithTitle('카카오톡')
    if kakao:
        kakao[0].activate()
        time.sleep(1)
    else:
        print("❌ 카카오톡 창을 찾을 수 없습니다.")
        sys.exit()

# ✅ 친구 탭 클릭 (카카오톡 창 기준 상대 위치)
def click_friend_tab_relative():
    global init_pos
    kakao = gw.getWindowsWithTitle('카카오톡')[0]
    x, y = kakao.left, kakao.top
    friend_tab_x = x + 40
    friend_tab_y = y + 50
    pyautogui.click(friend_tab_x, friend_tab_y)
    time.sleep(1)
    init_pos = pyautogui.position()  # ✅ 클릭 후 위치를 초기값으로 설정

def is_kakao_running():
    kakao = gw.getWindowsWithTitle('카카오톡')
    return len(kakao) > 0

def save_stop_index(index, total_count):
    with open(SAVE_FILE, "w") as f:
        json.dump({"last_index": index, "total_count": total_count}, f)

def load_stop_index():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_index", 0), data.get("total_count", 0)
    return 0, 0

def clear_stop_index():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

# ✅ 메시지 전송
def send_message_to_friends(name_keyword, message, start_index=0, total_count=5):
    global stop_flag
    activate_kakao()
    click_friend_tab_relative()

    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)

    for _ in range(20):
        pyautogui.press('backspace')
        time.sleep(0.05)

    pyperclip.copy(name_keyword)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)

    for _ in range(start_index):
        pyautogui.press('down')
        time.sleep(0.3)

    print(f"\n[시작] {start_index + 1}번째 친구부터 메시지 전송 시작\n")
    start_time = datetime.now()
    print(f"🕒 전송 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    for i in range(start_index, total_count):
        if stop_flag:
            print(f"\n🛑 [중단됨] {i + 1}번째 친구 전송 전 중단되었습니다.")
            save_stop_index(i, total_count)
            return

        if not is_kakao_running():
            print(f"\n❌ [오류] 카카오톡 창이 사라졌습니다. {i + 1}번째에서 중단합니다.")
            save_stop_index(i, total_count)
            return

        try:
            pyautogui.press('enter')
            time.sleep(1)

            send_multiline_message(message)
            print(f"📤 {i + 1}번째 메시지 전송 완료")
            time.sleep(random.uniform(1.2, 2.5))

            pyautogui.press('esc')
            time.sleep(0.3)
            pyautogui.press('down')
            time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            print(f"\n❌ [오류] {i + 1}번째에서 예외 발생: {e}")
            save_stop_index(i, total_count)
            return

        if stop_flag:
            print(f"\n🛑 [중단됨] {i + 1}번째 친구까지 전송 완료 후 중단되었습니다.")
            save_stop_index(i + 1, total_count)
            return

    end_time = datetime.now()
    print("\n✅ [완료] 메시지 전송이 종료되었습니다.")
    print(f"🕒 전송 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("👉 창을 닫으려면 아무 키나 누르세요.")
    input()
    clear_stop_index()

# ✅ 프로그램 시작점
if __name__ == "__main__":
    print("✨ 카카오톡 자동 메시지 발송기 ✨")
    print("(ESC, 마우스 움직임, 키보드 입력 시 자동 중단됩니다)\n")

    keyword = input("🔍 검색할 키워드를 입력하세요: ")

    if not os.path.exists(MESSAGE_FILE):
        print(f"❌ 메시지 파일이 존재하지 않습니다: {MESSAGE_FILE}")
        print("📄 먼저 message.txt 파일을 만들고 메시지를 작성해 주세요.")
        sys.exit()

    with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
        message = f.read()

    print("\n📄 메시지 파일 내용 미리보기:\n───────────────────────────")
    print(message)
    print("───────────────────────────")

    start_index = 0
    total_count = 0
    if os.path.exists(SAVE_FILE):
        last_index, saved_total = load_stop_index()
        print(f"\n📌 이전에 {last_index + 1}번째에서 중단된 기록이 있습니다.")
        resume = input("⏩ 이어서 다시 시작할까요? (Y/N): ").strip().lower()
        if resume == "y":
            start_index = last_index
            total_count = saved_total

    if total_count == 0:
        while True:
            try:
                if start_index == 0:
                    start_index = int(input("⏱️ 몇 번째 친구부터 시작할까요? (예: 0): "))
                total_count = int(input("📦 총 몇 명에게 보내기를 원하세요? (예: 5): "))
                break
            except ValueError:
                print("❗ 숫자를 정확히 입력해주세요!")

    monitor_thread = threading.Thread(target=user_interrupt_monitor, daemon=True)
    monitor_thread.start()

    send_message_to_friends(keyword, message, start_index, total_count)
