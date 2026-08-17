import json

from app.db.session import SessionLocal
from app.modules.autonomy.mission import status_payload


def main() -> None:
    with SessionLocal() as db:
        print(json.dumps(status_payload(db), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
