# Business Workflow Specification

**Source**: Notion "Requirement Analysis" (Synced)

## 1. System Overview
**Project Name**: NoSpoiler Filtering Service
**Goal**: A wiki and Q&A service that strictly prevents story spoilers based on the user's progress.

## 2. Core Workflows

### S-1. Main Page (Entry)
1. **Drama Selection**: User selects a Drama from the list.
2. **Progress Input**: User inputs their current progress (e.g., "Watched until Episode 4").
   - *System stores this state as `K` (Current Episode).* 
3. **Character List**: System displays characters.
   - **Filtering Rule**: Only show information revealed up to Episode `K`.
   - **Spoiler Block**: Blurred or hidden details for events > `K`.

### S-2. Q&A (Search/Chat)
1. **Inquiry**: User asks a question (e.g., "Who killed character X?").
2. **Analysis**: System analyzes the question to identify entities and context.
3. **Spoiler Check**:
   - If the answer requires information from Episode > `K`, the system **WARNS** or **BLOCKS** the answer.
   - Output: "This information is revealed in Episode Y. You are currently at Episode K. Do you want to see it?"

### S-3. Wiki Contribution
1. **Drafting**: Users can edit character or event information.
2. **Event Tagging**: Every piece of information MUST be tagged with a `revealEpisode` (When does this happen?).
3. **Review**: Changes enter a 'Review' state.
4. **Approval**: Approved changes satisfy the spoiler constraints and are published.

## 3. User Roles
- **General User**: View (Filtered), Q&A.
- **Contributor**: Edit Wiki, Propose Changes.
- **Admin**: Approve Wiki changes, Manage Dramas.

## 4. K Handling Policy (Safety Gate)
- UI flow normally supplies `K` (episode progress) on navigation and API calls.
- **If `K` is missing** (direct API call, test tool, or UI bug), the system must default to safe behavior.
  - Recommended: **block** spoiler-prone responses, or treat as `K=0`.
  - Avoid returning unfiltered event data when `K` is absent.
- Prefer enforcing this at a shared layer (gateway or server defaults), not only in the UI.

