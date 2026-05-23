from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base


def create_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=create_uuid)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)

    companies = relationship("Company", back_populates="user")
    jobs = relationship("JobApplication", back_populates="user")
    preferences = relationship("JobPreference")


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=create_uuid)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    website_url = Column(String)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="companies")
    jobs = relationship("JobApplication", back_populates="company")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(String, primary_key=True, default=create_uuid)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    company_id = Column(
        String,
        ForeignKey("companies.id"),
        nullable=False
    )

    job_title = Column(String, nullable=False)
    status = Column(String, default="APPLIED")
    work_model = Column(String, default="HYBRID")
    location = Column(String)

    salary_min = Column(Integer)
    salary_max = Column(Integer)

    currency = Column(String, default="GBP")

    job_description_url = Column(String)

    applied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="jobs")
    company = relationship("Company", back_populates="jobs")

class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(String, primary_key=True, default=create_uuid)

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    preferred_role = Column(String(150), nullable=False)
    preferred_location = Column(String(100), nullable=False)
    preferred_work_model = Column(String(30), nullable=False)

    minimum_salary = Column(Integer)
    skills = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, default=create_uuid)

    job_id = Column(
        String,
        ForeignKey("job_applications.id"),
        nullable=False
    )

    round_number = Column(Integer, nullable=False)

    interview_type = Column(String, nullable=False)

    scheduled_at = Column(DateTime, nullable=False)

    duration_minutes = Column(Integer, default=30)

    status = Column(String, default="SCHEDULED")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True, default=create_uuid)

    company_id = Column(
        String,
        ForeignKey("companies.id"),
        nullable=False
    )

    first_name = Column(String, nullable=False)
    last_name = Column(String)
    email = Column(String)
    linkedin_url = Column(String)
    role = Column(String)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=create_uuid)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(String, nullable=False)


class JobTag(Base):
    __tablename__ = "job_tags"

    id = Column(String, primary_key=True, default=create_uuid)

    job_id = Column(
        String,
        ForeignKey("job_applications.id"),
        nullable=False
    )

    tag_id = Column(
        String,
        ForeignKey("tags.id"),
        nullable=False
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=create_uuid)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    job_id = Column(
        String,
        ForeignKey("job_applications.id")
    )

    document_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=create_uuid)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(String)

    action = Column(String, nullable=False)

    ip_address = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)