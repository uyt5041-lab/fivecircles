#!/usr/bin/env python3
"""
NoSpoiler Swarm Orchestrator
CLI 에이전트(codex, gemini, claude)를 오케스트레이션하여 개발 사이클 자동화

사이클: Plan → Code → Review → Re-review → Re-code → Test → Build → Repeat
"""
import subprocess
import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

# ============================================================
# Configuration
# ============================================================
PROJECT_ROOT = Path("/Users/pio/IdeaProjects/nospoiler")
FIVECIRCLES = PROJECT_ROOT / "fivecircles"
OUTPUT_DIR = FIVECIRCLES / "architecture" / "proposals"
LOG_DIR = FIVECIRCLES / "work" / "swarm-logs"

class AgentType(Enum):
    CODEX = "codex"
    GEMINI = "gemini"
    CLAUDE = "claude"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

@dataclass
class AgentTask:
    id: str
    agent: AgentType
    role: str  # planner, coder, reviewer
    prompt: str
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    review_comments: List[str] = field(default_factory=list)

# ============================================================
# Agent Runner
# ============================================================
class AgentRunner:
    """CLI 에이전트 실행기"""

    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def run(self, agent: AgentType, prompt: str, save_output: bool = True) -> str:
        """에이전트 실행 및 결과 반환"""
        cmd = self._get_command(agent, prompt)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\n{'='*60}")
        print(f"🤖 [{agent.value.upper()}] Executing...")
        print(f"{'='*60}")
        print(f"Prompt: {prompt[:100]}...")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(PROJECT_ROOT),
                env={**os.environ, "TERM": "xterm-256color"}
            )
            output = result.stdout or result.stderr or "[No output]"

            if save_output:
                log_file = self.log_dir / f"{agent.value}_{timestamp}.log"
                log_file.write_text(f"PROMPT:\n{prompt}\n\nOUTPUT:\n{output}")
                print(f"📝 Log saved: {log_file.name}")

            print(f"✅ [{agent.value.upper()}] Complete ({len(output)} chars)")
            return output

        except subprocess.TimeoutExpired:
            print(f"⏰ [{agent.value.upper()}] Timeout after {self.timeout}s")
            return f"[TIMEOUT after {self.timeout}s]"
        except Exception as e:
            print(f"❌ [{agent.value.upper()}] Error: {e}")
            return f"[ERROR: {e}]"

    def _get_command(self, agent: AgentType, prompt: str) -> str:
        """에이전트별 CLI 명령어 생성"""
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$')

        if agent == AgentType.CODEX:
            return f'codex "{escaped_prompt}"'
        elif agent == AgentType.GEMINI:
            return f'gemini "{escaped_prompt}"'
        elif agent == AgentType.CLAUDE:
            return f'claude --print "{escaped_prompt}"'
        else:
            raise ValueError(f"Unknown agent: {agent}")

# ============================================================
# Development Cycle Orchestrator
# ============================================================
class SwarmOrchestrator:
    """개발 사이클 오케스트레이터"""

    def __init__(self):
        self.runner = AgentRunner(timeout=300)
        self.cycle_count = 0
        self.results = {}

    def run_full_cycle(self, feature_description: str) -> Dict:
        """
        전체 개발 사이클 실행:
        Plan → Code → Review → Additional Review → Re-code → Test → Build
        """
        self.cycle_count += 1
        cycle_id = f"cycle_{self.cycle_count}_{int(time.time())}"

        print(f"\n{'#'*60}")
        print(f"# SWARM CYCLE #{self.cycle_count}: {feature_description[:50]}")
        print(f"{'#'*60}")

        cycle_result = {
            "id": cycle_id,
            "feature": feature_description,
            "started_at": datetime.now().isoformat(),
            "phases": {}
        }

        # Phase 1: PLAN (Codex)
        print("\n" + "="*60)
        print("📋 PHASE 1: PLANNING (Codex)")
        print("="*60)

        plan = self._phase_plan(feature_description)
        cycle_result["phases"]["plan"] = plan

        if not plan.get("success"):
            print("❌ Planning failed. Aborting cycle.")
            return cycle_result

        # Phase 2: CODE (Gemini/Claude)
        print("\n" + "="*60)
        print("💻 PHASE 2: CODING (Gemini + Claude)")
        print("="*60)

        code_results = self._phase_code(plan["output"])
        cycle_result["phases"]["code"] = code_results

        # Phase 3: REVIEW (Codex reviews others' code)
        print("\n" + "="*60)
        print("🔍 PHASE 3: REVIEW (Codex)")
        print("="*60)

        review = self._phase_review(code_results)
        cycle_result["phases"]["review"] = review

        # Phase 4: ADDITIONAL REVIEW (Cross-review)
        print("\n" + "="*60)
        print("🔄 PHASE 4: CROSS-REVIEW (All agents)")
        print("="*60)

        cross_review = self._phase_cross_review(code_results, review)
        cycle_result["phases"]["cross_review"] = cross_review

        # Phase 5: RE-CODE if needed
        if cross_review.get("needs_rework"):
            print("\n" + "="*60)
            print("🔧 PHASE 5: RE-CODE (Based on feedback)")
            print("="*60)

            recode = self._phase_recode(code_results, cross_review)
            cycle_result["phases"]["recode"] = recode
        else:
            print("\n✅ No rework needed, proceeding to test")

        # Phase 6: TEST
        print("\n" + "="*60)
        print("🧪 PHASE 6: TEST")
        print("="*60)

        test_result = self._phase_test()
        cycle_result["phases"]["test"] = test_result

        # Phase 7: BUILD
        print("\n" + "="*60)
        print("🏗️ PHASE 7: BUILD")
        print("="*60)

        build_result = self._phase_build()
        cycle_result["phases"]["build"] = build_result

        # Summary
        cycle_result["completed_at"] = datetime.now().isoformat()
        cycle_result["success"] = build_result.get("success", False)

        self._save_cycle_result(cycle_result)

        return cycle_result

    def _phase_plan(self, feature: str) -> Dict:
        """Codex가 플랜 작성"""
        prompt = f"""fivecircles 폴더를 읽고 다음 기능에 대한 구현 플랜을 작성해:

기능: {feature}

플랜에 포함할 내용:
1. 목표 및 범위
2. 변경할 파일 목록
3. 구현 단계 (step-by-step)
4. 역할 분배 (Backend/Frontend/Infra)
5. 테스트 계획
6. 완료 기준

결과를 fivecircles/architecture/proposals/current-plan.md에 저장해."""

        output = self.runner.run(AgentType.CODEX, prompt)

        return {
            "success": "[ERROR" not in output and "[TIMEOUT" not in output,
            "output": output
        }

    def _phase_code(self, plan: str) -> Dict:
        """Gemini와 Claude가 병렬로 코딩"""
        results = {}

        # Gemini: Backend
        backend_prompt = f"""다음 플랜에 따라 Backend 코드를 구현해:

{plan[:2000]}

Spring Boot 서비스 코드만 작성하고, 파일을 직접 수정해."""

        results["gemini_backend"] = {
            "agent": "gemini",
            "output": self.runner.run(AgentType.GEMINI, backend_prompt)
        }

        # Claude: Frontend
        frontend_prompt = f"""다음 플랜에 따라 Frontend 코드를 구현해:

{plan[:2000]}

React/TypeScript 코드만 작성하고, 파일을 직접 수정해."""

        results["claude_frontend"] = {
            "agent": "claude",
            "output": self.runner.run(AgentType.CLAUDE, frontend_prompt)
        }

        return results

    def _phase_review(self, code_results: Dict) -> Dict:
        """Codex가 코드 리뷰"""
        review_prompt = f"""다음 코드 변경사항을 리뷰해:

Backend (Gemini):
{code_results.get('gemini_backend', {}).get('output', '')[:1500]}

Frontend (Claude):
{code_results.get('claude_frontend', {}).get('output', '')[:1500]}

리뷰 항목:
1. 버그/보안 이슈
2. 코드 품질
3. 스펙 준수 여부

결과: APPROVE 또는 REQUEST_CHANGES (상세 피드백 포함)"""

        output = self.runner.run(AgentType.CODEX, review_prompt)

        return {
            "output": output,
            "approved": "APPROVE" in output.upper() and "REQUEST_CHANGES" not in output.upper()
        }

    def _phase_cross_review(self, code_results: Dict, initial_review: Dict) -> Dict:
        """다른 에이전트들의 추가 리뷰"""

        # Gemini reviews Claude's code
        gemini_review_prompt = f"""Claude가 작성한 Frontend 코드를 리뷰해:

{code_results.get('claude_frontend', {}).get('output', '')[:1500]}

추가 의견이나 개선점이 있으면 제안해."""

        gemini_review = self.runner.run(AgentType.GEMINI, gemini_review_prompt)

        # Claude reviews Gemini's code
        claude_review_prompt = f"""Gemini가 작성한 Backend 코드를 리뷰해:

{code_results.get('gemini_backend', {}).get('output', '')[:1500]}

추가 의견이나 개선점이 있으면 제안해."""

        claude_review = self.runner.run(AgentType.CLAUDE, claude_review_prompt)

        # 재작업 필요 여부 판단
        needs_rework = (
            "REQUEST_CHANGES" in initial_review.get("output", "").upper() or
            "개선" in gemini_review or "수정" in gemini_review or
            "개선" in claude_review or "수정" in claude_review
        )

        return {
            "gemini_review": gemini_review,
            "claude_review": claude_review,
            "needs_rework": needs_rework
        }

    def _phase_recode(self, original_code: Dict, reviews: Dict) -> Dict:
        """피드백 기반 재코딩"""
        recode_prompt = f"""다음 리뷰 피드백을 반영하여 코드를 수정해:

Codex Review:
{reviews.get('gemini_review', '')[:1000]}

Claude Review:
{reviews.get('claude_review', '')[:1000]}

파일을 직접 수정해."""

        output = self.runner.run(AgentType.CODEX, recode_prompt)

        return {"output": output}

    def _phase_test(self) -> Dict:
        """테스트 실행"""
        test_prompt = """프로젝트 테스트를 실행해:

1. ./gradlew test (Backend)
2. npm test (Frontend, 있다면)

결과를 요약해서 보고해."""

        output = self.runner.run(AgentType.CODEX, test_prompt)

        return {
            "output": output,
            "success": "BUILD SUCCESSFUL" in output or "passed" in output.lower()
        }

    def _phase_build(self) -> Dict:
        """빌드 실행"""
        build_prompt = """프로젝트 빌드를 실행해:

1. ./gradlew build -x test (Backend)
2. npm run build (Frontend)

결과를 보고해."""

        output = self.runner.run(AgentType.CODEX, build_prompt)

        return {
            "output": output,
            "success": "BUILD SUCCESSFUL" in output or "build" in output.lower()
        }

    def _save_cycle_result(self, result: Dict):
        """사이클 결과 저장"""
        output_file = OUTPUT_DIR / f"swarm-cycle-{result['id']}.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n📄 Cycle result saved: {output_file}")

# ============================================================
# Main Entry
# ============================================================
def main():
    """메인 실행"""
    if len(sys.argv) < 2:
        feature = "V3 마이그레이션: event_character.role 컬럼 추가 및 RoleType enum 적용"
    else:
        feature = " ".join(sys.argv[1:])

    print("""
╔══════════════════════════════════════════════════════════════╗
║         NoSpoiler SWARM ORCHESTRATOR v1.0                   ║
║                                                              ║
║  Cycle: Plan → Code → Review → Cross-Review →               ║
║         Re-code → Test → Build                               ║
╚══════════════════════════════════════════════════════════════╝
    """)

    orchestrator = SwarmOrchestrator()
    result = orchestrator.run_full_cycle(feature)

    print("\n" + "="*60)
    print("📊 CYCLE COMPLETE")
    print("="*60)
    print(f"Feature: {result['feature']}")
    print(f"Success: {'✅' if result.get('success') else '❌'}")
    print(f"Duration: {result['started_at']} → {result.get('completed_at', 'N/A')}")

    return 0 if result.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())
