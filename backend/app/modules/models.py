"""Central model import used only for SQLAlchemy metadata discovery."""

from app.modules.appointments.models import Appointment
from app.modules.budget.models import (
    BudgetAppropriation,
    BudgetClassifier,
    BudgetCycle,
    BudgetExecutionRecord,
    BudgetFinding,
    BudgetModification,
    BudgetProgram,
    BudgetRevenue,
    BudgetVersion,
    FinancingOrganization,
    FundingSource,
    InterinstitutionalTransfer,
)
from app.modules.employment_relationships.models import EmploymentRelationship
from app.modules.evidence.models import Evidence
from app.modules.institutions.models import Institution, InstitutionEvidence
from app.modules.legal_basis.models import LegalBasis
from app.modules.organizational_units.models import (
    OrganizationalEvent,
    OrganizationalUnit,
    OrganizationalUnitEvidence,
    PositionUnitAssignment,
)
from app.modules.payroll_entries.models import PayrollConcept, PayrollEntry, PayrollEntryComponent
from app.modules.payroll_findings.models import PayrollFinding
from app.modules.payroll_periods.models import PayrollPeriod, PayrollVersion
from app.modules.persons.models import Person
from app.modules.positions.models import Position
from app.modules.procurement_processes.models import (
    ContractAmendment,
    ContractDelivery,
    ContractGuarantee,
    ContractPayment,
    ProcurementAward,
    ProcurementBid,
    ProcurementChallenge,
    ProcurementContract,
    ProcurementEvaluation,
    ProcurementFinding,
    ProcurementItem,
    ProcurementLot,
    ProcurementProcess,
    ProcurementVersion,
    PurchaseOrder,
)
from app.modules.sources.models import Source
from app.modules.suppliers.models import Supplier, SupplierHistory
from app.modules.territories.models import Territory

__all__ = [
    "Appointment",
    "BudgetAppropriation",
    "BudgetClassifier",
    "BudgetCycle",
    "BudgetExecutionRecord",
    "BudgetFinding",
    "BudgetModification",
    "BudgetProgram",
    "BudgetRevenue",
    "BudgetVersion",
    "Evidence",
    "EmploymentRelationship",
    "Institution",
    "InstitutionEvidence",
    "InterinstitutionalTransfer",
    "LegalBasis",
    "OrganizationalEvent",
    "OrganizationalUnit",
    "OrganizationalUnitEvidence",
    "Person",
    "PayrollConcept",
    "PayrollEntry",
    "PayrollEntryComponent",
    "PayrollFinding",
    "PayrollPeriod",
    "PayrollVersion",
    "Position",
    "PositionUnitAssignment",
    "ProcurementAward",
    "ProcurementBid",
    "ProcurementChallenge",
    "ProcurementContract",
    "ProcurementEvaluation",
    "ProcurementFinding",
    "ProcurementItem",
    "ProcurementLot",
    "ProcurementProcess",
    "ProcurementVersion",
    "PurchaseOrder",
    "ContractAmendment",
    "ContractDelivery",
    "ContractGuarantee",
    "ContractPayment",
    "Source",
    "Supplier",
    "SupplierHistory",
    "FinancingOrganization",
    "FundingSource",
    "Territory",
]
