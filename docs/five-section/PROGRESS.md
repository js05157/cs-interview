# 다섯 절 개편 진행 · 2026-10-29

사용자가 승인한 샘플 구조를 100개에 적용하고 질문별 답변과 클릭 UI를 통합하는 중입니다. 공개 첫 ID 같은 URL·날짜·Notion 페이지 개정/재배포는 승인됐으며 신규 CS 주제 공개와 CS_AUTO_PUBLISH 활성화는 금지입니다.

- 안전한 원본 문법: H2 정의/설명/적용 예시/정리/꼬리 질문, 질문은 H3 Q1. …와 답변, 출처는 하단 divider + 굵은 참고 자료. 임의 HTML은 계속 거부합니다.
- 렌더 버전 3에서만 질문·답변을 신뢰할 수 있는 details/summary로 생성합니다. 기본 닫힘·서로 독립·키보드 기본 동작·테마 CSS를 사용합니다. 이전 렌더 버전과 Notion 관리 블록 fingerprint는 호환됩니다.
- Notion은 같은 질문·답변 파서를 사용해 관리 chunk 안의 질문별 Toggle로 변환합니다. 코드·인라인 코드·링크 순서와 내용을 유지합니다.
- 이전 개정 metadata는 revision_history에 보존합니다. 같은 페이지의 이전 블록 대조 → 새 블록 검증 → 알려진 이전 블록만 archive하는 복구 계약을 유지합니다.
- Python 73개 통과: 원본 HTML 차단, 불완전 구조 거부, code fence 안 가짜 질문 제외, 안전한 생성, 두 번의 응답 유실과 같은 페이지 재실행 포함. 승인된 첫 글 로컬 fixture 실제 Jekyll 빌드 성공(HTML 10개/글 1개). 실제 운영 결과는 아직 완료로 기록하지 않습니다.
- 비공개 OS 10개·질문 21개 배치 검증과 Java 5/Python 4 실행 통과, private commit 6b2e80c. 다음 분야는 Network이며 최신 숫자는 private manifests/five_section_checkpoint.json을 기준으로 합니다.

원본 보존 태그는 두 저장소의 pre-five-section-20261029입니다. 공개 백업에는 이미 공개된 첫 글만 보관합니다. 다른 99개나 비공개 카탈로그를 공개 Git에 복사하지 않습니다.
