"""Iterative propose -> judge -> repair loop controller."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from learning_compiler.agent.model_policy import ModelPolicy
from learning_compiler.agent.pedagogy_critic import PedagogyCritic
from learning_compiler.agent.proposer import Proposer
from learning_compiler.agent.quality_model import DeterministicQualityJudge
from learning_compiler.agent.repair_executor import RepairExecutor
from learning_compiler.agent.repair_planner import RepairPlanner
from learning_compiler.agent.research import ResourceResolver
from learning_compiler.agent.spec import GenerationSpec
from learning_compiler.agent.trace import IterationTrace, OptimizationTrace


@dataclass(slots=True, frozen=True)
class OptimizeResult:
    curriculum: dict[str, object]
    trace: OptimizationTrace


class LoopController:
    """Main optimization control loop."""

    def __init__(
        self,
        proposer: Proposer,
        critic: PedagogyCritic,
        judge: DeterministicQualityJudge,
        planner: RepairPlanner,
        repair: RepairExecutor,
    ) -> None:
        self._proposer = proposer
        self._critic = critic
        self._judge = judge
        self._planner = planner
        self._repair = repair

    def optimize(
        self,
        spec: GenerationSpec,
        resolver: ResourceResolver,
        policy: ModelPolicy,
    ) -> OptimizeResult:
        draft = self._proposer.propose(spec, resolver, policy)
        best = draft
        best_score = -1
        accepted = False
        stop_reason = "max_iterations_reached"
        iterations: list[IterationTrace] = []

        for iteration in range(1, policy.max_iterations + 1):
            pedagogy = self._critic.critique(draft, spec.topic_spec, policy)
            report = self._judge.evaluate(draft, spec.topic_spec, pedagogy)

            if report.total_score > best_score:
                best = deepcopy(draft)
                best_score = report.total_score

            actions = self._planner.plan(report, pedagogy)
            iterations.append(
                IterationTrace(
                    iteration=iteration,
                    model_policy=policy.snapshot(),
                    pedagogy_summary=pedagogy.summary_dict(),
                    score_summary=report.score_summary(),
                    learner_path_diagnostics=tuple(
                        item.to_dict()
                        for item in report.diagnostics
                        if item.rule_id.startswith("learner.")
                    ),
                    selected_actions=actions,
                    post_score_summary=report.score_summary(),
                )
            )

            if report.hard_fail_count == 0 and report.total_score >= policy.target_score and pedagogy.min_quality_met:
                accepted = True
                stop_reason = "accepted_threshold_met"
                break

            if not actions:
                stop_reason = "no_actions_available"
                break

            draft = self._repair.apply(draft, actions, spec, resolver, policy)

        trace = OptimizationTrace(
            schema_version=policy.schema_version,
            stop_reason=stop_reason,
            iterations=tuple(iterations),
            best_score=max(0, best_score),
            accepted=accepted,
        )
        return OptimizeResult(curriculum=best, trace=trace)
