from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PublicModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Page[T](PublicModel):
    items: list[T]
    page: int
    page_size: int
    total: int
    pages: int


class InstitutionRef(PublicModel):
    id: str
    slug: str
    official_name: str


class EvidenceRef(PublicModel):
    id: str
    title: str
    locator: str
    observed_at: datetime
    source_name: str
    source_url: str
    official_source: bool


class AuthoritySummary(PublicModel):
    appointment_id: str
    person_id: str
    public_name: str
    position: str
    appointment_status: str


class TransparencySummary(PublicModel):
    assessment_id: str
    assessment_date: date
    methodology_version: str
    normalized_score: Decimal
    coverage_percentage: Decimal
    maturity_status: str


class ExecutiveSummary(PublicModel):
    total_institutions: int
    total_active_institutions: int
    total_ministries: int
    presidency_present: bool
    vice_presidency_present: bool
    total_current_authorities: int
    total_relationships: int
    institutions_with_transparency_assessment: int
    institutions_with_complete_assessment: int
    institutions_with_partial_assessment: int
    latest_data_update: datetime | None
    methodology_versions: list[str]
    ranking_enabled: Literal[False] = False
    data_scope: str
    limitations: list[str]


class InstitutionListItem(PublicModel):
    id: str
    slug: str
    official_name: str
    short_name: str | None
    institution_type: str
    status: str
    parent_institution: InstitutionRef | None
    official_website: str | None
    current_authority_summary: AuthoritySummary | None
    latest_transparency_summary: TransparencySummary | None
    source_count: int
    last_verified_at: datetime | None


class LegalDocument(PublicModel):
    id: str
    norm_type: str
    number: str
    date: date | None
    title: str
    url: str | None
    located: bool
    searchable: bool | None
    source: EvidenceRef
    observations: str | None
    limitations: list[str] = Field(default_factory=list)


class RelationshipItem(PublicModel):
    id: str
    direction: Literal["incoming", "outgoing"]
    source_institution: InstitutionRef
    target_institution: InstitutionRef
    relationship_type: str
    valid_from: date | None
    valid_to: date | None
    is_current: bool
    evidence: EvidenceRef
    legal_basis: list[LegalDocument]
    verification_status: str


class AuthorityDetail(PublicModel):
    appointment_id: str
    person_id: str
    public_name: str
    position: str
    position_type: str
    institution: InstitutionRef
    capacity: str | None
    appointment_status: str
    start_date: date | None
    end_date: date | None
    appointment_act: str | None
    appointment_mechanism: str | None
    act_located: bool
    appointment_evidence: list[EvidenceRef]
    current_status_evidence: list[EvidenceRef]
    verification_level: str
    limitations: list[str]


class TransparencyComponent(PublicModel):
    dimension: str
    awarded_score: Decimal
    maximum_score: Decimal
    rule_code: str | None
    public_explanation: str
    calculation_reason: str
    evidence: EvidenceRef
    observation_status: str
    checked_at: datetime | None


class TransparencyAssessmentPublic(PublicModel):
    assessment_id: str
    assessment_date: date
    methodology_version: str
    raw_score: Decimal
    evaluated_max_score: Decimal
    normalized_score: Decimal
    coverage_percentage: Decimal
    maturity_status: str
    rank: None = None
    comparison_position: None = None
    ranking_enabled: Literal[False] = False
    components: list[TransparencyComponent]
    public_explanation: str
    limitations: list[str]


class TransparencyResponse(PublicModel):
    latest_assessment: TransparencyAssessmentPublic | None
    historical_assessments: list[TransparencySummary]
    ranking_enabled: Literal[False] = False
    limitations: list[str]


class InstitutionDetail(PublicModel):
    id: str
    slug: str
    official_name: str
    short_name: str | None
    institution_type: str
    status: str
    creation_date: date | None
    functions_summary: str | None
    legal_basis_summary: list[LegalDocument]
    official_website: str | None
    current_authority: AuthorityDetail | None
    current_relationships: list[RelationshipItem]
    official_sources: list[EvidenceRef]
    evidence: list[EvidenceRef]
    latest_transparency_assessment: TransparencyAssessmentPublic | None
    assessment_history: list[TransparencySummary]
    documentary_gaps: list[str]
    last_updated_at: datetime | None
    public_limitation: str


class AuthorityListItem(PublicModel):
    person_id: str
    appointment_id: str
    public_name: str
    position: str
    institution: InstitutionRef
    appointment_status: str
    start_date: date | None
    end_date: date | None
    appointment_act_status: str
    verification_status: str


class PersonAuthorityDetail(PublicModel):
    person_id: str
    public_name: str
    positions: list[str]
    appointments: list[AuthorityDetail]
    periods: list["AuthorityPeriod"]
    evidence: list[EvidenceRef]
    related_institutions: list[InstitutionRef]
    limitations: list[str]


class AuthorityPeriod(PublicModel):
    start_date: date | None
    end_date: date | None


class ChangeItem(PublicModel):
    id: str
    change_type: str
    occurred_at: datetime
    institution: InstitutionRef | None
    description: str
    evidence: list[EvidenceRef]
