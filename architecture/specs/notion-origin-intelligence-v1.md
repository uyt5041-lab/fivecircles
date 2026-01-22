# Intelligence Service Spec v1 (LLM-based Ontology Refinement)

> **Status**: Proposed / Under Discussion
> **Role**: Team Member C (Intelligence & Filter)
> **Objective**: Transform raw natural language wiki submissions into structured ontology triples (Event-Predicate-Character).

---

## 1. Core Responsibilities

The Intelligence Service acts as an **Ontology Refiner**, performing three primary tasks on raw text content:

### Task A: Entity Extraction (involvedCharacterIds)

- **Goal**: Identify all characters mentioned in the text and map them to system-internal `character_id`s.
- **Process**: LLM is provided with a drama-specific character list (Name/Alias to ID) in the context to perform accurate mapping.

### Task B: Predicate Classification (predicateCode)

- **Goal**: Categorize the core action of the event into a predefined `PredicateCode` Enum.
- **Constraint**: Must use a closed set (e.g., `DIES`, `BETRAYS`, `MEETS`) to maintain graph integrity.

### Task C: Summary Refinement (refinedSummary)

- **Goal**: Rewrite emotionally charged or informal content into a dry, standard, and concise summary for the event timeline.
- **Example**: "Wow, I can't believe character A betrayed B!" -> "Character A betrays B."

---

## 2. Architecture & Workflow

### Independent Service

- Specialized service (`intelligence-service`) to decouple heavy LLM processing and AI-specific dependencies (e.g., Python/FastAPI) from core business logic (`wiki-service`).

### Asynchronous Enrichment Flow (Hybrid Approach)

1. **Submission**: User submits a fact to `wiki-service` (Real-time).
2. **Analysis**: `wiki-service` triggers `intelligence-service` asynchronously (Message Queue or Async Call).
3. **Drafting**: LLM generates a "Structure Proposal" (Characters, Predicate, Refined Summary).
4. **Human-in-the-loop**: User/Reviewer receives an update/notification. They verify or correct the AI-generated tags via a tag-editor UI.

---

## 3. Technical Strategy

### ID Mapping (Context Injection)

- To prevent mismatched IDs, every LLM call for a specific drama will fetch the current character list from `character-service` and inject it into the prompt.
- **Prompt Example**: "Characters in this drama: [101: Jon, 102: Dany]. Content: 'Jon meets Dany'. Extract IDs." -> Output: `[101, 102]`.

### Hallucination Prevention & Expansion Strategy

- **Backend**: Enforce **JSON Schema** in LLM response. Use `OTHER` as a fallback for undefined predicates.
- **Semantic OTHER Strategy**: If LLM cannot find a suitable Enum value, it returns `OTHER` for `predicateCode` and provides the intended predicate (e.g., "KIDNAPS") in the `predicateSuggestion` field. This data is used for future ontology expansion.
- **Frontend**: AI suggestions are rendered as "Clickable Tag Badges". Users can delete incorrect tags or manually search/add missing ones from the character DB.

### Fallback Mechanism (AI Unavailable)

1. **Rule-based (Regex)**: Simple keyword matching for character names in the text.
2. **System Default**: Predicate defaults to `OTHER`, involved characters default to the main subject of the wiki page.
3. **Manual Trigger**: Provide a "Re-analyze with AI" button for users to try again later.

---

## 4. API Interface (Draft)

### `POST /intelligence/refine`

- **Request**:
  ```json
  {
    "dramaId": 1,
    "content": "natural language text",
    "context": {
      "characterList": [{"id": 101, "name": "A"}, ...]
    }
  }
  ```
- **Response**:
  ```json
  {
    "predicateCode": "BETRAYS",
    "predicateSuggestion": null,
    "involvedCharacterIds": [101, 102],
    "refinedSummary": "Standardized summary text"
  }
  ```

---

<!-- USER_MEMO_START -->

## 💡 Notes & Considerations

1. **UX Optimization**
   - Respond immediately upon wiki submission, run LLM analysis in the background.
   - Send "AI Proposal Arrived" notification (WebSocket/SSE) to ensure smooth workflow.
   - UX Scenario: User writes -> clicks submit -> receives "Submitted. AI is analyzing..." -> redirected to list/detail page.

2. **Independence of Intelligence Service**
   - Build `intelligence-service` as an independent service to allow future migration to AI-optimized environments (e.g., Python/FastAPI).
   - Consider Rate Limits due to high LLM costs.
   - Reuse for Q&A or Community services.

3. **Data Mapping Precision**
   - Dynamic RAG approach for injecting character and drama info into prompts is most efficient.

4. **Stability (Fallback)**
   - If AI is unavailable: Regex matching -> Defaults (OTHER/Primary Subject) -> Manual Tagging request UI.

5. **Semantic OTHER Expansion Strategy**
   - Keep v1 PredicateCode Enum generic.
   - Store LLM's raw suggestions in `predicate_suggestion` when code is `OTHER`.
   - Periodically promote high-frequency suggestions to official Enum values.
   <!-- USER_MEMO_END -->

---
