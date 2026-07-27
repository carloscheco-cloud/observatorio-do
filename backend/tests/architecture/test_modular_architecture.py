from pathlib import Path

ROOT = Path(__file__).parents[2] / "app"
MODULES = (
    "territories",
    "sources",
    "evidence",
    "institutions",
    "persons",
    "legal_basis",
    "positions",
    "appointments",
)


def test_each_business_module_has_required_layers() -> None:
    for module in MODULES:
        path = ROOT / "modules" / module
        assert path.is_dir()
        for layer in ("models.py", "schemas.py", "service.py", "router.py"):
            assert (path / layer).is_file(), f"{module} lacks {layer}"


def test_modules_do_not_import_http_layer_from_services() -> None:
    for service in (ROOT / "modules").glob("*/service.py"):
        content = service.read_text(encoding="utf-8")
        assert "fastapi" not in content
        assert ".router" not in content


def test_canonical_models_are_separate_from_evidence_and_sources() -> None:
    assert "class Institution" not in (ROOT / "modules/sources/models.py").read_text()
    assert "class Institution" not in (ROOT / "modules/evidence/models.py").read_text()


def test_ai_guards_exist_at_service_and_database_layers() -> None:
    canonical = ("persons", "legal_basis", "positions", "appointments")
    for module in canonical:
        assert "actor_type.lower()" in (ROOT / "modules" / module / "service.py").read_text()
    migration = (
        ROOT.parent / "alembic" / "versions" / "0002_block_3_persons_positions.py"
    ).read_text()
    for table in canonical:
        assert table in migration
    assert "reject_ai_canonical_write" in migration
