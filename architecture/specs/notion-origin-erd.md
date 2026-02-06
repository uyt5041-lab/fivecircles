# Sprint 1 ERD Specification (Source: Notion)

> **Synced**: 2026-01-15
> **Principles**:
> - Database per Service (Owner model)
> - **No Physical FK**, Logical ID references only.
> - All IDs are `bigint`.

---

## 1. User / Identity Domain (Member A)

### `user`
- `id` (PK), `email`, `password_hash`, `role` (VIEWER/CONTRIBUTOR/REVIEWER/ADMIN), `created_at`.

### `user_state`
- `id` (PK), `user_id`, `drama_id`, `last_watched_episode_number` (K), `updated_at`.
- *Constraint*: `unique(user_id, drama_id)`

---

## 2. Drama / Content Domain (Member B)

### `drama`
- `id` (PK), `title`, `created_at`.

### `episode`
- `id` (PK), `drama_id`, `episode_number`.
- *Constraint*: `unique(drama_id, episode_number)`

### `character`
- `id` (PK), `drama_id`, `display_name`.

---

## 3. Wiki Domain (Member B)

### `wiki_submission`
- `id` (PK), `drama_id`, `episode`, `character_id`, `author_id`, `content`, `predicate_code`, `status`, `created_at`, `updated_at`.
- *Index*: `(drama_id, episode)`

### `wiki_submission_verification`
- `id` (PK), `submission_id`, `voter_id`, `is_agreed`, `comment`, `created_at`.
- *Constraint*: `unique(submission_id, voter_id)`

---

## 4. Ontology / Event Domain (Member C)

### `event`
- `id` (PK), `drama_id`, `summary`, `episode_start`, `episode_end`, `source_type` (WIKI/MANUAL), `source_id`, `predicate_code`, `source_status`.
- *Index*: `(drama_id, episode_start, episode_end)`
- predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN'
- source_status VARCHAR(20) NOT NULL DEFAULT 'APPROVED'

### `event_character`
- `event_id`, `character_id`.
- *Constraint*: `unique(event_id, character_id)`

### `event_relation`
- `from_event_id`, `to_event_id`, `type` (PRECEDES).
- type VARCHAR(20)
  - PRECEDES
Indexes (for BFS):
- (from_event_id, type, to_event_id)
- (to_event_id, type, from_event_id)
### `event_reveal` (Sprint 1: Storage Only)
- `event_id`, `target_type` (CHARACTER/ATTRIBUTE), `target_id`, `reveal_type`.

---

## 5. Policy / QA Domain (No DB)
- **`spoiler_policy_service`**: Logic only (Allowed? Explain?).
- **`qa_service`**: AI Search & Policy judgement.

---

## Flyway Migration (Sprint 1)

### 1️⃣ auth-service / user-service
```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  role VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE user_state (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  drama_id BIGINT NOT NULL,
  last_watched_episode_number INT NOT NULL,
  updated_at TIMESTAMP DEFAULT now(),
  UNIQUE (user_id, drama_id)
);
```

### 2️⃣ content-service
```sql
CREATE TABLE drama (
  id BIGSERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL
);

CREATE TABLE episode (
  id BIGSERIAL PRIMARY KEY,
  drama_id BIGINT NOT NULL,
  episode_number INT NOT NULL,
  UNIQUE (drama_id, episode_number)
);

CREATE TABLE character (
  id BIGSERIAL PRIMARY KEY,
  drama_id BIGINT NOT NULL,
  display_name VARCHAR(255) NOT NULL
);
```

### 3️⃣ wiki-service
```sql
CREATE TABLE wiki_submission (
  id BIGSERIAL PRIMARY KEY,
  drama_id BIGINT NOT NULL,
  episode BIGINT NOT NULL,
  character_id BIGINT NOT NULL,
  author_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  predicate_code VARCHAR(50),
  status VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_wiki_submission_drama_episode
  ON wiki_submission (drama_id, episode);

CREATE TABLE wiki_submission_verification (
  id BIGSERIAL PRIMARY KEY,
  submission_id BIGINT NOT NULL,
  voter_id BIGINT NOT NULL,
  is_agreed BOOLEAN NOT NULL,
  comment VARCHAR(500),
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE (submission_id, voter_id)
);
```

### 4️⃣ ontology / filter / qa-service
```sql
CREATE TABLE event (
  id BIGSERIAL PRIMARY KEY,
  drama_id BIGINT NOT NULL,
  summary TEXT NOT NULL,
  episode_start INT NOT NULL,
  episode_end INT NOT NULL,
  source_type VARCHAR(20) NOT NULL,
  source_id BIGINT,
  predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN',
  source_status VARCHAR(20) NOT NULL DEFAULT 'APPROVED'
);

CREATE TABLE event_character (
  event_id BIGINT NOT NULL,
  character_id BIGINT NOT NULL,
  PRIMARY KEY (event_id, character_id)
);

CREATE TABLE event_relation (
  from_event_id BIGINT NOT NULL,
  to_event_id BIGINT NOT NULL,
  type VARCHAR(20) NOT NULL,
  PRIMARY KEY (from_event_id, to_event_id)
);

CREATE TABLE event_reveal (
  event_id BIGINT NOT NULL,
  target_type VARCHAR(20) NOT NULL,
  target_id BIGINT NOT NULL,
  reveal_type VARCHAR(30),
  PRIMARY KEY (event_id, target_type, target_id)
);
```

---

## Flyway Rules
- **No Physical FKs.**
- Column changes: increment version (`V2__`, etc.).
- No rollbacks allowed.
