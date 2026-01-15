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

### `wiki_entry`
- `id` (PK), `drama_id`, `character_id`, `content`, `episode_start`, `episode_end`, `status`, `created_by_user_id`, `created_at`.
- *Index*: `(character_id, status, episode_end)`

### `review`
- `id` (PK), `wiki_entry_id`, `reviewer_user_id`, `decision`, `comment`, `created_at`.
- *Constraint*: `unique(wiki_entry_id, reviewer_user_id)`

---

## 4. Ontology / Event Domain (Member C)

### `event`
- `id` (PK), `drama_id`, `summary`, `episode_start`, `episode_end`, `source_type` (WIKI_ENTRY/MANUAL), `source_id`.
- *Index*: `(drama_id, episode_start, episode_end)`

### `event_character`
- `event_id`, `character_id`, `role`.
- *Constraint*: `unique(event_id, character_id)`

### `event_relation`
- `from_event_id`, `to_event_id`, `type` (RELATED/PRECEDES).

### `event_reveal` (Sprint 1: Storage Only)
- `id` (PK), `event_id`, `target_type` (CHARACTER/ATTRIBUTE), `target_id`, `reveal_type`.

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
CREATE TABLE wiki_entry (
  id BIGSERIAL PRIMARY KEY,
  drama_id BIGINT NOT NULL,
  character_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  episode_start INT NOT NULL,
  episode_end INT NOT NULL,
  status VARCHAR(20) NOT NULL,
  created_by_user_id BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE review (
  id BIGSERIAL PRIMARY KEY,
  wiki_entry_id BIGINT NOT NULL,
  reviewer_user_id BIGINT NOT NULL,
  decision VARCHAR(20) NOT NULL,
  comment TEXT,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE (wiki_entry_id, reviewer_user_id)
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
  source_id BIGINT
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