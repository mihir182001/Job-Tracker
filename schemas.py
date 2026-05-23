from pydantic import BaseModel, EmailStr, field_validator, HttpUrl, model_validator
from datetime import datetime
from enum import Enum


class InterviewType(str, Enum):
    TECHNICAL = "TECHNICAL"
    HR = "HR"
    MANAGERIAL = "MANAGERIAL"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"
    FINAL = "FINAL"


class JobStatus(str, Enum):
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    OFFER_RECEIVED = "OFFER_RECEIVED"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"


class WorkModel(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"


class Currency(str, Enum):
    GBP = "GBP"
    USD = "USD"
    EUR = "EUR"
    INR = "INR"
    CAD = "CAD"


class RegisterUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Full name must be at least 2 characters")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")

        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    email: EmailStr
    access_token: str
    token_type: str = "X-Auth-Token"


class CompanyCreate(BaseModel):
    name: str
    website_url: HttpUrl | None = None
    industry: str | None = None

    @field_validator("name")
    @classmethod
    def validate_company_name(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Company name must be at least 2 characters")

        return value

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, value):
        if value is not None:
            value = value.strip()

            if len(value) < 2:
                raise ValueError("Industry must be at least 2 characters")

        return value


class CompanyResponse(BaseModel):
    id: str
    user_id: str
    name: str
    website_url: str | None = None
    industry: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    company_id: str
    job_title: str
    status: JobStatus = JobStatus.APPLIED
    work_model: WorkModel = WorkModel.HYBRID
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: Currency = Currency.GBP
    job_description_url: HttpUrl | None = None

    @field_validator("job_title")
    @classmethod
    def validate_job_title(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Job title must be at least 2 characters")

        return value

    @field_validator("location")
    @classmethod
    def validate_location(cls, value):
        if value is not None:
            value = value.strip()

            if len(value) < 2:
                raise ValueError("Location must be at least 2 characters")

        return value

    @field_validator("salary_min", "salary_max")
    @classmethod
    def validate_salary(cls, value):
        if value is not None and value < 0:
            raise ValueError("Salary cannot be negative")

        return value

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("Minimum salary cannot be greater than maximum salary")

        return self


class JobResponse(BaseModel):
    id: str
    user_id: str
    company_id: str
    job_title: str
    status: JobStatus
    work_model: WorkModel
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: Currency
    job_description_url: str | None = None
    applied_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewCreate(BaseModel):
    job_id: str
    round_number: int
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int = 30

    @field_validator("round_number")
    @classmethod
    def validate_round_number(cls, value):
        if value < 1:
            raise ValueError("Round number must be at least 1")

        return value

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value):
        if value < 15:
            raise ValueError("Interview duration must be at least 15 minutes")

        if value > 300:
            raise ValueError("Interview duration cannot exceed 300 minutes")

        return value


class InterviewResponse(BaseModel):
    id: str
    job_id: str
    round_number: int
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int
    status: str

    class Config:
        from_attributes = True

class JobPreferenceCreate(BaseModel):
    preferred_role: str
    preferred_location: str
    preferred_work_model: WorkModel = WorkModel.HYBRID
    minimum_salary: int | None = None
    skills: list[str] = []

    @field_validator("preferred_role", "preferred_location")
    @classmethod
    def validate_text_fields(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Field must be at least 2 characters")

        return value

    @field_validator("minimum_salary")
    @classmethod
    def validate_minimum_salary(cls, value):
        if value is not None and value < 0:
            raise ValueError("Minimum salary cannot be negative")

        return value

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value):
        if len(value) > 10:
            raise ValueError("Maximum 10 skills are allowed")

        cleaned_skills = []

        for skill in value:
            skill = skill.strip()

            if len(skill) < 2:
                raise ValueError("Each skill must be at least 2 characters")

            cleaned_skills.append(skill)

        return cleaned_skills


class JobPreferenceResponse(BaseModel):
    id: str
    user_id: str
    preferred_role: str
    preferred_location: str
    preferred_work_model: WorkModel
    minimum_salary: int | None = None
    skills: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendedJobResponse(BaseModel):
    job_title: str
    company: str
    location: str
    salary: str
    work_model: WorkModel
    matched_skills: list[str]
    apply_url: str

class SaveRecommendedJobCreate(BaseModel):
    company_name: str
    job_title: str
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: Currency = Currency.GBP
    work_model: WorkModel = WorkModel.HYBRID
    job_description_url: HttpUrl

    @field_validator("company_name", "job_title")
    @classmethod
    def validate_required_text(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Field must be at least 2 characters")

        return value

class DashboardResponse(BaseModel):
    total_companies: int
    total_jobs: int
    total_interviews: int
    total_preferences: int

    applied_jobs: int
    shortlisted_jobs: int
    interview_scheduled_jobs: int
    offer_received_jobs: int
    rejected_jobs: int
    accepted_jobs: int

    success_rate: float