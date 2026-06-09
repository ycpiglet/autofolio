# Autofolio

**Autofolio**는 한국투자증권(KIS) Open API 기반 개인용 국장 자동매매 시스템이다.
최종 지향점은 단순 자동매매 봇이 아니라 **에이전트 기반 개인 투자 운용체계(Agentic Quant Portfolio OS)**다.

현재 기본 실행 모드는 `mock`이다.  
즉, 실제 주문이 나가지 않는다.

## 핵심 목표

- 국장 ETF/대형주 화이트리스트 관리
- 목표 가격 도달형 매수/매도 조건 설정
- 기본 안전조건 검사
- Mock Broker 기반 주문 흐름 검증
- SQLite 로그 저장
- Streamlit UI 관제
- Telegram 알림 확장
- 한투 Open API 어댑터 확장 준비

## 빠른 시작: Windows PowerShell

```powershell
cd autofolio
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python scripts/init_db.py
python scripts/seed_sample_data.py
streamlit run app/ui/streamlit_app.py
```

## 테스트 실행

```powershell
pytest
```

## 현재 안전 기본값

- `KIS_ENV=mock`
- 자동주문 기본값 OFF
- 실 API 주문부는 바로 주문하지 않도록 어댑터 형태
- Kill Switch 제공
- Mock API 통합 테스트 포함

## 다음 개발 순서

1. 한투 Open API 모의투자 키 발급
2. `.env`에 모의투자 키 입력
3. `app/brokers/kis/kis_client.py`의 TODO 부분을 공식 문서 기준으로 구현
4. 현재가 조회부터 검증
5. 주문은 모의투자에서만 먼저 검증
6. 실전은 1주 수동 버튼 테스트 후 단계적으로 진행

## 주의

이 프로젝트는 개발용 스캐폴딩이며 투자 권유, 수익 보장, 실전 자동매매 안전 보장을 의미하지 않는다.  
실 API 주문 코드를 구현할 때는 반드시 모의투자와 소액 실전 테스트를 거쳐야 한다.
