from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime, 
    Float, ForeignKey, Enum, JSON, func, Table
)
from sqlalchemy.orm import relationship
from database.database import Base
import enum

# ===================== ENUMS =====================
class CitizenStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DECEASED = "deceased"

class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    SALARY = "salary"
    FINE = "fine"
    TAX = "tax"

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"

class ElectionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    FINISHED = "finished"

class CourtCaseStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    APPEAL = "appeal"

# ===================== ASSOCIATION TABLES =====================
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

# ===================== MODELS =====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    citizen = relationship("Citizen", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")

class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    citizen_id = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    character_name = Column(String(200), nullable=True)
    birth_date = Column(DateTime(timezone=True), nullable=True)
    gender = Column(String(50), nullable=True)
    cpf = Column(String(14), unique=True, nullable=True)
    rg = Column(String(20), unique=True, nullable=True)
    marital_status = Column(String(50), nullable=True)
    profession = Column(String(100), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    salary = Column(Float, default=0.0)
    cash = Column(Float, default=500.0)
    bank_balance = Column(Float, default=0.0)
    pix_key = Column(String(50), unique=True, nullable=True)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    reputation = Column(Integer, default=0)
    status = Column(Enum(CitizenStatus), default=CitizenStatus.ACTIVE)
    criminal_record = Column(Text, nullable=True)
    licenses = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="citizen")
    job = relationship("Job", back_populates="citizens")
    bank_account = relationship("BankAccount", back_populates="citizen", uselist=False)
    properties = relationship("Property", back_populates="owner")
    vehicles = relationship("Vehicle", back_populates="owner")
    police_records = relationship("PoliceRecord", back_populates="citizen")
    arrests = relationship("Arrest", back_populates="citizen")
    fines = relationship("Fine", back_populates="citizen")
    votes = relationship("Vote", back_populates="citizen")
    court_cases = relationship("CourtCase", foreign_keys="CourtCase.plaintiff_id", back_populates="plaintiff")
    court_cases_defendant = relationship("CourtCase", foreign_keys="CourtCase.defendant_id", back_populates="defendant")
    employees = relationship("Employee", back_populates="citizen")
    transactions_sent = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")
    transactions_received = relationship("Transaction", foreign_keys="Transaction.receiver_id", back_populates="receiver")

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), unique=True)
    agency = Column(String(10), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    is_frozen = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    citizen = relationship("Citizen", back_populates="bank_account")
    transactions = relationship("Transaction", back_populates="bank_account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bank_account = relationship("BankAccount", back_populates="transactions")
    sender = relationship("Citizen", foreign_keys=[sender_id], back_populates="transactions_sent")
    receiver = relationship("Citizen", foreign_keys=[receiver_id], back_populates="transactions_received")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    base_salary = Column(Float, default=0.0)
    category = Column(String(50), nullable=True)
    requirements = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)

    citizens = relationship("Citizen", back_populates="job")
    employees = relationship("Employee", back_populates="job")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=True)
    balance = Column(Float, default=0.0)
    sector = Column(String(100), nullable=True)
    founded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    owner = relationship("Citizen")
    employees = relationship("Employee", back_populates="company")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    position = Column(String(100), nullable=False)
    salary = Column(Float, default=0.0)
    hired_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    citizen = relationship("Citizen", back_populates="employees")
    company = relationship("Company", back_populates="employees")
    job = relationship("Job", back_populates="employees")

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    price = Column(Float, default=0.0)
    rent_price = Column(Float, default=0.0)
    property_type = Column(String(50), nullable=True)
    is_for_sale = Column(Boolean, default=False)
    is_for_rent = Column(Boolean, default=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("Citizen", back_populates="properties")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(200), nullable=False)
    plate = Column(String(20), unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    color = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    price = Column(Float, default=0.0)
    is_stolen = Column(Boolean, default=False)
    is_for_sale = Column(Boolean, default=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("Citizen", back_populates="vehicles")

class PoliceRecord(Base):
    __tablename__ = "police_records"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    citizen = relationship("Citizen", foreign_keys=[citizen_id], back_populates="police_records")
    officer = relationship("Citizen", foreign_keys=[officer_id])

class Arrest(Base):
    __tablename__ = "arrests"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    reason = Column(Text, nullable=False)
    sentence_time = Column(Integer, default=0)
    arrested_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    citizen = relationship("Citizen", foreign_keys=[citizen_id], back_populates="arrests")
    officer = relationship("Citizen", foreign_keys=[officer_id])

class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    citizen = relationship("Citizen", foreign_keys=[citizen_id], back_populates="fines")
    officer = relationship("Citizen", foreign_keys=[officer_id])

class Law(Base):
    __tablename__ = "laws"

    id = Column(Integer, primary_key=True, index=True)
    law_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    penalty = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class Government(Base):
    __tablename__ = "government"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(100), nullable=False)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    term_start = Column(DateTime(timezone=True), nullable=True)
    term_end = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    budget = Column(Float, default=0.0)
    decrees = Column(JSON, default=list)

class Election(Base):
    __tablename__ = "elections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ElectionStatus), default=ElectionStatus.SCHEDULED)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidates = relationship("Candidate", back_populates="election")
    votes = relationship("Vote", back_populates="election")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    proposal = Column(Text, nullable=True)
    party = Column(String(100), nullable=True)
    votes_count = Column(Integer, default=0)

    election = relationship("Election", back_populates="candidates")
    citizen = relationship("Citizen")

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    voted_at = Column(DateTime(timezone=True), server_default=func.now())

    election = relationship("Election", back_populates="votes")
    citizen = relationship("Citizen", back_populates="votes")

class CourtCase(Base):
    __tablename__ = "court_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    plaintiff_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    defendant_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    judge_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    status = Column(Enum(CourtCaseStatus), default=CourtCaseStatus.PENDING)
    verdict = Column(Text, nullable=True)
    sentence = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    plaintiff = relationship("Citizen", foreign_keys=[plaintiff_id], back_populates="court_cases")
    defendant = relationship("Citizen", foreign_keys=[defendant_id], back_populates="court_cases_defendant")
    judge = relationship("Citizen", foreign_keys=[judge_id])

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    discord_user_id = Column(BigInteger, nullable=False)
    category = Column(String(100), nullable=False)
    subject = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    channel_id = Column(BigInteger, nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")

class ServerConfig(Base):
    __tablename__ = "server_configs"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    discord_role_id = Column(BigInteger, nullable=True)
    is_custom = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
