 요청한 “V3 구현(레벨 4 관점)” 기준으로 추가로 필요한 것들을 정리하면 아래야. 핵
  심은 저장 포맷이 아니라 ‘신호(라벨/지표)’ 추가라는 점이야. (refs: fivecircles/
  architecture/specs/event-v3-definition.md, fivecircles/architecture/proposals/
  공유-온톨로지레이어구축/ex05-lv4.md, fivecircles/architecture/proposals/공유-온
  톨로지레이어구축/Ex07-stepsformigration(editing).md)

  레벨 4 질문별 최소 신호

  - Q16 “중요 인물 부상”: event_metric.importance_score (또는 동등한 파생 점수)
  - Q17 “예고된 사건”: event_relation.type = FORESHADOWS + 노출은 카운트/축만
  - Q18 “인물 관점 재구성”: event_character.role (SUBJECT/OBJECT/ALLY/ENEMY 등)
  - Q19 “갈등 축 묶기”: event_axis_tag(event_id, axis_code)
  - Q20 “카테고리 분포”: event.predicate_code + 캐릭터 참여 집계

  현재 V2 기반에서 V3로 가기 위해 필요한 실제 작업

  - DB 마이그레이션
      - event_character.role 컬럼 추가 + 인덱스 (plan에 명시)
      - event_axis_tag 테이블 신설
      - event_metric 테이블 신설(importance_score 등)
      - event_relation.type에 FORESHADOWS 사용 규칙 정의(스키마는 그대로)
  - Mapper/Service 로직
      - event_character insert/select에 role 반영
      - Event 생성 시 role 기본값 정합(INVOLVED 등) 맞추기
      - axis/metric 저장 경로 추가 (wiki 승인/리뷰 단계에서 입력)
  - API/쿼리
      - 축별 조회, 중요도 기반 조회, 관점 재구성 뷰 등 레벨4 전용 API 또는 기존
        API 확장
      - FORESHADOWS는 BFS에 포함시키지 말고 “미래 디테일 노출 금지” 정책 유지
  - 운영 룰
      - episode_end <= K + source_status=APPROVED 게이트 유지(레벨4도 동일)

  요약하면, 프리디켓만으로는 레벨4 질문 대부분이 해결되지 않아. role + axis_tag +
  metric + foreshadows가 최소 추가 세트고, 이게 V3 구현의 실제 코어야.
  원하면 이 중에서 “오늘 구현 범위”를 좁혀서(예: role+axis_tag까지만) 진행 순서도
  잡아줄게.


› 그럼 실제 인물a가 중요인물로 부상하는시점이 언제냐? 라는 질문을 던졌을때 답을
  내놓는 로직이 어떻게되니


• 캐릭터 A가 중요한 인물로 부상하는 시점은 에피소드 내에서 이벤트 별 중요도를 계
  산한 후, 누적 중요도가 일정 임계값을 넘거나 드라마 참여도 순위가 상승하는 첫 번
  째 이벤트로 정의합니다. 중요도는 event_metric.importance_score, event_character
  역할, predicate_code, reveal_count, centrality 등을 가중치로 합산하며,
  episode_end ≤ K 및 source_status=APPROVED 조건으로 안전하게 필터링합니다.

  MVP 알고리즘은 이벤트별 중요도를 가중 합산(예:
  w1log(1+character_count)+w2out_degree+w3reveal_count+w4role_bonus)하여 계산한
  뒤, 각 캐릭터의 누적 중요도를 사전에 계산해 rise point를 결정합니다. 이벤트 메
  트릭은 오프라인으로 미리 precompute하며, 메트릭 부재 시에는 참여 횟수와
  predicate_code 하이라이트를 대체로 사용합니다.

  스포일러를 방지하기 위해 K 에피소드 이내의 이벤트만 취급하고, axis_tag는 불필요
  하며 predicate_code와 event_metric은 이미 확보된 상태입니다. 이 룰 기반 방식으
  로 캐릭터 A의 "부상 시점"을 효과적으로 산정할 수 있습니다.

  제안하는 부상 시점 산정 절차

  캐릭터 A에 대해 다음 단계로 중요도 상승 이벤트(부상 시점)를 산정합니다.

  1. event_character에서 A 관련 이벤트 필터링(episode_end ≤ K,
     source_status=APPROVED 조건 포함)
  2. 각 이벤트별 event_metric에서 중요도 점수 확보(누락 시 0 처리)
  3. episode_end, 이벤트 ID 순으로 정렬
  4. 누적 중요도 계산 및 전체 캐릭터 분포 대비 상대 임계값(예: 상위 20% 누적 중요
     도 또는 전체 순위 내 상위 N위)과 비교
  5. 임계값을 최초 넘는 이벤트를 부상 시점으로 선택하며 없으면 "아직 부상하지 않
     음" 반환

  MVP 모드로는 단순 최고 중요도 이벤트를 rise event로 하거나, 좀 더 고도화된 모드
  로 누적 중요도 및 랭크 기반 판정을 지원합니다. MySQL 8의 윈도 함수 활용 쿼리 작
  성도 가능하며, triple-store 없이 RDB로 충분히 구현할 수 있습니다. 스포일러 차원
  에서 K 이전 에피소드만 처리합니다.

• 아래는 **“인물 A가 중요 인물로 부상하는 시점”**을 산출하는 구체 로직(V3/Level4
  기준, 스포일러 안전 게이트 포함)이야.

  핵심 아이디어

  - “부상 시점” = A가 얽힌 사건들의 중요도 누적이 임계치(또는 상위 랭크)를 넘는
    최초 사건
  - 중요도는 라벨/지표 기반으로 계산해 event_metric.importance_score에 저장(또는
    요청 시 계산)

  ———

  ## 1) 중요도 점수(importance_score) 산식

  최소 신호를 이용한 결정적(재현 가능한) 점수:

  importance = w1*log(1+character_count)
             + w2*out_degree
             + w3*reveal_count
             + w4*role_bonus
             + w5*predicate_bonus

  - character_count: event_character 참여 인물 수
  - out_degree: event_relation from_event 기준 연결 수
  - reveal_count: event_reveal 수
  - role_bonus: SUBJECT/OBJECT/ALLY/ENEMY 등 역할 가중치
  - predicate_bonus: predicate_code가 중요한 타입이면 가점 (예: TRANSFORMS,
    BATTLE)

  > 이 점수는 event_metric에 사전 계산해두는 게 안정적.

  ———

  ## 2) 부상 시점 판정 규칙 (MVP 규칙 2가지 중 택1)

  ### 규칙 A (가장 단순)

  - A가 관여한 사건 중 **importance_score가 상위 P%**에 처음 진입한 사건을 부상
    시점으로 정의
  - 예: A의 사건 중 importance_score 상위 20%에 최초 진입한 사건

  ### 규칙 B (누적치 기반)

  - 사건을 시간순으로 누적해 누적 점수가 임계치 도달한 첫 사건을 부상 시점으로 정
    의
  - 예: A의 누적 importance가 전체 캐릭터 상위 N위에 들어가는 최초 사건

  ———

  ## 3) 스포일러 게이트 (필수)

  - 항상 event.episode_end <= K AND source_status = 'APPROVED'
  - 미래 사건은 계산/노출 모두 금지

  ———

  ## 4) SQL 스케치 (MVP)

  A의 사건 목록 + 중요도 + 역할 포함

  SELECT e.id, e.episode_end, e.summary, m.importance_score, ec.role
  FROM event e
  JOIN event_character ec ON ec.event_id = e.id
  LEFT JOIN event_metric m ON m.event_id = e.id
  WHERE ec.character_id = :characterId
    AND e.episode_end <= :K
    AND e.source_status = 'APPROVED'
  ORDER BY e.episode_end ASC, e.id ASC;

  부상 시점 (예: 상위 20% 최초 진입)

  - 애플리케이션에서 percentile 계산 후 첫 진입 사건 선택

  ———

  ## 5) 결과 출력 예시 (스포일러 안전)

  - “A는 **Ep.7의 ‘왕위 갈등 사건’**에서 중요 인물로 부상하기 시작했습니다.”
  - (기준: A의 사건 중 중요도 상위 20% 최초 진입)

  ———

  ## 결론

  V3/Level4의 “부상 시점”은 **role + metric(importance_score)**가 있어야 안정적으
  로 산출 가능하고,
  그 외에는 “단순 참여 이벤트 수/타입” 정도의 약한 추정밖에 못함.

  원하면 **임계치 기준(규칙 A/B)**를 어떤 방식으로 고정할지 같이 정하자.




 레벨4 질문들은 추가 신호/라벨이 없으면 답을 만들기 어려움. 질문별로 필요한
  최소 추가물은 아래야.

  - Q17 “예고된 사건”: event_relation.type = FORESHADOWS 라벨 필요. 미래 사건 내
    용은 노출 금지, 카운트/축만 반환.
  - Q18 “인물 관점 재구성”: event_character.role 필요 (SUBJECT/OBJECT/ALLY/ENEMY
    등). 최소는 SUBJECT/OBJECT만 있어도 동작.
  - Q19 “갈등 축 묶기”: event_axis_tag(event_id, axis_code) 필요. 축 코드 목록
    (5~10개) 고정 필요.
  - Q20 “서사 분포”: event.predicate_code만으로 가능하지만, 표준 predicate 정리가
    전제.

  추가로 필요한 공통 작업

  - DB 마이그레이션: event_character.role, event_axis_tag, event_metric,
    (FORESHADOWS는 type 규칙만)
  - 라벨 입력 루트: Wiki 리뷰/승인 단계에서 역할/축/중요도 입력 or 규칙 기반 계산
  - 노출 게이트: episode_end <= K + source_status = APPROVED 유지

  즉, v3(레벨4)로 가려면 role + axis_tag + metric + foreshadows가 최소 추가 세트
  고, 지금은 대부분이 없는 상태야. 원하는 질문부터 우선순위 정하면 그 순서대로 최
  소 신호만 붙여서 진행할 수 있어.

===
›>> 그럼 일단 프레디켓코드가 만들어진상태니까, 거기맞춰서 q20것만 일단 추가해놓고,
  q15(레벨3)전꺼 먼저 동작시키고 그다음 진행해도될라나

>>
  가능해. 순서도 합리적이야. predicate_code만으로 Q20은 최소 구현 가능하고,
  Q15(레벨3)는 기존 event v2 연쇄(원인/결과)만 정상 동작하면 됨.

  핵심 포인트만 정리하면:

  - Q20(인물 서사 분포): event.predicate_code만 있으면 됨.
    가장 빠른 방법은 /api/event/v2/characters/{id}/events로 사건 리스트 받고, 프
    론트에서 predicate별 카운트 집계해서 보여주는 방식.
    (백엔드 집계 API는 나중에 필요하면 추가)
  - Q15(레벨3): event_relation 기반 cause/effect가 제대로 있으면 그대로 동작.
    데이터가 없으면 “빈 상태”가 나올 수 있으니 시드/실데이터 확인이 필요.

  진행 순서 제안

  1. Q20은 프론트에서 집계 UI 추가(backend 변경 없이)

  이대로 가도 돼.
  원하면 Q20을 어디에 배치할지(인물 모달 vs 타임라인) 먼저 정하자.
