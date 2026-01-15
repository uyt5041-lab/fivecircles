-- V2__create_wiki_entry.sql
-- Proposed by Member C (Intelligence & Filter) to match Sprint 1 ERD
-- Note: This matches the required schema for spoiler filtering logic.

CREATE TABLE IF NOT EXISTS wiki_entry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    drama_id BIGINT NOT NULL,
    character_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    episode_start INT NOT NULL,
    episode_end INT NOT NULL,
    status VARCHAR(20) NOT NULL COMMENT 'PENDING, APPROVED, REJECTED, NEEDS_EDIT',
    created_by_user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_wiki_entry_character_status_range ON wiki_entry(character_id, status, episode_start, episode_end);

CREATE TABLE IF NOT EXISTS review (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    wiki_entry_id BIGINT NOT NULL,
    reviewer_user_id BIGINT NOT NULL,
    decision VARCHAR(20) NOT NULL COMMENT 'APPROVE, REJECT, REQUEST_EDIT',
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_wiki_entry_reviewer (wiki_entry_id, reviewer_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
