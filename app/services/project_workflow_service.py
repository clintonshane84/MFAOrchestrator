# app/services/project_workflow_service.py
from __future__ import annotations

import json
import uuid
from typing import Any

from app.services.orchestrator_service import OrchestratorService
from app.domain.models.tasks import TaskType, TaskPriority
from app.domain.models.messages import Message, MessageRole
from app.domain.models.workflows import ProjectScaffoldResult


class ProjectWorkflowService:
    """
    High-level coordinator that mimics your manual ChatGPT-based dev workflow:

    1) Requirements gathering loop (Product Owner)
    2) PO user story generation
    3) System Architect ERD + class diagrams
    4) Backend Dev file layout + code skeleton
    5) Technical Lead review of combined bundle

    Returns a ProjectScaffoldResult with all raw JSON outputs.
    """

    def __init__(self, orchestrator: OrchestratorService) -> None:
        self._orch = orchestrator

    async def run_full_scaffold(
        self,
        created_by: str,
        initial_requirements: str,
    ) -> ProjectScaffoldResult:
        # 1) Start session
        session = await self._orch.start_session(
            created_by=created_by,
            title="Project scaffold",
            default_agent_id="product_owner_default",
        )

        # Keep “chat-like” messages in history
        history: list[Message] = []

        # Add initial customer requirements as a USER message
        initial_msg = Message(
            id=str(uuid.uuid4()),
            session_id=session.id,
            agent_id=None,
            role=MessageRole.USER,
            content=initial_requirements,
        )
        await self._orch._sessions.append_message(initial_msg)  # type: ignore[attr-defined]
        history.append(initial_msg)

        # 2) Requirements gathering loop with PO
        requirements_result = await self._run_requirements_loop(session.id, history)

        # Parse the finalised F/NFRs + user stories seed
        req_json = json.loads(requirements_result["raw"])

        # 3) User story generation (PO)
        user_story_bundle_str = json.dumps(req_json, indent=2)
        user_story_task = await self._orch.submit_task(
            session_id=session.id,
            agent_id="product_owner_default",
            title="Generate user stories",
            description=user_story_bundle_str,
            task_type=TaskType.ANALYSIS,
        )
        user_stories_raw = json.loads(user_story_task.result["raw"])  # type: ignore[index]

        # 4) Architecture (System Architect – ERD + class diagram)
        architect_input_bundle = {
            "project_summary": req_json.get("project_summary"),
            "functional_requirements": req_json.get("functional_requirements", []),
            "non_functional_requirements": req_json.get("non_functional_requirements", []),
            "user_stories": user_stories_raw.get("user_stories", []),
        }
        architect_task = await self._orch.submit_task(
            session_id=session.id,
            agent_id="system_architect_default",
            title="Design ERD and class diagrams",
            description=json.dumps(architect_input_bundle, indent=2),
            task_type=TaskType.DESIGN,
        )
        architecture_raw = json.loads(architect_task.result["raw"])  # type: ignore[index]

        # 5) Backend code skeleton (Backend Dev)
        backend_input_bundle = {
            "requirements": architect_input_bundle,
            "architecture": architecture_raw,
        }
        backend_task = await self._orch.submit_task(
            session_id=session.id,
            agent_id="backend_dev_default",
            title="Generate backend file layout and code skeleton",
            description=json.dumps(backend_input_bundle, indent=2),
            task_type=TaskType.CODE_SKELETON,
        )
        code_skeleton_raw = json.loads(backend_task.result["raw"])  # type: ignore[index]

        # 6) Technical Lead review (quality gate)
        review_bundle = {
            "requirements": req_json,
            "user_stories": user_stories_raw,
            "architecture": architecture_raw,
            "code_skeleton": code_skeleton_raw,
        }
        review_task = await self._orch.submit_task(
            session_id=session.id,
            agent_id="tech_lead_default",
            title="Technical review of project scaffold",
            description=json.dumps(review_bundle, indent=2),
            task_type=TaskType.REVIEW,
        )
        tech_lead_review_raw = json.loads(review_task.result["raw"])  # type: ignore[index]

        return ProjectScaffoldResult(
            requirements_raw=req_json,
            user_stories_raw=user_stories_raw,
            architecture_raw=architecture_raw,
            code_skeleton_raw=code_skeleton_raw,
            tech_lead_review_raw=tech_lead_review_raw,
        )

    async def _run_requirements_loop(
        self,
        session_id: str,
        history: list[Message],
        max_iterations: int = 5,
    ) -> dict[str, Any]:
        """
        Loop using ProductOwnerAgent in REQUIREMENTS_GATHERING mode until
        it returns action == 'finalise' or max_iterations reached.
        """
        current_round = 0
        last_result_json: dict[str, Any] | None = None

        # We'll treat the latest customer input as the last USER-role message.
        while current_round < max_iterations:
            current_round += 1

            # For simplicity, use the last USER message content as current “customer input”
            latest_customer_input = ""
            for msg in reversed(history):
                if msg.role == MessageRole.USER:
                    latest_customer_input = msg.content
                    break

            po_task = await self._orch.submit_task(
                session_id=session_id,
                agent_id="product_owner_default",
                title=f"Requirements gathering round {current_round}",
                description=latest_customer_input,
                task_type=TaskType.REQUIREMENTS_GATHERING,
            )

            po_raw = po_task.result["raw"]  # type: ignore[index]
            result_json = json.loads(po_raw)

            action = result_json.get("action")
            last_result_json = result_json

            if action == "ask_more":
                questions = result_json.get("questions", [])
                # In a real UI workflow, you'd show these questions to the customer,
                # capture their answers, and append another USER message.
                #
                # For automation-only mode, you could:
                # - Store questions and stop here, OR
                # - Integrate with a front-end that calls back with answers.
                #
                # Here, we just append a SYSTEM message noting that more info is required.
                q_text = "\n".join(f"- {q}" for q in questions)
                system_msg = Message(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    agent_id="product_owner_default",
                    role=MessageRole.SYSTEM,
                    content=f"PO requires more information:\n{q_text}",
                )
                await self._orch._sessions.append_message(system_msg)  # type: ignore[attr-defined]
                history.append(system_msg)

                # Break out early here because, in reality, you need a human to answer.
                break

            if action == "finalise":
                return result_json

        # Fall-back: return the last seen JSON (even if incomplete)
        return last_result_json or {"action": "unknown"}
