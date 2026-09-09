from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routers import ml_evaluation

from app.config import get_settings
from app.routers import applications, auth_routes, duplicates, email_sync, webhooks  ,assessments,ai_interviews,final_selection
from app.services.rate_limit import limiter

from app.routers.job_requirements import router as job_requirements_router

from app.routers import departments
from app.routers import shortlisting
from app.routers import interviews

from app.routers.offer_letters import router as offer_letters_router



settings = get_settings()

app = FastAPI(
    title="HRMS API",
    version="0.2.0-phase2",
    description="HR Recruitment Management System backend — Phase 1 (data model, "
    "application intake, HR auth) + Phase 2 (email ingestion, duplicate detection, "
    "bounce handling).",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(auth_routes.router)
app.include_router(duplicates.router)
app.include_router(email_sync.router)
app.include_router(webhooks.router)

app.include_router(job_requirements_router)

app.include_router(departments.router)

app.include_router(shortlisting.router)

app.include_router(assessments.router)

app.include_router(ai_interviews.router)

app.include_router(interviews.router)

app.include_router(final_selection.router)

app.include_router(
    offer_letters_router
)
app.include_router(
    ml_evaluation.router
)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
