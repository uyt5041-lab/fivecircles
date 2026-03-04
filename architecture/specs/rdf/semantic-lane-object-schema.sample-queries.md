# Semantic Lane Object Schema Sample SPARQL Queries

기준일: 2026-03-04

대상 그래프
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/semantic-lane-object-schema.draft.ttl`

기본 prefix
```sparql
PREFIX ns: <https://nospoiler.dev/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
```

## Q1. 현재 object type 전체 목록

```sparql
PREFIX ns: <https://nospoiler.dev/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?objectType ?label ?status ?notes
WHERE {
  ?objectType rdf:type ns:ObjectType ;
              rdfs:label ?label .
  OPTIONAL { ?objectType ns:status ?status }
  OPTIONAL { ?objectType ns:notes ?notes }
}
ORDER BY ?label
```

의도
- semantic lane에서 정의된 object type catalog를 한 번에 확인한다.

## Q2. reveal semantic root와 연결된 object type 보기

```sparql
PREFIX ns: <https://nospoiler.dev/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?semantic ?semanticLabel ?objectType ?objectLabel
WHERE {
  ?semantic rdf:type ns:RevealSemantic ;
            ns:broader ns:r_semantic_reveal ;
            rdfs:label ?semanticLabel ;
            ns:objectType ?objectType .
  ?objectType rdfs:label ?objectLabel .
}
ORDER BY ?semanticLabel
```

의도
- `R_IDENTITY_REVEAL`, `R_RELATIONSHIP_REVEAL` 같은 root semantic family가 어떤 object type과 연결되는지 본다.

## Q3. 특정 semantic leaf의 상위 체인 보기
예시: `RK_ALIAS_IDENTITY`

```sparql
PREFIX ns: <https://nospoiler.dev/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node ?label
WHERE {
  VALUES ?leaf { ns:rk_alias_identity }
  ?leaf (ns:broader)* ?node .
  ?node rdfs:label ?label .
}
ORDER BY ?label
```

의도
- leaf 하나가 어떤 reveal semantic chain 아래에 속하는지 확인한다.
- Fuseki에서 transitive path(`*`)가 잘 동작하는지 빠르게 검증하는 smoke query로도 쓸 수 있다.

## Q4. runtime 대응이 없는 semantic-only object 찾기

```sparql
PREFIX ns: <https://nospoiler.dev/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?mapping ?label ?source ?notes
WHERE {
  ?mapping rdf:type ns:RuntimeMapping ;
           rdfs:label ?label ;
           ns:runtimeSource ?source .
  FILTER(?source = "semantic-only")
  OPTIONAL { ?mapping ns:notes ?notes }
}
ORDER BY ?label
```

의도
- 아직 RDB runtime 직접 대응이 없는 semantic lane object(`RELATION`, `ALIAS` 등)만 따로 본다.

## Q5. object type별 semantic leaf 수 집계

```sparql
PREFIX ns: <https://nospoiler.dev/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?objectLabel (COUNT(?semantic) AS ?semanticCount)
WHERE {
  ?semantic rdf:type ns:RevealSemantic ;
            ns:objectType ?objectType .
  ?objectType rdfs:label ?objectLabel .
  FILTER(?semantic != ns:r_semantic_reveal)
}
GROUP BY ?objectLabel
ORDER BY DESC(?semanticCount) ?objectLabel
```

의도
- semantic lane이 어느 object type에 치우쳐 있는지 거칠게 본다.
