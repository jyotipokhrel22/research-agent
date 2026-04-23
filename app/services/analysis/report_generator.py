from app.schemas.gap_analysis import CandidateGap


def render_gap_summary(gap: CandidateGap) -> str:
    evidence = gap.evidence
    support_line = (
        f"Supported by {evidence.support_count} papers"
        f" ({evidence.recent_support_count} recent, {evidence.influential_support_count} influential)."
    )
    return " ".join(
        part
        for part in [
            gap.statement,
            support_line,
            f"Why it matters: {gap.why_it_matters}",
            f"Action: {gap.actionable_opportunity}",
        ]
        if part
    )


def render_report(gaps: list[CandidateGap]) -> list[dict]:
    return [
        {
            "gap_id": gap.gap_id,
            "category": gap.category,
            "title": gap.title,
            "summary": render_gap_summary(gap),
            "score": gap.overall_score,
        }
        for gap in gaps
    ]
