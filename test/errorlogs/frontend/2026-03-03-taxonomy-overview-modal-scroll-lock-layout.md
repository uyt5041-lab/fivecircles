# 2026-03-03 Taxonomy Overview Modal Scroll/Layout

- Timestamp: 2026-03-03 17:05 KST
- Page: `front/features/admin/components/TaxonomyOverviewModal.tsx`

## Symptom
- `Overview` 모달에서 배경 페이지는 lock 되었지만, 모달 내부 좌/우 패널이 끝까지 스크롤되지 않고 페이지 레이아웃만 움직이는 것처럼 보였다.

## Root Cause
- 원인은 preview API 자동 호출이 아니라, Tailwind 레이아웃에서 모달 본문 높이 상속이 끊겨 내부 컬럼이 scroll container로 성립하지 못한 것이었다.
- `max-h`만 두고 `flex-1 / min-h-0 / overflow-y-auto`를 맞추지 않아 자식이 콘텐츠 높이만큼 계속 늘어났다.

## Fix
- 모달 본체를 `flex-col`로 정리하고, 본문 래퍼에 `flex-1 min-h-0 overflow-hidden` 적용.
- 좌/우 컬럼에 각각 `min-h-0 overflow-y-auto`를 적용해 내부 스크롤만 타도록 고정.

## Prevention
- 모달/드로어 스크롤 이슈는 API 호출 원인으로 먼저 오진하지 말고, `body lock`과 `scroll container` 구조를 분리해서 확인한다.
- Tailwind 모달은 `max-h`만으로 끝내지 말고 `flex-col -> flex-1 -> min-h-0 -> overflow-y-auto` 체인을 기본 패턴으로 사용한다.
