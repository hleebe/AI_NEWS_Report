import requests
import smtplib
import re
import os
from google import genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

SEARCH_KEYWORD = "유가"
MAX_NEWS_COUNT = 3


def clean_html(text):
    text = re.sub(r'<.*?>', '', text)
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&apos;', "'")
    return text


def fetch_naver_news(keyword, max_items=5):
    print(f"🔍 네이버에서 '{keyword}' 관련 뉴스 수집 중...")
    
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": keyword,
        "display": max_items,
        "sort": "date"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            return None
            
        news_list = []
        for item in items:
            title = clean_html(item['title'])
            link = item.get('originallink', item['link'])
            news_list.append(f"- 제목: {title}\n  링크: {link}")
            
        return "\n\n".join(news_list)
    except Exception as e:
        print(f"네이버 API 호출 오류: {e}")
        return None


def generate_ai_report(news_text, max_retries=3):
    print("리포트 생성하는 중...")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""당신은 전문 애널리스트입니다. 
제공된 뉴스 기사들을 분석하여 바쁜 경영진이 3분 안에 읽을 수 있는 '일일 트렌드 리포트'를 작성해 주세요.

[형식]
1. 💡 오늘의 핵심 요약 (3줄 이내)
2. 📰 주요 뉴스 상세 (각 기사별 핵심 요약 및 링크 포함)
3. 🎯 비즈니스 인사이트 (이 뉴스들이 비즈니스에 미치는 영향 1단락)

[수집된 네이버 뉴스 데이터]
{news_text}
"""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait_time = 2 ** attempt
                print(f"서버 과부하로 {wait_time}초 후 재시도합니다... ({attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Gemini API 오류: {e}")
                return None
    return None


def send_to_slack(report_text):
    print("슬랙으로 리포트 전송 중...")
    payload = {"text": report_text}
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("슬랙 전송 성공!")
        else:
            print(f"슬랙 전송 실패: 상태 코드 {response.status_code}")
    except Exception as e:
        print(f"슬랙 전송 중 오류 발생: {e}")


def main():
    print("=== 네이버-Gemini-슬랙 자동화 파이프라인 시작 ===")
    
    # 1. 뉴스 수집
    news_data = fetch_naver_news(SEARCH_KEYWORD, MAX_NEWS_COUNT)
    if not news_data:
        print("수집된 뉴스가 없습니다.")
        return

    # 2. AI 리포트 생성
    report = generate_ai_report(news_data)
    
    # 3. 결과 전송
    if report:
        send_to_slack(report)
        print("=== 모든 작업이 성공적으로 완료되었습니다 ===")
    else:
        print("리포트 생성 실패로 전송을 취소합니다.")


if __name__ == "__main__":
    main()
