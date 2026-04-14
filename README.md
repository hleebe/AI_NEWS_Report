# 🤖 AI Daily News Automation Bot

> 본 프로젝트는 네이버 뉴스의 최신 데이터를 수집하고, Google Gemini AI를 통해 핵심 인사이트를 추출하여, 슬랙(Slack)으로 자동 전송하는 비즈니스 자동화 파이프라인입니다.

## Key Features
- **Data Sourcing**: 네이버 검색 API를 활용한 실시간 뉴스 데이터 수집
- **AI Processing**: Google Gemini 최신 Flash 모델을 활용한 3줄 핵심 요약 및 비즈니스 인사이트 추출
- **Communication Automation**: 슬랙 웹훅(Webhook)을 통한 즉각적인 리포트 발행
- **Serverless Scheduling**: GitHub Actions를 활용하여 매일 아침 9시(KST) 완전 자동 실행

## Tech Stack
- **Language**: Python 3.10
- **AI**: Google Gemini API (`google-genai`)
- **Infrastructure**: GitHub Actions (CI/CD)
- **APIs**: Naver Search API, Slack Incoming Webhooks

## Pipeline Architecture
1. **Trigger**: GitHub Actions 스케줄러 (매일 아침 9시)
2. **Fetch**: Python 스크립트가 네이버 API에서 설정된 키워드(`하이닉스` 등)의 최신 뉴스 3개 수집
3. **Analyze**: Gemini AI가 뉴스 본문을 분석하여 경영진 보고용 리포트 생성
4. **Notify**: 생성된 리포트를 지정된 슬랙 채널로 전송

