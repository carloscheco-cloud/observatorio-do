from app.main import app


def test_block_3_routes_are_registered() -> None:
    paths = app.openapi()["paths"]
    routes = {(path, method.upper()) for path, operations in paths.items() for method in operations}
    expected = {
        ("/api/v1/persons", "GET"),
        ("/api/v1/persons", "POST"),
        ("/api/v1/persons/{person_id}", "GET"),
        ("/api/v1/persons/{person_id}/appointments", "GET"),
        ("/api/v1/positions", "GET"),
        ("/api/v1/positions", "POST"),
        ("/api/v1/positions/{position_id}", "GET"),
        ("/api/v1/positions/{position_id}/history", "GET"),
        ("/api/v1/appointments", "GET"),
        ("/api/v1/appointments", "POST"),
        ("/api/v1/appointments/active", "GET"),
        ("/api/v1/institutions/{institution_id}/appointments", "GET"),
        ("/api/v1/legal-bases", "GET"),
        ("/api/v1/legal-bases", "POST"),
    }
    assert expected <= routes
