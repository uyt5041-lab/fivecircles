#!/usr/bin/env python3
"""
NoSpoiler Swarm TMUX Orchestrator
tmux 세션을 통해 CLI 에이전트(codex, gemini, claude)를 오케스트레이션

사이클: Plan → Code → Review → Re-review → Re-code → Test → Build → Repeat
"""
import subprocess
import time
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
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

# ============================================================
# TMUX Agent Controller
# ============================================================
class TmuxAgentController:
    """tmux를 통한 CLI 에이전트 컨트롤러"""

    def __init__(self):
        self.sessions = {}
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _run_tmux(self, *args) -> str:
        """tmux 명령 실행"""
        cmd = ["tmux"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def _session_exists(self, name: str) -> bool:
        """세션 존재 여부 확인"""
        result = subprocess.run(
            ["tmux", "has-session", "-t", name],
            capture_output=True
        )
        return result.returncode == 0

    def create_session(self, agent: AgentType) -> bool:
        """에이전트용 tmux 세션 생성"""
        session_name = f"swarm-{agent.value}"

        if self._session_exists(session_name):
            print(f"  ℹ️ Session '{session_name}' already exists")
            return True

        # 새 세션 생성 (detached)
        subprocess.run([
            "tmux", "new-session", "-d", "-s", session_name,
            "-c", str(PROJECT_ROOT)
        ])

        # 잠시 대기 후 CLI 에이전트 시작
        time.sleep(1)

        # 에이전트별 시작 명령
        if agent == AgentType.CODEX:
            start_cmd = "codex"
        elif agent == AgentType.GEMINI:
            start_cmd = "gemini"
        elif agent == AgentType.CLAUDE:
            start_cmd = "claude"

        self._run_tmux("send-keys", "-t", session_name, start_cmd, "Enter")
        print(f"  ✅ Created session '{session_name}' with {agent.value}")

        self.sessions[agent] = session_name
        return True

    def send_prompt(self, agent: AgentType, prompt: str) -> None:
        """에이전트에게 프롬프트 전송"""
        session_name = f"swarm-{agent.value}"

        if not self._session_exists(session_name):
            print(f"  ❌ Session '{session_name}' not found")
            return

        # 프롬프트를 안전하게 이스케이프
        # tmux send-keys는 특수문자 처리가 필요
        escaped_prompt = prompt.replace("'", "'\\''")

        # 프롬프트 전송 (Enter로 실행)
        self._run_tmux("send-keys", "-t", session_name, escaped_prompt, "Enter")
        print(f"  📤 Sent prompt to {agent.value} ({len(prompt)} chars)")

    def capture_output(self, agent: AgentType, lines: int = 200) -> str:
        """에이전트 출력 캡처"""
        session_name = f"swarm-{agent.value}"

        if not self._session_exists(session_name):
            return "[Session not found]"

        # 현재 pane 내용 캡처
        output = self._run_tmux(
            "capture-pane", "-t", session_name, "-p", "-S", f"-{lines}"
        )

        return output.strip()

    def wait_for_completion(self, agent: AgentType, timeout: int = 300,
                            poll_interval: int = 5) -> str:
        """에이전트 작업 완료 대기"""
        session_name = f"swarm-{agent.value}"
        start_time = time.time()
        last_output = ""
        stable_count = 0

        print(f"  ⏳ Waiting for {agent.value} (max {timeout}s)...")

        while time.time() - start_time < timeout:
            current_output = self.capture_output(agent)

            # 출력이 안정화되었는지 확인 (3번 연속 동일하면 완료로 간주)
            if current_output == last_output:
                stable_count += 1
                if stable_count >= 3:
                    print(f"  ✅ {agent.value} output stabilized")
                    return current_output
            else:
                stable_count = 0
                last_output = current_output

            time.sleep(poll_interval)

        print(f"  ⏰ {agent.value} timeout after {timeout}s")
        return self.capture_output(agent)

    def kill_session(self, agent: AgentType) -> None:
        """세션 종료"""
        session_name = f"swarm-{agent.value}"
        if self._session_exists(session_name):
            self._run_tmux("kill-session", "-t", session_name)
            print(f"  🔴 Killed session '{session_name}'")

    def kill_all_sessions(self) -> None:
        """모든 스웜 세션 종료"""
        for agent in AgentType:
            self.kill_session(agent)


# ============================================================
# TMUX Swarm Orchestrator
# ============================================================
class TmuxSwarmOrchestrator:
    """tmux 기반 스웜 오케스트레이터"""

    def __init__(self):
        self.controller = TmuxAgentController()
        self.cycle_count = 0

    def setup_agents(self) -> bool:
        """모든 에이전트 세션 초기화"""
        print("\n" + "="*60)
        print("🚀 INITIALIZING AGENT SESSIONS")
        print("="*60)

        for agent in [AgentType.CODEX, AgentType.GEMINI, AgentType.CLAUDE]:
            self.controller.create_session(agent)
            time.sleep(2)  # 에이전트 초기화 대기

        print("\n✅ All agent sessions ready")
        print("💡 View sessions: tmux ls")
        print("💡 Attach: tmux attach -t swarm-codex")
        return True

    def run_phase(self, phase_name: str, agent: AgentType, prompt: str,
                  timeout: int = 300) -> Dict:
        """단일 페이즈 실행"""
        print(f"\n{'='*60}")
        print(f"📋 {phase_name} ({agent.value.upper()})")
        print("="*60)

        # 프롬프트 전송
        self.controller.send_prompt(agent, prompt)

        # 완료 대기
        output = self.controller.wait_for_completion(agent, timeout=timeout)

        # 로그 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOG_DIR / f"{phase_name.lower().replace(' ', '_')}_{agent.value}_{timestamp}.log"
        log_file.write_text(f"PROMPT:\n{prompt}\n\nOUTPUT:\n{output}")
        print(f"  📝 Log: {log_file.name}")

        return {
            "agent": agent.value,
            "output": output,
            "log_file": str(log_file)
        }

    def run_full_cycle(self, feature: str) -> Dict:
        """전체 개발 사이클 실행"""
        self.cycle_count += 1
        cycle_id = f"cycle_{self.cycle_count}_{int(time.time())}"

        print(f"\n{'#'*60}")
        print(f"# SWARM CYCLE #{self.cycle_count}")
        print(f"# Feature: {feature[:50]}...")
        print(f"{'#'*60}")

        result = {
            "id": cycle_id,
            "feature": feature,
            "started_at": datetime.now().isoformat(),
            "phases": {}
        }

        # Phase 1: PLAN (Codex)
        plan_prompt = f"""fivecircles 폴더를 읽고 다음 기능에 대한 구현 플랜을 작성해:

기능: {feature}

플랜에 포함할 내용:
1. 목표 및 범위
2. 변경할 파일 목록
3. 구현 단계
4. 역할 분배
5. 테스트 계획

결과를 fivecircles/architecture/proposals/v3-migration-plan.md에 저장해."""

        result["phases"]["plan"] = self.run_phase(
            "PHASE 1: PLANNING", AgentType.CODEX, plan_prompt, timeout=180
        )

        # Phase 2: CODE (Gemini - Backend)
        backend_prompt = f"""fivecircles/architecture/proposals/v3-migration-plan.md를 읽고
Backend 코드를 구현해. Spring Boot 서비스 파일을 직접 수정해."""

        result["phases"]["code_backend"] = self.run_phase(
            "PHASE 2A: BACKEND CODE", AgentType.GEMINI, backend_prompt, timeout=300
        )

        # Phase 2: CODE (Claude - Frontend)
        frontend_prompt = f"""fivecircles/architecture/proposals/v3-migration-plan.md를 읽고
Frontend 코드를 구현해. React/TypeScript 파일을 직접 수정해."""

        result["phases"]["code_frontend"] = self.run_phase(
            "PHASE 2B: FRONTEND CODE", AgentType.CLAUDE, frontend_prompt, timeout=300
        )

        # Phase 3: REVIEW (Codex)
        review_prompt = """git diff를 확인하고 변경된 코드를 리뷰해.
버그, 보안 이슈, 개선점을 찾아서 보고해.
결과: APPROVE 또는 REQUEST_CHANGES"""

        result["phases"]["review"] = self.run_phase(
            "PHASE 3: REVIEW", AgentType.CODEX, review_prompt, timeout=180
        )

        # Phase 4: CROSS-REVIEW
        cross_review_prompt = """다른 에이전트가 작성한 코드를 git diff로 확인하고
추가 의견이나 개선점을 제안해."""

        result["phases"]["cross_review_gemini"] = self.run_phase(
            "PHASE 4A: CROSS-REVIEW", AgentType.GEMINI, cross_review_prompt, timeout=180
        )

        result["phases"]["cross_review_claude"] = self.run_phase(
            "PHASE 4B: CROSS-REVIEW", AgentType.CLAUDE, cross_review_prompt, timeout=180
        )

        # Phase 5: TEST
        test_prompt = """./gradlew test를 실행해서 테스트 결과를 보고해."""

        result["phases"]["test"] = self.run_phase(
            "PHASE 5: TEST", AgentType.CODEX, test_prompt, timeout=300
        )

        # Phase 6: BUILD
        build_prompt = """./gradlew build -x test를 실행해서 빌드 결과를 보고해."""

        result["phases"]["build"] = self.run_phase(
            "PHASE 6: BUILD", AgentType.CODEX, build_prompt, timeout=300
        )

        result["completed_at"] = datetime.now().isoformat()

        # 결과 저장
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / f"swarm-result-{cycle_id}.json"
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n📄 Cycle result: {output_file}")

        return result


# ============================================================
# Main
# ============================================================
def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       NoSpoiler TMUX SWARM ORCHESTRATOR v2.0                ║
║                                                              ║
║  tmux sessions → CLI agents → Full Dev Cycle                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    orchestrator = TmuxSwarmOrchestrator()

    # 커맨드라인 인자 처리
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "setup":
            # 에이전트 세션만 초기화
            orchestrator.setup_agents()

        elif cmd == "run":
            # 전체 사이클 실행
            feature = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else \
                "V3 마이그레이션: event_character.role 컬럼 추가"
            orchestrator.setup_agents()
            time.sleep(5)  # 에이전트 준비 대기
            orchestrator.run_full_cycle(feature)

        elif cmd == "cleanup":
            # 모든 세션 종료
            orchestrator.controller.kill_all_sessions()

        elif cmd == "status":
            # 세션 상태 확인
            os.system("tmux ls 2>/dev/null || echo 'No tmux sessions'")

        else:
            print(f"Unknown command: {cmd}")
            print("Usage: swarm_tmux_orchestrator.py [setup|run|cleanup|status]")

    else:
        print("""
Usage:
  python swarm_tmux_orchestrator.py setup     # 에이전트 세션 초기화
  python swarm_tmux_orchestrator.py run       # 전체 사이클 실행
  python swarm_tmux_orchestrator.py cleanup   # 세션 정리
  python swarm_tmux_orchestrator.py status    # 세션 상태 확인

Manual control:
  tmux ls                        # 세션 목록
  tmux attach -t swarm-codex     # Codex 세션 접속
  tmux send-keys -t swarm-codex "prompt here" Enter  # 프롬프트 전송
        """)

if __name__ == "__main__":
    main()
