# UI 패리티 감사 — Streamlit 8화면 vs Next.js (2026-06-15)

> 작성: 2026-06-15T18:27:03+09:00 · 관련: TASK-049 (UI 대개편 Phase 5) · 스펙 `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md`

## 목적

UI 대개편 Phase 1~5 빌드아웃 완료 후, 기존 Streamlit 8화면 대비 Next.js 앱의 기능 패리티를
점검한다. **Streamlit 은퇴 여부의 판단 근거**가 된다.

## 패리티 체크리스트 (8화면)

| # | 화면 | Streamlit | Next.js 경로 | 빌드 단계 | 패리티 | 비고 |
|---|------|-----------|-------------|-----------|--------|------|
| 1 | 홈(대시보드) | ✅ | `/home` | Phase 2 | ✅ | KPI·자산곡선·지수·보유미리보기·최근체결·제안 |
| 2 | 포트폴리오 | ✅ | `/portfolio` | Phase 2 | ✅ | HoldingsTable·배분차트·KPI·자산곡선 |
| 3 | 매매/주문 | ✅ | `/trade` | Phase 3 | ✅ | OrderForm(조건, 2단계 ack)·호가·run-once·킬/자동 |
| 4 | 내역·손익 | ✅ | `/history` | Phase 3 | ✅ | 주문로그·체결 |
| 5 | 분석 | ✅ | `/analysis` | Phase 5 | ✅ | CandleChart·백테스트·VaR·시나리오·기여도(Sankey) |
| 6 | 에이전트 | ✅ | `/agents` | Phase 4 | ✅ | 팀상태·Ask·IC live(SSE)·과거결정 |
| 7 | 알림 | ✅ | `/alerts` | Phase 4 | ✅ | 라이브 피드(SSE) · (워치리스트/스크리너/알림룰은 TASK-038 Streamlit 레이어) |
| 8 | 설정·연동 | ✅ | `/settings` | Phase 3 | △ | 리스크한도 PUT 연동; 계정/연결 탭은 표시 위주, 일부 설정 setter 미구현 |
| + | 로그인 | ✅ | `/login` | Phase 1 | ✅ | ID/PW + 게스트, §4.4 |

**기능 패리티: 8/8 화면 구현 완료** (설정 화면 일부 setter는 추후 보강 — 핵심 리스크한도는 연동됨).

## 안전 패리티 (불변식 §3)

| 항목 | Streamlit | Next.js | 일치 |
|------|-----------|---------|------|
| 직접 주문 엔드포인트 없음(run-once→OrderFlow→SafetyChecker 유일) | ✅ | ✅(POST /trade/orders 404) | ✅ |
| 킬스위치/자동매매 DB-backed | ✅ | ✅ | ✅ |
| 상태변경 require_owner+CSRF | n/a | ✅(guest 403, 무세션 401) | ✅ |
| 조건 저장 2단계 게이트(공시/컴플 ack) | ✅(뷰) | ✅(서버사이드 422/409+ack_token) | ✅ |
| 데몬 미기동(SSE 요청당, KIS WS opt-in OFF) | n/a | ✅ | ✅ |

## Streamlit 은퇴 — 판단 및 권고

**현 상태: 은퇴 보류 (Owner 결정 + paper 검증 선행 필요).**

은퇴(`app/ui/views` 아카이브 + AppTest 제거 + `backend.py`→`app/services` 역파사드 해소 + docker-compose
streamlit 제거)는 다음 이유로 **즉시 실행하지 않는다**:

1. **새 앱 미검증**: Next.js 앱은 **실 KIS paper 계정 수동 검증(Phase 3 Done-When)이 미완**. 작동하는
   안전망 UI를 검증 전 제거하는 것은 비가역적·임프루던트.
2. **파괴적 규모**: 은퇴는 **AppTest 32개 파일 제거**(상당한 커버리지 손실) + **`app.ui.backend` 패치
   의존 테스트 26개 파일 재배선** + backend 실구현 이동(스펙 §5 Phase 0가 의도적으로 Phase 5로 연기한 작업)을
   수반. 커버리지 게이트(≥50%)·회귀 위험 큼.
3. **되돌리기 비용**: 코드 삭제+테스트 제거는 git revert 외 복구 어려움.

### 은퇴 진행 조건 (충족 시 별도 태스크로)

- [ ] Owner가 `run_api.bat` + `run_frontend.bat`로 Next.js 앱을 **실 KIS paper 환경에서 수동 검증** 통과
- [ ] (설정 화면 잔여 setter 보강 등) 패리티 100% 확정
- [ ] 은퇴 시 커버리지 ≥50% 유지 방안(AppTest 제거분 보전) 확인
- [ ] Owner 명시 은퇴 승인

조건 충족 시: `app/ui/views` 아카이브 → AppTest 제거 → `backend.py`→`app/services` 실이동(26개 테스트 경로 갱신)
→ docker-compose streamlit 제거 → demo-walkthrough.spec.ts(게스트 8페이지 순회) green → CI 그린.

## 결론

UI 대개편 **빌드아웃(Phase 1~5 화면)은 8/8 완료**, 안전 불변식 패리티 확보. **Streamlit 은퇴만 Owner 게이트로 잔존**.
TASK-049는 빌드아웃·패리티 감사 완료, 은퇴 보류 상태로 기록.
