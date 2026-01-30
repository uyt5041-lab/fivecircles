# DB Migration Summary (Full SQL)

> As of 2026-01-30 (local repo)
> Purpose: one-stop view of Flyway migration versions per service including SQL contents.

---

## Overview
- Each service owns its own Flyway migrations under:
  `services/<service>/src/main/resources/db/migration/`
- Versioning is per-service (not global). Highest version differs by service.

---

## Event Service (nospoiler_event)
Path: `services/event-service/src/main/resources/db/migration/`

### V1__init_event_schema.sql
`services/event-service/src/main/resources/db/migration/V1__init_event_schema.sql`

```sql
-- V1__init_event_schema.sql
-- Adapted from Notion V1__init_event.sql

CREATE TABLE IF NOT EXISTS event (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    drama_id BIGINT NOT NULL,
    summary TEXT NOT NULL,
    episode_start INT NOT NULL,
    episode_end INT NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    source_id BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_event_drama_range ON event(drama_id, episode_start, episode_end);

CREATE TABLE IF NOT EXISTS event_character (
    event_id BIGINT NOT NULL,
    character_id BIGINT NOT NULL,
    PRIMARY KEY (event_id, character_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS event_relation (
    from_event_id BIGINT NOT NULL,
    to_event_id BIGINT NOT NULL,
    type VARCHAR(20) NOT NULL,
    PRIMARY KEY (from_event_id, to_event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS event_reveal (
    event_id BIGINT NOT NULL,
    character_id BIGINT NOT NULL,
    reveal_type VARCHAR(20) NOT NULL,
    PRIMARY KEY (event_id, character_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### V2__fix_event_reveal_schema.sql
`services/event-service/src/main/resources/db/migration/V2__fix_event_reveal_schema.sql`

```sql
-- V2__fix_event_reveal_schema.sql
-- Fix event_reveal schema to match Spec (target_type, target_id)

DROP TABLE IF EXISTS event_reveal;

CREATE TABLE event_reveal (
    event_id BIGINT NOT NULL,
    target_type VARCHAR(20) NOT NULL COMMENT 'CHARACTER, ATTRIBUTE',
    target_id BIGINT NOT NULL,
    reveal_type VARCHAR(30),
    PRIMARY KEY (event_id, target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### V3__event_v2_pre_triple.sql
`services/event-service/src/main/resources/db/migration/V3__event_v2_pre_triple.sql`

```sql
-- V3__event_v2_pre_triple.sql
-- Add V2 fields and indexes before triples

-- 1) predicate_code (Level2 filter)
ALTER TABLE event
  ADD COLUMN predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN';

-- 2) source_status (Explainability: review status)
ALTER TABLE event
  ADD COLUMN source_status VARCHAR(20) NOT NULL DEFAULT 'APPROVED';

-- 3) event query index (common filters)
CREATE INDEX idx_event_drama_pred_end
  ON event (drama_id, predicate_code, episode_end, episode_start, id);

CREATE INDEX idx_event_drama_end
  ON event (drama_id, episode_end, id);

-- 4) BFS performance indexes
CREATE INDEX idx_er_from_type_to
  ON event_relation (from_event_id, type, to_event_id);

CREATE INDEX idx_er_to_type_from
  ON event_relation (to_event_id, type, from_event_id);
```

### V4__mig4_event_status_index.sql
`services/event-service/src/main/resources/db/migration/V4__mig4_event_status_index.sql`

```sql
-- V4__mig4_event_status_index.sql

CREATE INDEX idx_event_drama_status_end
  ON event (drama_id, source_status, episode_end, id);
```

### V5__mig5_event_character_index.sql
`services/event-service/src/main/resources/db/migration/V5__mig5_event_character_index.sql`

```sql
-- V5__mig5_event_character_index.sql

CREATE INDEX idx_ec_character_event
  ON event_character (character_id, event_id);
```

### V6__event_v3_triple_roles.sql
`services/event-service/src/main/resources/db/migration/V6__event_v3_triple_roles.sql`

```sql
-- V6__event_v3_triple_roles.sql
-- Ontology V3 Prep: Add Role column to distinguish Subject/Object

ALTER TABLE event_character
ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'INVOLVED' COMMENT 'INVOLVED, SUBJECT, OBJECT';

-- Add Index for Role-based queries (Level 4 Q16, Q18)
CREATE INDEX idx_ec_role_character ON event_character (character_id, role);
```

### V7__event_relation_pk_with_type.sql
`services/event-service/src/main/resources/db/migration/V7__event_relation_pk_with_type.sql`

```sql
-- V7__event_relation_pk_with_type.sql
-- Allow multiple relation types between the same event pair

ALTER TABLE event_relation
    DROP PRIMARY KEY,
    ADD PRIMARY KEY (from_event_id, to_event_id, type);
```

---

## Wiki Service (nospoiler_wiki)
Path: `services/wiki-service/src/main/resources/db/migration/`

### V1__init_wiki.sql
`services/wiki-service/src/main/resources/db/migration/V1__init_wiki.sql`

```sql
CREATE TABLE wiki_submission (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    character_id BIGINT NOT NULL COMMENT '대상 캐릭터 ID',
    author_id BIGINT NOT NULL COMMENT '제보자 사용자 ID',
    content TEXT NOT NULL COMMENT '제보 내용 (Fact)',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING, APPROVED, REJECTED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='위키(Fact) 제보 테이블';

CREATE TABLE wiki_submission_verification (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    submission_id BIGINT NOT NULL COMMENT '제보 ID',
    voter_id BIGINT NOT NULL COMMENT '투표자 ID',
    is_agreed BOOLEAN NOT NULL COMMENT 'TRUE: 찬성, FALSE: 반대',
    comment VARCHAR(500) COMMENT '검증 코멘트',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES wiki_submission(id) ON DELETE CASCADE,
    UNIQUE KEY uk_submission_voter (submission_id, voter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='위키 제보 검증(투표) 테이블';
```

### V2__add_context_columns.sql
`services/wiki-service/src/main/resources/db/migration/V2__add_context_columns.sql`

```sql
ALTER TABLE wiki_submission
ADD COLUMN drama_id BIGINT NOT NULL COMMENT '관련 드라마 ID' AFTER id,
ADD COLUMN episode BIGINT NOT NULL COMMENT '관련 회차 (또는 ID)' AFTER drama_id;

-- Index for searching submissions by drama and episode
CREATE INDEX idx_wiki_submission_drama_episode ON wiki_submission(drama_id, episode);
```

### V3__add_predicate_code.sql
`services/wiki-service/src/main/resources/db/migration/V3__add_predicate_code.sql`

```sql
ALTER TABLE wiki_submission
ADD COLUMN predicate_code VARCHAR(50) DEFAULT NULL;
```

### V4__add_ontology_fields.sql
`services/wiki-service/src/main/resources/db/migration/V4__add_ontology_fields.sql`

```sql
-- 1. 온톨로지용 정제 요약 (LLM or User Edited)
ALTER TABLE wiki_submission
ADD COLUMN refined_summary VARCHAR(1000) NULL COMMENT '온톨로지용 정제 요약';

-- 2. 관련 인물 매핑 테이블 (Logical FK only)
CREATE TABLE wiki_submission_involved_character (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    submission_id BIGINT NOT NULL,
    character_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_wsic_submission (submission_id)
);
```

### V5__add_predicate_suggestion.sql
`services/wiki-service/src/main/resources/db/migration/V5__add_predicate_suggestion.sql`

```sql
-- wiki_submission 테이블에 LLM의 추천 서술어를 저장하기 위한 컬럼 추가
ALTER TABLE wiki_submission ADD COLUMN predicate_suggestion VARCHAR(50) NULL;
```

---

## Auth Service (nospoiler_auth)
Path: `services/auth-service/src/main/resources/db/migration/`

### V1__init_refresh_tokens.sql
`services/auth-service/src/main/resources/db/migration/V1__init_refresh_tokens.sql`

```sql
CREATE TABLE IF NOT EXISTS refresh_tokens (
    key_id VARCHAR(255) NOT NULL,
    value VARCHAR(1024) NOT NULL,
    PRIMARY KEY (key_id)
);
```

### V2__create_email_verifications.sql
`services/auth-service/src/main/resources/db/migration/V2__create_email_verifications.sql`

```sql
CREATE TABLE email_verifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    verification_code VARCHAR(10) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_code (verification_code)
);
```

---

## User Service (nospoiler_user)
Path: `services/user-service/src/main/resources/db/migration/`

### V1__init_user_schema.sql
`services/user-service/src/main/resources/db/migration/V1__init_user_schema.sql`

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL UNIQUE,
    social_type VARCHAR(20) NOT NULL DEFAULT 'EMAIL',
    social_id VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### V2__add_status_and_profile_image.sql
`services/user-service/src/main/resources/db/migration/V2__add_status_and_profile_image.sql`

```sql
ALTER TABLE users ADD COLUMN profile_image VARCHAR(255);
ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE';
```

---

## Drama Service (nospoiler_drama)
Path: `services/drama-service/src/main/resources/db/migration/`

### V1__init_drama_schema.sql
`services/drama-service/src/main/resources/db/migration/V1__init_drama_schema.sql`

```sql
-- V1__init_drama_schema.sql
-- Adapted from Notion V1__init_content.sql (Part 1)

CREATE TABLE IF NOT EXISTS drama (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS episode (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    drama_id BIGINT NOT NULL,
    episode_number INT NOT NULL,
    UNIQUE KEY uk_episode_drama_number (drama_id, episode_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_episode_drama_episode ON episode(drama_id, episode_number);
```

### V2__add_details_to_drama.sql
`services/drama-service/src/main/resources/db/migration/V2__add_details_to_drama.sql`

```sql
-- V2__add_details_to_drama.sql
-- Add additional columns to drama table for API support

ALTER TABLE drama
    ADD COLUMN description TEXT AFTER title,
    ADD COLUMN poster_image_url VARCHAR(500) AFTER description,
    ADD COLUMN total_episodes INT AFTER poster_image_url,
    ADD COLUMN broadcast_network VARCHAR(100) AFTER total_episodes,
    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER broadcast_network,
    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
```

---

## Character Service (nospoiler_character)
Path: `services/character-service/src/main/resources/db/migration/`

### V1__init_character_schema.sql
`services/character-service/src/main/resources/db/migration/V1__init_character_schema.sql`

```sql
-- V1__init_character_schema.sql
-- Adapted from Notion V1__init_content.sql (Part 2)

CREATE TABLE IF NOT EXISTS `character` (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    drama_id BIGINT NOT NULL,
    display_name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_character_drama ON `character`(drama_id);
```

### V2__add_details_to_character.sql
`services/character-service/src/main/resources/db/migration/V2__add_details_to_character.sql`

```sql
-- V2__add_details_to_character.sql
-- Add detailed information columns to character table

ALTER TABLE `character`
    ADD COLUMN `name` VARCHAR(255) NOT NULL COMMENT 'Character Name' AFTER `drama_id`,
    ADD COLUMN `actor_name` VARCHAR(255) NULL COMMENT 'Actor Name' AFTER `name`,
    ADD COLUMN `description` TEXT NULL COMMENT 'Character Description' AFTER `actor_name`,
    ADD COLUMN `profile_image_url` VARCHAR(2048) NULL COMMENT 'Profile Image URL' AFTER `description`,
    ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    ADD COLUMN `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update Time';

-- Migrate existing data if any (Assuming 'display_name' was used as name)
UPDATE `character` SET `name` = `display_name`;

-- Remove old display_name column if desired, or keep it.
-- For now, we will drop it to keep schema clean, assuming V1 was just for testing.
ALTER TABLE `character` DROP COLUMN `display_name`;
```

---

## Admin Service (nospoiler_admin)
Path: `services/admin-service/src/main/resources/db/migration/`

### V1__init_admin_schema.sql
`services/admin-service/src/main/resources/db/migration/V1__init_admin_schema.sql`

```sql
-- V1__init_admin_schema.sql
-- Currently empty as Wiki tables moved to Wiki Service
-- Placeholder for future admin audit logs

-- CREATE TABLE IF NOT EXISTS admin_audit_log (...);
```

---

## Spoiler-Policy Service (nospoiler_policy)
Path: `services/spoiler-policy-service/src/main/resources/db/migration/`

### V1__init_policy_schema.sql
`services/spoiler-policy-service/src/main/resources/db/migration/V1__init_policy_schema.sql`

```sql
CREATE TABLE IF NOT EXISTS spoiler_policy (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    condition_json JSON COMMENT '판단 로직을 위한 조건 정의 (예: 특정 키워드, 특정 인물 조합)',
    severity_level VARCHAR(50) NOT NULL COMMENT '적용될 스포일러 레벨',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Appendix: Paths (for quick navigation)
- Event: `services/event-service/src/main/resources/db/migration/`
- Wiki: `services/wiki-service/src/main/resources/db/migration/`
- Auth: `services/auth-service/src/main/resources/db/migration/`
- User: `services/user-service/src/main/resources/db/migration/`
- Drama: `services/drama-service/src/main/resources/db/migration/`
- Character: `services/character-service/src/main/resources/db/migration/`
- Admin: `services/admin-service/src/main/resources/db/migration/`
- Spoiler-Policy: `services/spoiler-policy-service/src/main/resources/db/migration/`
