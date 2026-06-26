/**
 * finance-roadmap-labels.ts
 * Static display labels for the FinanceRoadmapPanel.
 *
 * Rules (TASK-174 gate):
 * - All strings are neutral/descriptive.
 * - No recommendation, advice, order, or action wording.
 * - Unit-tested in finance-roadmap-wording.test.ts for forbidden phrases.
 */

export const ROADMAP_LABELS = {
  pageTitle: "재무 로드맵 미리보기",
  previewBadge: "미리보기 / 데모 데이터",
  previewNote:
    "합성 픽스처 기반 읽기 전용 계획 미리보기입니다. 실제 포트폴리오 사실·세무회계 자문이 아닙니다.",

  // Plan vs Expected section
  sectionPlanVsExpected: "계획 대비 예상 비교",
  labelPlanned: "계획 수익률",
  labelExpectedRange: "예상 수익률 범위",
  labelConfidence: "신뢰도",
  labelHorizon: "기획 지평",
  notGuaranteedNote: "시나리오 범위이며, 수익은 보장되지 않습니다.",

  // Gap section
  sectionGap: "갭 현황",
  labelGapLow: "갭 하단 (퍼센트포인트)",
  labelGapHigh: "갭 상단 (퍼센트포인트)",

  // Allocation drift
  sectionAllocationDrift: "배분 편차",

  // Timeline candidates
  sectionTimeline: "검토 후보 일정",
  labelHorizonItem: "지평",
  labelTrigger: "트리거 조건",
  labelRequiredEvidence: "필요 증거",
  tagCandidateOnly: "Owner 검토 후보",
  tagBlockedAction: "현재 조치 불가",

  // Review candidates
  sectionReview: "검토 후보 항목",
  labelWhyFlagged: "플래그 사유",
  labelMissingEvidence: "누락 증거",
  tagNoTradeInstruction: "거래 지시 없음",

  // Data quality / operations gaps
  sectionDataQuality: "운영 지원 갭",
  labelMissingItem: "누락 항목",
  tagOwnerDecision: "Owner 결정 필요",

  // Boundary note
  boundaryNote:
    "이 데이터는 Owner 전용 검토 자료입니다. 투자·세무·법적 자문이 아닙니다.",

  // Loading / error states
  loadingText: "로드맵 데이터를 불러오는 중...",
  authPendingText: "인증 확인 중...",
  errorTitle: "데이터를 불러오지 못했습니다.",
  unauthorizedText: "이 페이지는 로그인이 필요합니다.",
} as const;

export type RoadmapLabelKey = keyof typeof ROADMAP_LABELS;
