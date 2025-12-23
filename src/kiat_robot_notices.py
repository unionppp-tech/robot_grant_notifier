#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import datetime

# =========================
# 필수 라이브러리 자동 설치
# =========================
def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

try:
    import requests
except ImportError:
    install("requests")
    import requests

# =========================
# 환경 변수
# =========================
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DATA_GO_KR_API_KEY = os.environ.get("DATA_GO_KR_API_KEY")

API_URL = "https://apis.data.go.kr/1371000/rdBizPbancInfoService/getRdBizPbancInfoList"

KEYWORDS = ["로봇", "robot", "자동화", "ai"]

# =========================
# 디스코드 메시지 전송
# =========================
def send_message(msg):
    now = datetime.datetime.now()
    payload = {"content": f"[{now:%Y-%m-%d %H:%M:%S}] {msg}"}
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    print(msg)

# =========================
# 국가 R&D 공고 조회 (공공데이터 API)
# =========================
def fetch_robot_rd_projects():
    params = {
        "serviceKey": DATA_GO_KR_API_KEY,
        "pageNo": 1,
        "numOfRows": 50,
        "type": "json"
    }

    res = requests.get(API_URL, params=params, timeout=10)
    res.raise_for_status()

    body = res.json().get("response", {}).get("body", {})
    items = body.get("items", {}).get("item", [])

    results = []
    for it in items:
        title = it.get("pbancNm", "")
        org = it.get("pbancInstNm", "")
        url = it.get("pbancUrl", "")
        start = it.get("rcptBgngYmd", "")
        end = it.get("rcptEndYmd", "")

        if any(k in title.lower() for k in KEYWORDS):
            results.append(
                f"[{org}]\n"
                f"{title}\n"
                f"접수기간: {start} ~ {end}\n"
                f"{url}"
            )

    return results

# =========================
# 메인 실행
# =========================
if __name__ == "__main__":
    projects = fetch_robot_rd_projects()

    if not projects:
        send_message("🤖 최근 로봇 관련 국가 R&D 공모사업이 없습니다.")
    else:
        send_message("🤖 로봇 관련 국가 R&D 공모사업")
        for p in projects[:5]:
            send_message(p)
