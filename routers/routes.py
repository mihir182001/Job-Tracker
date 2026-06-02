from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy.orm import Session

from datetime import datetime

from database import get_db

from external_jobs import fetch_arbeitnow_jobs

from logger_config import logger


from models import (
    User,
    Company,
    JobApplication,
    Interview,
    AuditLog,
    JobPreference
)

from schemas import (
    RegisterUser,
    CompanyCreate,
    CompanyResponse,
    JobCreate,
    JobResponse,
    InterviewCreate,
    InterviewResponse,
    LoginRequest,
    LoginResponse,
    JobPreferenceCreate,
    JobPreferenceResponse,
    RecommendedJobResponse,
    SaveRecommendedJobCreate,
    DashboardResponse
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter()


def add_audit_log(
    db: Session,
    user_id: str | None,
    action: str,
    request: Request
):

    ip_address = (
        request.client.host
        if request.client
        else "Unknown"
    )

    log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address
    )

    db.add(log)
    db.commit()


@router.post("/register")
def register_user(
    user_data: RegisterUser,
    request: Request,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        )
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    logger.info(
        f"User registered successfully: {new_user.email}"
    )

    add_audit_log(
        db,
        new_user.id,
        "USER_REGISTERED",
        request
    )

    return {
        "message": "User registered successfully",
        "email": new_user.email
    }


@router.post("/login", response_model=LoginResponse)
def login_user(
    request: Request,
    form_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == form_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        data={"sub": user.email}
    )

    add_audit_log(
        db,
        user.id,
        "USER_LOGIN",
        request
    )

    logger.info(
        f"User logged in successfully: {user.email}"
    )

    return LoginResponse(
        email=user.email,
        access_token=token
    )


@router.post("/companies", response_model=CompanyResponse)
def create_company(
    company_data: CompanyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = Company(
        user_id=current_user.id,
        name=company_data.name,
        website_url=str(company_data.website_url) if company_data.website_url else None,
        industry=company_data.industry
    )

    db.add(company)

    db.commit()

    db.refresh(company)

    logger.info(
        f"Company created: {company.name} by {current_user.email}"
    )

    add_audit_log(
        db,
        current_user.id,
        "COMPANY_CREATED",
        request
    )

    return company


@router.get("/companies", response_model=list[CompanyResponse])
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return (
        db.query(Company)
        .filter(Company.user_id == current_user.id)
        .all()
    )


@router.post("/jobs", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    company = (
        db.query(Company)
        .filter(
            Company.id == job_data.company_id,
            Company.user_id == current_user.id
        )
        .first()
    )

    if not company:

        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    job = JobApplication(
        user_id=current_user.id,
        company_id=job_data.company_id,
        job_title=job_data.job_title,
        status=job_data.status,
        work_model=job_data.work_model,
        location=job_data.location,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        currency=job_data.currency,
        job_description_url=str(job_data.job_description_url) if job_data.job_description_url else None,
        applied_at=datetime.utcnow()
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    logger.info(
        f"Job created: {job.job_title} by {current_user.email}"
    )

    add_audit_log(
        db,
        current_user.id,
        "JOB_CREATED",
        request
    )

    return job


@router.get("/jobs", response_model=list[JobResponse])
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return (
        db.query(JobApplication)
        .filter(JobApplication.user_id == current_user.id)
        .all()
    )

@router.put("/companies/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: str,
    company_data: CompanyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.name = company_data.name
    company.website_url = company_data.website_url
    company.industry = company_data.industry

    db.commit()
    db.refresh(company)

    add_audit_log(db, current_user.id, "COMPANY_UPDATED", request)

    return company


@router.delete("/companies/{company_id}")
def delete_company(
    company_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()

    add_audit_log(db, current_user.id, "COMPANY_DELETED", request)

    return {"message": "Company deleted successfully"}

@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: str,
    job_data: JobCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(JobApplication).filter(
        JobApplication.id == job_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.company_id = job_data.company_id
    job.job_title = job_data.job_title
    job.status = job_data.status
    job.work_model = job_data.work_model
    job.location = job_data.location
    job.salary_min = job_data.salary_min
    job.salary_max = job_data.salary_max
    job.currency = job_data.currency
    job.job_description_url = job_data.job_description_url

    db.commit()
    db.refresh(job)

    add_audit_log(db, current_user.id, "JOB_UPDATED", request)

    return job


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(JobApplication).filter(
        JobApplication.id == job_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

    add_audit_log(db, current_user.id, "JOB_DELETED", request)

    return {"message": "Job deleted successfully"}

@router.post(
    "/interviews",
    response_model=InterviewResponse
)
def create_interview(
    interview_data: InterviewCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == interview_data.job_id,
            JobApplication.user_id == current_user.id
        )
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    interview = Interview(
        job_id=interview_data.job_id,
        round_number=interview_data.round_number,
        interview_type=interview_data.interview_type,
        scheduled_at=interview_data.scheduled_at,
        duration_minutes=interview_data.duration_minutes
    )

    db.add(interview)

    db.commit()

    db.refresh(interview)

    logger.info(
        f"Interview scheduled for job {interview.job_id}"
    )

    add_audit_log(
        db,
        current_user.id,
        "INTERVIEW_CREATED",
        request
    )

    return interview


@router.get(
    "/interviews",
    response_model=list[InterviewResponse]
)
def get_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interviews = (
        db.query(Interview)
        .join(
            JobApplication,
            Interview.job_id == JobApplication.id
        )
        .filter(
            JobApplication.user_id == current_user.id
        )
        .all()
    )

    return interviews

@router.post("/job-preferences", response_model=JobPreferenceResponse)
def create_job_preference(
    preference_data: JobPreferenceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preference = JobPreference(
        user_id=current_user.id,
        preferred_role=preference_data.preferred_role,
        preferred_location=preference_data.preferred_location,
        preferred_work_model=preference_data.preferred_work_model,
        minimum_salary=preference_data.minimum_salary,
        skills=",".join(preference_data.skills)
    )

    db.add(preference)
    db.commit()
    db.refresh(preference)

    logger.info(
        f"Job preference created by {current_user.email}"
    )

    add_audit_log(
        db,
        current_user.id,
        "JOB_PREFERENCE_CREATED",
        request
    )

    return JobPreferenceResponse(
        id=preference.id,
        user_id=preference.user_id,
        preferred_role=preference.preferred_role,
        preferred_location=preference.preferred_location,
        preferred_work_model=preference.preferred_work_model,
        minimum_salary=preference.minimum_salary,
        skills=preference.skills.split(",") if preference.skills else [],
        created_at=preference.created_at
    )


@router.get("/job-preferences", response_model=list[JobPreferenceResponse])
def get_job_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preferences = (
        db.query(JobPreference)
        .filter(JobPreference.user_id == current_user.id)
        .all()
    )

    return [
        JobPreferenceResponse(
            id=preference.id,
            user_id=preference.user_id,
            preferred_role=preference.preferred_role,
            preferred_location=preference.preferred_location,
            preferred_work_model=preference.preferred_work_model,
            minimum_salary=preference.minimum_salary,
            skills=preference.skills.split(",") if preference.skills else [],
            created_at=preference.created_at
        )
        for preference in preferences
    ]


@router.get("/recommended-jobs", response_model=list[RecommendedJobResponse])
def get_recommended_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preference = (
        db.query(JobPreference)
        .filter(JobPreference.user_id == current_user.id)
        .order_by(JobPreference.created_at.desc())
        .first()
    )

    if not preference:
        raise HTTPException(
            status_code=404,
            detail="Please create job preferences first"
        )

    jobs = fetch_arbeitnow_jobs(
        search_query=preference.preferred_role,
        location=preference.preferred_location
    )

    return jobs

@router.post("/save-recommended-job", response_model=JobResponse)
def save_recommended_job(
    job_data: SaveRecommendedJobCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = (
        db.query(Company)
        .filter(
            Company.user_id == current_user.id,
            Company.name == job_data.company_name
        )
        .first()
    )

    if not company:
        company = Company(
            user_id=current_user.id,
            name=job_data.company_name,
            website_url=str(job_data.job_description_url),
            industry="External Job Source"
        )

        db.add(company)
        db.commit()
        db.refresh(company)

    job = JobApplication(
        user_id=current_user.id,
        company_id=company.id,
        job_title=job_data.job_title,
        status="APPLIED",
        work_model=job_data.work_model,
        location=job_data.location,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        currency=job_data.currency,
        job_description_url=str(job_data.job_description_url),
        applied_at=datetime.utcnow()
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(
        f"Recommended job saved: {job.job_title}"
    )

    add_audit_log(
        db,
        current_user.id,
        "RECOMMENDED_JOB_SAVED",
        request
    )

    return job

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_companies = (
        db.query(Company)
        .filter(Company.user_id == current_user.id)
        .count()
    )

    total_jobs = (
        db.query(JobApplication)
        .filter(JobApplication.user_id == current_user.id)
        .count()
    )

    total_interviews = (
        db.query(Interview)
        .join(
            JobApplication,
            Interview.job_id == JobApplication.id
        )
        .filter(
            JobApplication.user_id == current_user.id
        )
        .count()
    )

    total_preferences = (
        db.query(JobPreference)
        .filter(JobPreference.user_id == current_user.id)
        .count()
    )

    applied_jobs = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.status == "APPLIED"
        )
        .count()
    )

    shortlisted_jobs = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.status == "SHORTLISTED"
        )
        .count()
    )

    interview_scheduled_jobs = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.status == "INTERVIEW_SCHEDULED"
        )
        .count()
    )

    offer_received_jobs = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.status == "OFFER_RECEIVED"
        )
        .count()
    )

    rejected_jobs = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.status == "REJECTED"
        )
        .count()
    )

    accepted_jobs = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.status == "ACCEPTED"
        )
        .count()
    )

    success_rate = 0.0

    if total_jobs > 0:
        success_rate = round(
            (
                offer_received_jobs + accepted_jobs
            ) / total_jobs * 100,
            2
        )

    return DashboardResponse(
        total_companies=total_companies,
        total_jobs=total_jobs,
        total_interviews=total_interviews,
        total_preferences=total_preferences,
        applied_jobs=applied_jobs,
        shortlisted_jobs=shortlisted_jobs,
        interview_scheduled_jobs=interview_scheduled_jobs,
        offer_received_jobs=offer_received_jobs,
        rejected_jobs=rejected_jobs,
        accepted_jobs=accepted_jobs,
        success_rate=success_rate
    )