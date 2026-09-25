"""
Lab 11 — Main Entry Point

``--part`` khớp số Checkpoint (dễ nhớ):

    python main.py              # Core: 2 → 3 → 4
    python main.py --part 2     # Checkpoint 2 — guardrails
    python main.py --part 3     # Checkpoint 3 — pipeline / results.json
    python main.py --part 4     # Checkpoint 4 — red team / attacks

Optional (không chấm):

    python main.py --part 5     # Security testing pipeline
    python main.py --part 6     # HITL demos
"""
import sys
import asyncio
import argparse

from core.config import setup_api_key


async def part2_guardrails():
    """Checkpoint 2: input + output guardrails."""
    print("\n" + "=" * 60)
    print("CHECKPOINT 2: Guardrails")
    print("=" * 60)

    print("\n--- Input Guardrails ---")
    from guardrails.input_guardrails import (
        test_injection_detection,
        test_topic_filter,
        test_input_plugin,
    )
    test_injection_detection()
    print()
    test_topic_filter()
    print()
    await test_input_plugin()

    print("\n--- Output Guardrails ---")
    from guardrails.output_guardrails import test_content_filter
    test_content_filter()
    print("(LLM-as-Judge / NeMo — optional, skipped)")


async def part3_assignment_suite():
    """Checkpoint 3: defense suite → outputs/results.json."""
    import os

    print("\n" + "=" * 60)
    print("CHECKPOINT 3: Assignment suite → outputs/*.json")
    print("=" * 60)

    from assignment.pipeline import (
        build_production_plugins,
        build_observability,
        run_assignment_suite,
    )

    student_id = os.environ.get("STUDENT_ID", "").strip() or "2A2026xxxxx"
    try:
        plugins = build_production_plugins(use_llm_judge=False)
        audit, monitor = build_observability()
        pipeline = {"plugins": plugins, "audit": audit, "monitor": monitor}
        result = await run_assignment_suite(pipeline, student_id=student_id)
        print("Suite finished.")
        print(f"Wrote outputs under repo outputs/ (student_id={student_id})")
        return result
    except NotImplementedError as e:
        print(
            "Chưa xong Checkpoint 3 (src/assignment/pipeline.py). "
            "Hoàn thành rồi chạy lại:\n"
            "  cd src\n"
            "  python main.py --part 3"
        )
        print(f"Detail: {e}")
        return None


async def part4_attacks():
    """Checkpoint 4: attack Red Agent (default), then Red Agent (advance / bonus)."""
    print("\n" + "=" * 60)
    print("CHECKPOINT 4: Red Agent (default) + Red Agent (advance)")
    print("=" * 60)

    from agents.agent import create_red_agent_default, test_agent
    from agents.guards_agent import create_red_agent_advance
    from attacks.attacks import run_attacks, save_attack_results

    red_default, red_default_runner = create_red_agent_default()
    await test_agent(red_default, red_default_runner)

    print("\n--- Attacks on Red Agent (default) ---")
    unsafe_results = await run_attacks(
        red_default, red_default_runner, target_name="red_default"
    )

    print("\n--- Attacks on Red Agent (advance) (bonus B2 nếu LEAKED) ---")
    red_advance, red_advance_runner = create_red_agent_advance()
    guards_results = await run_attacks(
        red_advance, red_advance_runner, target_name="red_advance"
    )

    save_attack_results(
        unsafe_results=unsafe_results,
        guards_results=guards_results,
        ai_attacks=None,
    )

    bonus_leaks = sum(1 for r in guards_results if r.get("leaked"))
    print("\n" + "=" * 60)
    print(
        f"Red Agent (advance) leaks (bonus B2): {bonus_leaks}  "
        "→ +2/leak max +5 (tổng bonus lab ≤ +10) sau khi grader replay"
    )
    from core.config import is_harder_model, provider_label

    if is_harder_model():
        print(
            f"Hard model ({provider_label()}): "
            "Red Agent (default) leak → bonus B1 +5 nếu grader replay OK"
        )
    print("=" * 60)

    return {
        "red_default": unsafe_results,
        "red_advance": guards_results,
        # aliases cho tooling cũ
        "unsafe": unsafe_results,
        "guards": guards_results,
    }


async def part5_optional_testing():
    """Optional enrichment (không chấm)."""
    print("\n" + "=" * 60)
    print("OPTIONAL: Security Testing Pipeline (không chấm)")
    print("=" * 60)

    from testing.testing import run_comparison, print_comparison, SecurityTestPipeline
    from agents.agent import create_red_agent_default

    print("\n--- Before/After Comparison ---")
    unprotected, protected = await run_comparison()
    if unprotected and protected:
        print_comparison(unprotected, protected)
    else:
        print("Optional — chưa implement, bỏ qua.")

    print("\n--- Security Test Pipeline ---")
    agent, runner = create_red_agent_default()
    pipeline = SecurityTestPipeline(agent, runner)
    results = await pipeline.run_all()
    if results:
        pipeline.print_report(results)
    else:
        print("Optional — chưa implement, bỏ qua.")


def part6_optional_hitl():
    """Optional enrichment (không chấm)."""
    print("\n" + "=" * 60)
    print("OPTIONAL: HITL code (không chấm)")
    print("=" * 60)
    print("Optional enrichment — không chấm.\n")

    from hitl.hitl import test_confidence_router, test_hitl_points

    print("\n--- Confidence Router ---")
    test_confidence_router()

    print("\n--- HITL Decision Points ---")
    test_hitl_points()


async def main(parts=None):
    setup_api_key()

    if parts is None:
        parts = [2, 3, 4]  # Core: CP2 → CP3 → CP4

    for part in parts:
        if part == 2:
            await part2_guardrails()
        elif part == 3:
            await part3_assignment_suite()
        elif part == 4:
            await part4_attacks()
        elif part == 5:
            await part5_optional_testing()
        elif part == 6:
            part6_optional_hitl()
        else:
            print(
                f"Unknown part: {part}. "
                "Dùng 2=CP2, 3=CP3, 4=CP4 (core) · 5/6=optional."
            )

    print("\n" + "=" * 60)
    print("Lab 11 complete! Check your results above.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Lab 11: Guardrails / HITL / Red Team — "
            "--part khớp Checkpoint (2, 3, 4)"
        )
    )
    parser.add_argument(
        "--part",
        type=int,
        choices=[2, 3, 4, 5, 6],
        help=(
            "2=CP2 guardrails · 3=CP3 suite · 4=CP4 red-team · "
            "5/6=optional (không chấm)"
        ),
    )
    args = parser.parse_args()

    if args.part:
        asyncio.run(main(parts=[args.part]))
    else:
        asyncio.run(main())
