import os
import requests
from bs4 import BeautifulSoup
import datetime
import time

# =========================
# 환경 변수
# =========================
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# =========================
# 디스코드 메시지 전송
# =========================
def send_message(msg: str):
    now = datetime.datetime.now()
    payload = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Discord send failed: {e}")
    print(payload)

# =========================
# KIAT 로봇 관련 공고 크롤링
# =========================
def get_kiat_robot_notices(max_count=5):
    url = "https://www.kiat.or.kr/site/notice/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            send_message(f"❌ KIAT 접속 실패, 상태코드: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        notices = []

        # 공고 리스트 추출 (사이트 구조에 맞게 class/id 확인)
        rows = soup.select("table tbody tr")  # 일반적으로 tbody > tr 구조
        for row in rows:
            title_tag = row.select_one("td.title a")
            date_tag = row.select_one("td.date")
            if title_tag and date_tag:
                title = title_tag.get_text(strip=True)
                date = date_tag.get_text(strip=True)
                link = "https://www.kiat.or.kr" + title_tag.get("href")
                # 로봇 관련 키워드 필터링
                if "로봇" in title or "Robot" in title:
                    notices.append(f"{date} | {title} | {link}")
            if len(notices) >= max_count:
                break
        return notices

    except Exception as e:
        send_message(f"❌ KIAT 크롤링 오류: {e}")
        return []

# =========================
# 메인 실행
# =========================
if __name__ == "__main__":
    robot_notices = get_kiat_robot_notices()
    if robot_notices:
        send_message("🤖 KIAT 최신 로봇 관련 공모사업 공고:")
        for notice in robot_notices:
            send_message(notice)
    else:
        send_message("🤖 KIAT 최신 로봇 관련 공고가 없습니다.")
