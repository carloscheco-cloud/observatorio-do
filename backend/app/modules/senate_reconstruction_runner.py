from __future__ import annotations

from pathlib import Path

from app.modules import senate_reconstruction as base

# Official actas can include longer/formal variants than profile display names.
base.ALIASES.setdefault("cristobal-venerado-castillo-liriano", []).append(
    "Cristóbal Venerado Antonio Castillo Liriano"
)


def _final_marker_positions(text: str) -> list[int]:
    haystack = base.normalize(text)
    marker = base.normalize("Pase de lista final")
    positions: list[int] = []
    start = 0
    while True:
        index = haystack.find(marker, start)
        if index < 0:
            return positions
        positions.append(index)
        start = index + len(marker)


def classify_pass(text: str, senator_id: str, *, final: bool) -> str:
    """Classify one real roll-call section without treating the table of contents as a pass."""
    normalized = base.normalize(text)
    positions = _final_marker_positions(text)

    # Actas normally mention "Pase de lista final" once in the index and again
    # in the body. Only the last/body occurrence divides the real first/final passes.
    body_final = positions[-1] if len(positions) >= 2 else None
    if final:
        if body_final is None:
            return "unknown"
        relevant = normalized[body_final:]
    else:
        relevant = normalized[:body_final] if body_final is not None else normalized

    stop_headings = (
        "Senadores ausentes con excusa legítima",
        "Senadores ausentes sin excusa legítima",
        "Senadores incorporados después de comprobado el quórum e iniciada la sesión",
        "Comprobación de quórum",
        "Presentación de excusas",
        "Desarrollo de la sesión",
        "Cierre de la sesión",
    )
    present_chunks = base.section_chunks(relevant, "Senadores presentes", stop_headings)
    excused_chunks = base.section_chunks(
        relevant,
        "Senadores ausentes con excusa legítima",
        stop_headings[1:],
    )
    absent_chunks = base.section_chunks(
        relevant,
        "Senadores ausentes sin excusa legítima",
        stop_headings[2:],
    )

    if base.senator_in_chunks(present_chunks, senator_id):
        return "present"
    if base.senator_in_chunks(excused_chunks, senator_id):
        return "excused"
    if base.senator_in_chunks(absent_chunks, senator_id):
        return "absent"
    return "unknown"


def reconstruct_attendance() -> tuple[list[base.SessionSource], list[base.AttendanceRecord]]:
    sources = base.attendance_sources()
    records: list[base.AttendanceRecord] = []
    for source in sources:
        try:
            text = base.pdf_text(base.fetch(source.url))
        except Exception as exc:
            print(f"SOURCE_ERROR session={source.session} url={source.url} error={exc!r}")
            continue

        has_body_final = len(_final_marker_positions(text)) >= 2
        for senator_id in base.SENATORS:
            first_pass = classify_pass(text, senator_id, final=False)
            final_pass = classify_pass(text, senator_id, final=True) if has_body_final else "unknown"
            late_arrival = base.incorporated_late(text, senator_id)

            # Session-level status is final disposition when the acta has a real final roll call.
            # Otherwise a documented incorporation supersedes an initial absence; otherwise use first pass.
            if final_pass != "unknown":
                status = final_pass
            elif late_arrival:
                status = "present"
            else:
                status = first_pass

            records.append(
                base.AttendanceRecord(
                    session=source.session,
                    senator_id=senator_id,
                    status=status,
                    first_pass=first_pass,
                    final_pass=final_pass,
                    late_arrival=late_arrival,
                    source_url=source.url,
                    source_kind=source.source_kind,
                )
            )
    return sources, records


# Patch the combined reconstruction module so its normal write/summary/SIL flow stays reusable.
base.classify_pass = classify_pass
base.reconstruct_attendance = reconstruct_attendance


if __name__ == "__main__":
    base.write_outputs(Path("data/oed/senate"))
