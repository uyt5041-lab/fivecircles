# Production Q1-Q15 List

1. 월터의 첫 살인?
2. 첫 암페타민 제조?
3. 투코를 처음 만나는 시점?
4. 스카일러가 월터의 범죄 사실을 알아차린 시점? (REVEALS)
5. 월터가 처음 ‘범죄’ 결심한 순간?
6. 월터와 제시가 처음 파트너가 된 계기?
7. 월터가 처음 거짓말을 들키는 순간?
8. 월터의 ‘명분(가족)’이 처음 흔들리는 지점?
9. 행크가 수사 방향을 크게 바꾸는 계기?
10. 월터가 처음 본격적인 위협을 받는 순간?
11. 누가 월터를 의심하기 시작한 최초 시점?
12. 월터가 처음 통제권을 쥐는 순간?
13. 월터가 처음 돈의 흐름을 만들기 시작한 사건?
14. 스카일러-월터 관계가 돌이키기 어려워지는 첫 균열?
15. 월터가 본격적으로 은폐/도주를 시작하는 최초 지점?

## 참고(정합성/재사용)
- Predicate 그룹/승격/확장(질문 구현 + 유지보수): `fivecircles/architecture/specs/predicate/README.md`
- Production Q1~Q15 구현 라우팅(시범용): `fivecircles/architecture/specs/predicate/ex16-q1-q15-구현-라우팅-시범용.md`
- REVEALS 분류(표준/용어 충돌 정리, 통합 포인트): `fivecircles/architecture/specs/reveals/reveals-classification.md`
- REVEALS 재사용 케이스(정책/설명/랭킹/리캡 예시): `fivecircles/architecture/specs/reveals/reveals-reuse-cases.md`

---

프로덕션 서비스 단계의 질문


좋아. 네가 만든 1–15 질문을 “API 파라미터(필터) 형태”로 변환하고, 그 다음 **지금 V2.5에 이미 있는 로직(api3/api7/api8/api9 + PRECEDES BFS)**이랑 “겹치는 것 / 부족한 것”을 딱 비교해볼게.(전제: V2.5 통합 스펙 기준으로 episode_end <= K + APPROVED 게이트는 전부 자동 적용.)

A) 질문 → 필터링 로직(=API 호출 형태)
아래 표기는 “QA 서비스단 라우터가 만들어낼 정규화된 QuerySpec” 형태로 볼 수 있어:
* 공통: { dramaId, K, limit, order }
* 캐릭터 기반: characterIds[]
* 사건 유형: predicateCodes[]
* “최초” 질문: order=EARLIEST, limit=1
* “원인/결과”: api7/8로 PRECEDES BFS
1) 월터의 첫 살인?
* QueryType: CHARACTER_EVENTS (api3)
* Params:
    * characterIds=[Walter]
    * predicateCodes=[KILLS] (또는 사내 코드가 있다면 FIRST_KILL)
    * order=EARLIEST, limit=1
* Fallback(설명 강화): 결과 이벤트 E를 잡은 뒤 api7(causes, depth=1~2)로 “직전 계기” 붙이기
2) 첫 암페타민 제조?
* QueryType: CHARACTER_EVENTS (api3)
* Params:
    * characterIds=[Walter]
    * predicateCodes=[PRODUCES_DRUG] (또는 COOKS)
    * order=EARLIEST, limit=1
* 주의: “암페타민”처럼 물질명은 V2.5에 구조화 필터가 없으니, 현재는 summary/content 텍스트로만 판별(=QA 라벨링에서 요약문에 물질명 표준화)
3) 투코를 처음 만나는 시점?
* QueryType: CHARACTER_AND_CHARACTER_EVENTS (공동 등장, api4 또는 coevents)
* Params:
    * characterA=Walter, characterB=Tuco
    * order=EARLIEST, limit=1
* 보강: 공동 등장 사건 중 MEETS/INTRODUCES 같은 predicate가 있으면 그걸 우선, 없으면 “최초 coevent”가 곧 “처음 만남”으로 간주(보수적 규칙)
4) 스카일러가 월터의 범죄 사실을 알아차린 시점?
* QueryType: REVEALS 기반 검색 (현재 스펙상 REVEALS는 “설명용”으로만 유지)
* 그래서 V2.5에서 실제로 굴릴 수 있는 보수적 라우팅:
    * 1차: CHARACTER_EVENTS (api3) with
        * characterIds=[Skyler]
        * predicateCodes=[DISCOVERS, SUSPECTS, CONFRONTS, CONFESSES] 같은 “인지 변화” 계열 묶음(없으면 운영자가 지정한 최소 세트)
        * order=EARLIEST, limit=1
    * 2차(설명): 해당 이벤트 E의 event_reveal을 읽어 “무엇이 드러났는지” 텍스트로 붙인다(노출 판단은 여전히 event의 episode range로)

B) 5–15 (내가 만든 질문들)도 같은 방식으로 “QuerySpec”으로 박기
여기선 실사용 빈도 높은 것만, 딱 11개를 QuerySpec으로 고정해둘게.
5) 월터가 처음 ‘범죄’ 결심한 순간?
* api3: characterIds=[Walter]
* predicateCodes=[DECIDES, COMMITMENT, CROSSES_LINE]
* order=EARLIEST, limit=1
* 없으면 fallback: predicateCodes=[PRODUCES_DRUG, FIRST_DEAL]로 “행동 기준 첫 전환”으로 대체
6) 월터와 제시가 처음 파트너가 된 계기?
* api4(coevents): A=Walter, B=Jesse, order=EARLIEST, limit=3
* 그 중 predicateCodes=[PARTNERS_WITH, AGREES, DEAL] 우선 선택
* 계기는 api7(causes) depth=1 붙이기
7) 월터가 처음 거짓말을 들키는 순간?
* api3: characterIds=[Walter]
* predicateCodes=[LIE_EXPOSED, CONFRONTED]
* order=EARLIEST, limit=1
8) 월터의 ‘명분(가족)’이 처음 흔들리는 지점?
* api3: characterIds=[Walter]
* predicateCodes=[MOTIVE_SHIFT, SELFISH_REVEALED, CONFLICT_WITH_FAMILY]
* order=EARLIEST, limit=1
* (이건 QA에서 “요약문 분기점 테스트”로 아주 좋아)
9) 행크가 수사 방향을 크게 바꾸는 계기?
* api3: characterIds=[Hank]
* predicateCodes=[INVESTIGATES, CASE_TURNING_POINT, NEW_LEAD]
* order=EARLIEST, limit=1
* 계기: api7 depth=1
10) 월터가 처음 본격적인 위협을 받는 순간?
* api3: characterIds=[Walter]
* predicateCodes=[THREATENED, BLACKMAILED, TARGETED]
* order=EARLIEST, limit=1
11) 누가 월터를 의심하기 시작한 최초 시점?
* api3: characterIds=[Walter]만으론 “누가”가 안 나옴
* 보수적 라우팅:
    1. api3: characterIds=[Walter], predicateCodes=[SUSPECTS], order=EARLIEST, limit=10
    2. 결과 이벤트들의 등장인물은 api5(event characters)로 뽑아 “의심 주체 후보”를 표시
* (스펙 내에서 가능한 범위로 “누가”를 근사)
12) 월터가 처음 통제권을 쥐는 순간?
* api3: characterIds=[Walter]
* predicateCodes=[GAINS_CONTROL, TAKES_CHARGE, DOMINATES]
* order=EARLIEST, limit=1
13) 월터가 처음 돈의 흐름을 만들기 시작한 사건?
* api3: characterIds=[Walter]
* predicateCodes=[FIRST_DEAL, GETS_PAID, SELLS_PRODUCT]
* order=EARLIEST, limit=1
14) 스카일러-월터 관계가 돌이키기 어려워지는 첫 균열?
* api4(coevents): A=Walter, B=Skyler, order=EARLIEST, limit=10
* 그 중 predicateCodes=[BETRAYAL, MAJOR_CONFLICT, BREAKDOWN] 우선
15) 월터가 본격적으로 은폐/도주를 시작하는 최초 지점?
* api3: characterIds=[Walter]
* predicateCodes=[COVERS_UP, HIDES_EVIDENCE, EVADES]
* order=EARLIEST, limit=1

C) “이미 있는 로직”과 비교: 겹침/부족/추가 설계 포인트
이미 V2.5로 바로 커버되는 것
* “A 타임라인 + 유형 필터” = api3 + predicateCode
    * 1,2,5,7,8,9,10,12,13,15 대부분 여기로 떨어짐
* “원인/결과” = api7/api8 (PRECEDES BFS)
    * “계기” 붙이기(1~2 hop) 매우 강력
* “관련 인물” = api9 (shared character 파생)
    * 적대/협력자도 여기서 기본 뼈대가 나옴(아래에서 더)
현재 스펙에서 약한 것(=QA 라우터에서 보수적 규칙 필요)
* “누가 알아차렸나/누가 의심했나” 같은 주체 추출
    * REVEALS는 설명용이라 “정답 검색 키”로는 약함
    * 그래서 “SUSPECTS 계열 이벤트를 먼저 찾고 → event characters로 주체 후보를 붙이는” 방식이 안전함
* “첫 만남(3)”도 결국 coevents 기반 근사(스펙 내에서 가장 안전)

D) “월터의 적대 캐릭터/조직/협력자”는 어떻게 할까?
1) 협력자(=동맹/파트너/같이 움직이는 사람)
스펙에 이미 있는 가장 안전한 길:
1. 기본 리스트: api9(related characters)로 “월터 관련 인물” 뽑기
2. 협력자 판정 필터: 월터와 해당 인물 B의 coevents(api4) 중
    * predicateCodes in [PARTNERS_WITH, DEAL, COOPERATES, HELPS] 비율/빈도 높으면 “협력자”로 라벨
3. 표시: “협력자(확실)” / “협력자(가능)” 2단계(보수적)
장점: 스키마 변경 0, 전부 event + predicate + coevent로만 굴러감.
2) 적대자(=대립/위협/충돌하는 사람)
동일한 구조로 “반대 방향” predicate를 쓰면 된다:
1. api9로 후보군 뽑기
2. coevents에서
    * predicateCodes in [THREATENED, ATTACKED, BETRAYAL, CONFLICT, BLACKMAIL]가 강하면 “적대” 라벨
3) “조직”은? (ERD에 조직 엔티티가 없으니, 스키마 안 바꾸는 답)
여기서 선택지는 딱 2개인데, 요구사항 보수 해석 기준으로 하나만 고르면:
✅ 조직을 ‘Character’로 취급 (데이터로만 처리)
* DEA, 카르텔, 갱단 같은 걸 character.display_name으로 넣는다. (사람과 동일 테이블)
* 그러면:
    * “월터 vs 조직”도 그냥 coevents(Walter, DEA)로 처리 가능
    * “소속 변경”도 AFFILIATION_CHANGE 이벤트에 “Walter ↔ DEA”를 involvedCharacters로 엮어버리면 됨
* 스키마 변경 없음, QA/검색/API 전부 그대로 재사용
(버린 이유) ❌ 별도 Organization 테이블 신설은 스펙 밖이고, 지금 단계에서 구현 리스크만 커짐.

E) 성능 최적화(멀티유즈): coevents N+1 제거용 집계 엔드포인트 1개 추가
현재 구조(api9로 후보 뽑기 + 후보별 coevents 호출)는 `1 + 후보수` 만큼 호출이 필요해진다.
프로덕션/QA에서 “적대자/협력자/관계성” 질문이 늘어나면 병목이 되므로, 아래 1개 엔드포인트로 흡수한다.

* API(제안): `GET /api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode={K}&limit={N}&mode={MODE}`
* MODE 예시:
  - `ADVERSARY`: 전투/배신/위협 그룹 카운트 기반(적대자)
  - `ALLY`: 동맹/합류/도움 그룹 카운트 기반(협력자)
* 응답 예시(개념): `{ otherCharacterId, score, countsByGroup, evidenceEventIds? }[]`
* 그룹/폴백(정합성): `predicate_code` 합집합으로 1차 분류하고, `predicate_code='OTHER'`인 경우 `predicate_suggestion` 키워드(예: BATTLE/DEATH/EXIT/AFFILIATION_CHANGE)를 해당 그룹으로 폴백 매핑해 집계에 포함한다.

원하면 다음 액션으로 바로 간다:
1. 위 1–15를 고정 QA 버튼 셋(Q1~Q15)과 1:1로 매핑해서, /qa 화면에서 어떤 위젯이 어떤 API를 때리는지까지 “구현 체크리스트”로 뽑아줄게.









===


