import unicodedata
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.persons.models import Person
from app.modules.persons.schemas import PersonCreate


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip())
    unaccented = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(unaccented.casefold().split())


def list_persons(db: Session) -> list[Person]:
    return list(db.scalars(select(Person).order_by(Person.normalized_name)))


def get_person(db: Session, person_id: uuid.UUID) -> Person | None:
    return db.get(Person, person_id)


def create_person(db: Session, payload: PersonCreate, *, actor_type: str = "human") -> Person:
    if actor_type.lower() == "ai":
        raise PermissionError("AI actors cannot write canonical person records")
    person = Person(
        full_name=payload.full_name.strip(),
        normalized_name=normalize_name(payload.full_name),
        national_id_hash=payload.national_id_hash,
        birth_date=payload.birth_date,
        nationality=payload.nationality,
        status=payload.status,
        metadata_=payload.metadata_,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person
