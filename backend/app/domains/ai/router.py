"""HTTP routes for AI assessments."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.ai import service as ai_service
from app.domains.ai.response_schemas import AssessmentOut
from app.shared.db import get_db
from app.shared.errors import NotFoundError

router = APIRouter(prefix="/incidents", tags=["ai"])


@router.post("/{incident_id}/assess", response_model=AssessmentOut)
def assess_incident(incident_id: str, db: Session = Depends(get_db)) -> AssessmentOut:
    assessment = ai_service.generate_incident_assessment(db, incident_id)
    return AssessmentOut.model_validate(assessment)


@router.get("/{incident_id}/assessment", response_model=AssessmentOut)
def get_assessment(incident_id: str, db: Session = Depends(get_db)) -> AssessmentOut:
    assessment = ai_service.get_latest_assessment(db, incident_id)
    if assessment is None:
        raise NotFoundError(f"No assessment for incident {incident_id}")
    return AssessmentOut.model_validate(assessment)
