좋아, 이제 “데이터구조 정책”을 **어떤 질문 세트를 기준으로 고정할지**부터 딱 정리해서 스케치해볼게. (MVP 밖까지 포함)

---

## 결론부터

**데이터구조 정책의 기준 세트는 `Quick20`으로 잡는 게 맞다.**
이유: Quick20은 “위키로는 힘든, 온톨로지로만 풀리는 질의”를 **구조적으로 정의**한 세트라서, 스키마/관계/인덱스가 흔들리지 않아.

그 다음 계층은 이렇게 두면 된다:

1. **Quick20 = 데이터모델/쿼리 커버리지 기준(벤치마크)**
2. **Production15 = 데모 UI의 대표 질문 번들(제품 기준)**
3. **Expansion(후속 6개/100개) = 테스트 케이스 풀(품질/확장 기준)**
4. **“후속 1번 같은 서술형” = 분석용(STATE/PRESSURE 같은 확장 관계를 태우는 수요 확인용)**

## 운영 정렬 메모 (2026-02-26)

아래 원칙을 우선 적용한다.

1. **축 설정/커버리지 기준은 Quick20(Q20)**  
2. **SPO 설정은 기존 `event_character.role` 계약(`INVOLVED/SUBJECT/OBJECT`) 우선**  
3. **predicate 정합은 현재 `PredicateCode` + `PredicateGroup` 운영 스펙 기준**  
4. **DB 최소 변경 원칙**: 신규 enum/컬럼/relation type 추가는 보류하고, 기존 code/group/query 조합으로 먼저 커버리지 확보  

## 정합성 고정(필수, REVEALS 문서 기준)

- strict 정답 선택은 사실 이벤트(`event`) strict-first만 사용한다.
- `event_reveal`/`reveal_type(HINT|CONFIRM)`는 WHY/근거 강도 표시에만 사용한다.
- strict miss 상태에서 reveal/probe hit만으로 `ANSWERED` 승격을 허용하지 않는다.
- `STATE/PRESSURE`는 relation type 확장 대신 `event_reveal(ATTRIBUTE)`로 우회한다.
- canonical 기준:
  - `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
  - `fivecircles/architecture/specs/reveals/reveals-classification.md`
  - `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`

---

## 왜 Quick20이 1번이어야 하냐

Quick20은 이미 난이도/구현레벨까지 분해돼 있어.
즉 “이 질문을 풀려면 어떤 테이블/관계가 필요하다”가 **거의 곧 데이터 정책**이야.

* Level 1~2: `event + event_character + predicate_code + episode range`로 끝
* Level 3: `event_relation(PRECEDES)` + BFS hop 제한
* Level 4: 추론/분석(= MVP 밖)

너희가 “MVP 밖도 해도 된다” 했으니, 정책은 **Level 3까지는 강제**, Level 4는 **명시 데이터(STATE/PRESSURE/REVEALS)로 ‘추론 없이’ 흉내**내는 쪽이 안전해.

---

## 데이터구조 정책 스케치 (원칙 7개)

### P0. 질문 중심 설계 원칙 (Query-Driven)

* **모든 스키마 변경은 Quick20 중 최소 1개 질의가 더 정확/빠르게 풀리는 경우에만 허용**
* Production15/Expansion은 “질문 문구”일 뿐, **쿼리 형태로는 Quick20에 매핑**한다.

### P1. 이벤트는 “한 줄 사건”이 아니라 “SPO 트리플을 담는 컨테이너”

* Event 자체는 ID/episode range/predicate_code/summary만 가짐
* 사건의 의미는 **참여자 role로 구성**:

  * `(Subject, Predicate, Object)`
  * subject/object는 `event_character`에 **role**로 표시 (SUBJECT/OBJECT/INVOLVED)
* 이렇게 하면 “누가/누구를/무엇을” 질의는 SQL로 단단해짐.

### P2. Predicate는 통제된 taxonomy(코드북)로 운영

* `predicate_code`는 자유 텍스트 금지, 코드북에서만 선택
* Production15/Expansion의 문장들은 결국 predicate_code로 떨어져야 한다.
* 이게 없으면 “SPO” 넣어도 검색이 흐물흐물해짐.

### P3. 도미노(연쇄) 연결은 기본적으로 1종만 공식 채택

* **공식 관계 타입은 PRECEDES 하나**(지금 스펙 흐름 유지)
* 단, MVP 밖 확장으로 “왜/진화”를 하려면:

  * **STATE_CHANGE**와 **PRESSURE**는 “relation type 추가”가 아니라
  * **Event가 드러낸 속성/상태(ATTRIBUTE)를 REVEALS 대상으로 저장**해서 해결하는 게 가장 저렴함
  * 즉: `event_reveal(target=ATTRIBUTE)`로 “상태 변화”를 기록하고, 체인은 PRECEDES로 연결
* (너희가 원하면 나중에 event_relation.type 확장해도 되는데, 일단은 REVEALS/ATTRIBUTE로 우회가 덜 위험)

### P4. “언제(When)”는 episode range로만 답한다

* timestamp/scene time은 욕심내면 관리지옥이니까,
* 정책상 “언제”는 **SxEy** 기준으로 통일.

### P5. 체인 탐색 정책은 hop 제한이 규칙

* Level3(BFS)는 반드시:

  * `max_hops` 고정(예: 3)
  * `max_nodes` 고정(예: 50)
  * 노출은 Top path 1개, 나머지는 더보기
* 이 규칙이 없으면 질문 100개 넣는 순간 성능/UX 무너짐.

### P6. Production15는 “질문”이 아니라 “프리셋 파라미터”다

* Production15는 UI에서 버튼으로 제공되는 대표 세트니까,
* 정책상 Production15는 전부 아래로 내려가야 함:

  * Quick20의 query type + (subject/predicate/object/episode filters) 프리셋

### P7. Expansion(후속 100개)은 “새 기능 요구”가 아니다

* Expansion은 새 쿼리타입을 만드는 게 아니라,
* 기존 Quick20 질의를 **조합**해서 커버한다.
* Expansion 문항 중 Quick20으로 매핑 안 되는 건:

  * (A) 데이터 부족이라 NOT_ENOUGH_DATA
  * (B) 추론 요구라 “분석형(Phase2)”로 라벨링
  * (C) 상태/압력 필요라 event_reveal(ATTRIBUTE)로 최소 추가
    이 3개 중 하나로만 처리.

---

## 그래서 “뭐 기준으로 할까”에 대한 선택

* **기준(커버리지 벤치마크): Quick20**
* **UI/데모 기준: Production15**
* **개발 순서/회귀테스트 기준: Expansion(6개→100개)**
* **후속 1번 같은 서술형: 상태/압력(ATTRIBUTE) 스펙이 필요한지 판단하는 리서치용**

---

## 다음 액션(내가 바로 할 수 있는 산출물)

원하면 내가 다음 턴에 **정확히 이걸 만들어줄게**:

1. **Production15 → Quick20 매핑표**
   (각 질문이 Quick20의 어떤 타입(1~20)으로 떨어지는지)
2. **Expansion(후속 6개/100개) → Quick20 매핑 + “추가로 필요한 ATTRIBUTE 목록”**
   (STATE/PRESSURE를 어떤 attribute enum으로 최소화할지)

이렇게 가면 “데이터구조 정책”이 더 이상 감이 아니라 **질문 커버리지 기반 규칙**이 돼서, 팀원들이 왜 이렇게 했는지 안 물어봄.



ㅇㅋ. **“데이터구조 정책(= 스키마/관계/태깅/큐레이션 우선순위)”**를 뭘 기준으로 고정할지부터 딱 박고, 그 위에 **Production15를 Quick20으로 매핑**해줄게.

---

## 0) 기준 세트는 뭐로 고정?

**정답: Quick20을 커버리지 벤치마크로 고정**하는 게 제일 안정적이야.
Quick20은 “온톨로지로 질의 가능한 형태”를 난이도(Level 1~4)로 이미 쪼개놨고 , 관계·맥락 질의까지 포함돼서  스키마가 흔들리지 않아.

그 다음 우선순위는 이렇게:

1. **Quick20 = 데이터모델/쿼리 커버리지 기준(벤치마크)** 
2. **Production15 = 프론트 버튼(데모 UX) 기준** (v2.5-unify에 “front … Q1~Q15, Q20”로 이미 박혀있음) 
3. **Expansion(후속 100) = 회귀 테스트 풀(새 쿼리타입 금지)** 
4. “후속 1번 같은 서술형”은 **상태/압력(ATTRIBUTE) 필요성 검증용**(스키마 강제 기준으로 쓰면 폭발)

---

## 1) 데이터구조 정책 스케치 (한 장 요약)

### A. 노드/관계는 “3종 + 게이트”로 고정

* Node: **Event, Character** 
* Relation: **INVOLVES, REVEALS, PRECEDES** 
* 게이트: 모든 노출 쿼리에 `episode_end <= K` 강제 

### B. SPO는 “이벤트 내용”을 정밀하게 만드는 레이어

* Event 자체는 컨테이너, 의미는 `event_character.role`로 구성(이미 v2.5에서 role 존재) 
* 그래서 검색은 “텍스트”가 아니라 **(Subject/Predicate/Object) 조합**으로 줄어듦.

### C. 도미노(연쇄)는 PRECEDES만 ‘공식 링크’

* v2.5 정책상 `event_relation.type`은 PRECEDES만 허용 
* PRECEDES는 “명시된 경우만” 사용(자동 계산 X) 
* REVEALS는 설명용(표시/근거) 

### D. “왜/진화”는 스키마 확장 대신 **REVEALS → Attribute**로 우회

* 자동 인과 추론은 안 하기로 되어있으니 
* “폭력에 익숙해짐/통제권/압력” 같은 건 **Event가 드러낸 Attribute**로 기록하고, 체인은 PRECEDES로 엮는다.

---

## 2) Production15 → Quick20 매핑 (주요 1개 + 보조 2개)

Production15의 ‘원문 질문’ 파일은 지금 폴더에 없고, 대신 **Q1~Q15의 축 이름(살인의 진화… 은폐 전략)**은 Expansion 파일에 명시돼 있어서  그걸 기준으로 매핑했어.

> 표기: **주요(Primary)** / 보조(Secondary)

1. **Q1 살인의 진화**

* 주요: **#1 인물 A 사건 타임라인** 
* 보조: **#12 같은 유형 비교**, **#9 원인 체인** 

2. **Q2 제조의 확대**

* 주요: **#1 타임라인**
* 보조: **#12 유형 비교**, **#20 카테고리 분포 분석** 

3. **Q3 투코 관계 진화**

* 주요: **#2 A와 B 공동 등장 사건** 
* 보조: **#14 A→X→B 경로**, **#3 적대 인물 나열** 

4. **Q4 스카일러의 진실 접근**

* 주요: **#11 REVEALS(무엇이 드러났나)** 
* 보조: **#1 타임라인(스카일러 관점)**, **#17 관점 재구성** 

5. **Q5 범죄 결심 변화**

* 주요: **#5 ‘중요 인물로 부상’ 경로** 
* 보조: **#20 카테고리 분포**, **#9 원인 체인**

6. **Q6 월터-제시 파트너십 변질**

* 주요: **#2 공동 등장 사건**
* 보조: **#16 동일 갈등 축 묶기**, **#17 관점 재구성** 

7. **Q7 거짓말 균열/붕괴**

* 주요: **#11 REVEALS(단서가 드러남)**
* 보조: **#9 원인 체인**, **#12 유형 비교**

8. **Q8 가족 명분 붕괴**

* 주요: **#17 관점 재구성(가족 관점)**
* 보조: **#16 갈등 축 묶기**, **#20 카테고리 분포**

9. **Q9 행크 수사 진화**

* 주요: **#11 REVEALS(단서/증거가 드러남)**
* 보조: **#1 타임라인(행크)**, **#9 원인 체인**

10. **Q10 위협 성격 변화**

* 주요: **#16 갈등 축 묶기**
* 보조: **#12 유형 비교**, **#3 적대 인물 나열**

11. **Q11 의심하는 사람의 확장**

* 주요: **#11 REVEALS(‘의심을 낳는 단서’)**
* 보조: **#18 정체/폭로 유형 모아보기**, **#20 카테고리 분포** 

12. **Q12 통제권 장악 진화**

* 주요: **#12 유형 비교(협상/협박/통제 타입)** 
* 보조: **#5 부상 경로**, **#9 원인 체인** (필요하면 Attribute로 “control_level” 기록)

13. **Q13 돈 흐름 진화**

* 주요: **#20 카테고리 분포(돈/세탁/거래)**
* 보조: **#9 원인 체인**, **#12 유형 비교**
  (Expansion에도 돈 흐름 섹션이 있음) 

14. **Q14 스카일러-월터 관계 붕괴**

* 주요: **#16 갈등 축 묶기(관계 축)**
* 보조: **#17 관점 재구성**, **#11 REVEALS** 

15. **Q15 은폐 전략 진화**

* 주요: **#11 REVEALS(무엇을 숨겼고 무엇이 드러났나)**
* 보조: **#9 원인 체인**, **#12 유형 비교** 

---

## 3) 바로 적용되는 “정책” 한 줄

* **스키마/관계 추가는 Quick20 커버리지 증가할 때만**
* **Production15는 전부 Quick20 타입 + (S/P/O/episode) 프리셋으로만 구현** 
* **Expansion 100은 새 쿼리타입 금지, 기존 조합으로만** 

---

원하면 다음 턴에 바로 이어서:

1. 위 매핑을 기반으로 **“각 Production Q가 요구하는 최소 데이터(필수 테이블/필드/인덱스)” 체크리스트**
2. “왜/진화” 류를 위해 필요한 **Attribute enum 초안(최소 12개만)**
   이 두 개를 한 번에 뽑아줄게.


=========



좋아. “RDF 레이어가 이미 구현돼 있다”면 선택지는 2개야. 결론부터 말하면 **지금 있는 컬럼(role, reveals 등)을 꽉 채우고, 검색/도미노 축은 코드에서 불러오는 게 1순위**고, **SPARQL은 ‘진짜 그래프 질의가 이득인 일부 케이스’에만** 쓰는 게 안정적이야.

---

## 1) 지금 구조에서 뭐가 바뀌냐

### 네가 하려는 것

* SQL 테이블(이벤트/등장인물/관계)에는 **정규화된 사실(ground truth)**를 저장
* RDF 레이어는 그 사실을 **트리플로 투사(view)**해서 그래프 질의를 가능하게 함

이때 핵심은:

* **저장(Write)은 1곳만**: SQL (컬럼 채우기 포함)
* **조회(Read)는 2가지 경로**: 코드(SQL) 또는 SPARQL (필요한 것만)

이렇게 하면 데이터 일관성이 안 깨져.

---

## 2) “축(도미노/REVEALS/STATE/PRESSURE)”은 코드로 불러오면 되나?

**된다. 오히려 그게 맞다.**

축은 본질적으로 “데이터가 아니라 정책/모델”이야.

* 예: “REVEALS를 우선 연결로 본다”, “PRECEDES는 레일이다”, “hop=3”
  이건 RDF에 박아도 되지만, **바뀔 가능성이 크고** 디버깅도 코드가 훨씬 쉬워.

그래서 정책은 이렇게:

* DB: 사실 저장 (event, event_character(role), event_reveal, event_relation(precedes))
* 코드: 축 가중치/탐색 규칙/출력 템플릿

---

## 3) 그럼 SPARQL은 언제 쓰는 게 이득?

SPARQL은 “조인 지옥”이나 “패턴 매칭”에 강해.

### SPARQL이 이득인 케이스

1. **SPO 패턴 검색**

* (S=월터, P=THREATENS, O=?) 같은 트리플 패턴은 SPARQL이 깔끔함.

2. **REVEALS 기반 근거 펼치기**

* “이 요약이 왜 안전한가” 근거를 `:reveals` 트리플 묶음으로 뽑을 때 편함.

3. **제한된 경로 탐색(짧은 hop)**

* PRECEDES를 hop 2~3으로만 끊어서 탐색하면 SPARQL property path도 쓸만함.
* 단, hop을 크게 풀면 성능이 쉽게 터짐.

### SPARQL이 손해인 케이스

* “캐릭터 카드 리스트, 에피소드 K 필터, 중요도 정렬” 같은 건 **SQL이 압승**
* 운영에서 트리플스토어 튜닝/캐시/인덱싱까지 같이 관리해야 해서 부담이 커짐

---

## 4) 추천 운영안 (가장 덜 위험한 한 가지 안)

### 원칙

* **SQL = Canonical Store (정답 저장소)**
* **RDF = Read-only View (그래프 조회/실험/일부 고급 질의)**

### 실행 방식

1. 너 말대로 **기존 컬럼을 꽉 채운다**

   * event_character에 role(SUBJECT/OBJECT/INVOLVED)
   * event_reveal에 reveals(대상: Character/Attribute)
   * event_relation에 PRECEDES

2. API 기본은 **SQL + 코드 탐색(BFS)**

   * Quick20/Production15 대부분은 여기서 해결됨
   * PRECEDES 도미노는 코드 BFS가 디버깅 제일 쉬움

3. SPARQL은 **선택 기능으로만**

   * “SPO 검색(고급 필터)”이나 “근거(리빌) 펼치기” 같은 특정 엔드포인트에만 붙임
   * 경로 탐색도 hop 제한 걸고만 사용

---

## 5) 한 줄 결론

* **role/reveals 같은 ‘사실’은 컬럼에 다 채워.**
* **축/도미노 정책은 코드가 정답.**
* **SPARQL은 ‘패턴 매칭/근거 그래프/짧은 경로’만 골라서 쓰는 게 베스트.**

원하면 다음 턴에 내가 바로 “Quick20/Production15 기준으로”

* 어떤 질의는 SQL로,
* 어떤 질의는 SPARQL이 이득인지,
* 그리고 각각 필요한 트리플 스키마(IRI 규칙, predicate_code 매핑)
  를 딱 1장짜리 정책표로 만들어줄게.


======좋아. “**SQL+코드가 기본**, **SPARQL은 특화된 몇 개만**”을 기준으로, **Quick20/Production15 커버리지 관점**에서 1장짜리 정책표로 스케치해볼게.

---

## 1) 운영 원칙 한 줄

* **Write(정답 저장)는 SQL 한 곳만**: `event / event_character(role) / event_reveal / event_relation(PRECEDES)`
* **Read(조회)는 2경로**:

  * 기본: **SQL + 코드(BFS/정렬/필터)**
  * 선택: **SPARQL(패턴 매칭/근거 그래프/짧은 경로)**

---

## 2) “어떤 질의는 SQL, 어떤 질의는 SPARQL?” 결정 규칙

### SQL+코드가 이기는 경우 (기본 80%)

* K(episode gate)로 **범위 필터**가 크고
* 결과가 **리스트/정렬/페이지네이션** 중심이고
* 조인이 단순(캐릭터-이벤트)하거나
* PRECEDES 경로 탐색이 있어도 **hop 제한 BFS**면 충분할 때

### SPARQL이 이기는 경우 (선택 20%)

* 사용자가 “**SPO 패턴**”으로 빡세게 필터링할 때
  예: “월터가 *누구를* 위협했지?” = `(S=Walter, P=THREATENS, O=?)`
* “**근거(리빌) 묶음**”을 그래프처럼 묶어 보여줄 때
  예: “왜 스카일러가 의심했냐?” = `reveals` 관련 트리플 묶음
* “**짧은 경로 탐색**”을 트리플 패턴으로 바로 찾을 때 (hop 2~3 고정)

---

## 3) Quick20/Production15를 위한 조회 엔진 정책표 (1장)

| 질문 유형(대분류)         | 대표 예시              | 권장 엔진                      | 이유                       | SPARQL 쓰는 조건(있으면)                           |
| ------------------ | ------------------ | -------------------------- | ------------------------ | ------------------------------------------- |
| 인물 타임라인            | “월터 사건 나열”         | SQL                        | 정렬+페이지네이션+K필터 빠름         | 없음                                          |
| 인물 A·B 공동 사건       | “월터-제시 같이 나온 사건”   | SQL                        | 조인 2번이면 끝                | 없음                                          |
| 사건의 등장 인물          | “이 사건에 누가 나오나”     | SQL                        | 단건 조회                    | 없음                                          |
| predicate 필터       | “THREATENS만 보기”    | SQL                        | 인덱스 타기 쉬움                | 없음                                          |
| 에피소드 범위 사건         | “S1E1~E3 사건”       | SQL                        | 범위 필터 + 정렬               | 없음                                          |
| PRECEDES 체인(원인/결과) | “이 사건 이전/이후 도미노”   | SQL+코드 BFS                 | 디버깅/제한(hop/max_nodes) 쉬움 | hop 2~3 고정 + 결과 작을 때만 SPARQL path 허용        |
| SPO 패턴 검색          | “월터가 누구를 죽였나/협박했나” | SPARQL(선택) 또는 SQL(role 기반) | 그래프 패턴이 깔끔               | “S/P/O 중 2개 이상 고정”인 고급검색일 때만                |
| REVEALS 근거 펼치기     | “왜 의심했나(단서 목록)”    | SPARQL(선택)                 | reveals 트리플 묶기 좋음        | 근거 카드/그래프 UI를 제공할 때                         |
| 관계/심리 ‘진화’(후속/확장)  | “폭력 익숙해짐, 통제권”     | SQL(기본)                    | 결국 attribute 이벤트 나열이 안정  | SPARQL은 “attribute reveals”를 그래프로 묶어 보여줄 때만 |

**핵심:** Production15/Quick20의 메인 흐름은 **SQL+코드로 100% 커버** 가능하게 두고,
SPARQL은 “고급검색/근거시각화”처럼 **옵션 기능**으로만 붙이는 게 운영이 편해.

---

## 4) RDF 트리플 스키마 최소안 (이미 있는 컬럼을 그대로 투사)

SQL을 정답 저장소로 두고, RDF는 **읽기용 뷰**로만 만든다는 전제에서 “최소 트리플”은 이 정도면 충분해.

### 4.1 Event 기본

* `:Event/{event_id} a :Event`
* `:Event/{id} :episodeStart 1 ; :episodeEnd 3`
* `:Event/{id} :predicateCode "THREATENS"`

### 4.2 SPO(role 기반)

`event_character`에서 role을 읽어 트리플로 투사:

* SUBJECT: `:Event/{id} :subject :Character/{cid}`
* OBJECT: `:Event/{id} :object :Character/{cid}`
* INVOLVED: `:Event/{id} :involved :Character/{cid}`

(이걸로 SPO 패턴 질의가 성립)

### 4.3 PRECEDES

`event_relation(PRECEDES)` 투사:

* `:Event/{a} :precedes :Event/{b}`

### 4.4 REVEALS

`event_reveal` 투사:

* 캐릭터 리빌: `:Event/{id} :reveals :Character/{cid}`
* 속성 리빌(진화/압력/상태): `:Event/{id} :revealsAttribute :Attr/{key}`
  (값/레벨이 필요하면 `:Attr/{key} :value "high"` 같은 식으로 확장)

---

## 5) 너 질문에 대한 직답

> “있는 컬럼에 값 다 넣고(role, reveals 등) 축 같은 건 코드로 불러오면 되나?”

✅ **응. 그게 1순위 정답.**

* **role/reveals/precedes는 DB 컬럼에 꽉 채우고**
* **축(도미노 정책, 가중치, hop 제한, 출력 템플릿)은 코드에서** 관리
* **SPARQL은 고급검색/근거 그래프/짧은 경로**에만 선택적으로

---

원하면 다음 단계로 바로, 네 “Production15 버튼”을 기준으로:

1. **각 버튼이 호출할 SQL 쿼리/코드 BFS 루틴**을 정해주고
2. “SPARQL로만 제공할 고급 필터 5개”를 딱 골라서
3. 프론트에서 “고급검색 토글”로 보이게 UX까지 연결해줄게.
