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
    "organizational_units",
    "employment_relationships",
    "payroll_periods",
    "payroll_entries",
    "payroll_findings",
    "budget",
    "procurement_processes",
    "suppliers",
    "creditors",
    "public_debt",
    "asset_categories",
    "public_assets",
    "risk_engine",
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
    canonical = (
        "persons",
        "legal_basis",
        "positions",
        "appointments",
        "organizational_units",
        "employment_relationships",
        "payroll_periods",
        "payroll_entries",
        "budget",
        "procurement_processes",
        "suppliers",
        "creditors",
        "public_debt",
        "asset_categories",
        "public_assets",
    )
    for module in canonical:
        assert "actor_type.lower()" in (ROOT / "modules" / module / "service.py").read_text()
    migrations = list((ROOT.parent / "alembic" / "versions").glob("*.py"))
    for table in canonical:
        assert any(table in migration.read_text() for migration in migrations)
    assert any("reject_ai_canonical_write" in migration.read_text() for migration in migrations)


def test_risk_engine_is_decoupled_from_domain_models() -> None:
    engine = (ROOT / "modules/risk_engine/engine.py").read_text(encoding="utf-8")
    assert "app.modules.payroll" not in engine
    assert "app.modules.budget" not in engine
    assert "app.modules.procurement" not in engine
    assert "app.modules.public_debt" not in engine
    assert "app.modules.public_assets" not in engine


def test_domain_services_do_not_depend_on_risk_engine() -> None:
    for service in (ROOT / "modules").glob("*/service.py"):
        if service.parent.name != "risk_engine":
            assert "risk_engine" not in service.read_text(encoding="utf-8")
