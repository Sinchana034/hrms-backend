from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_hr_admin
from app.services.offer_letter_service import (
    generate_offer_letter,
    get_offer_letters,
)

router = APIRouter(
    prefix="/offer-letters",
    tags=["offer-letters"],
)


class OfferLetterRequest(BaseModel):

    salary: str

    joining_date: str


# =========================================================
# GENERATE OFFER LETTER
# =========================================================

@router.post("/{application_id}")
async def create_offer_letter(
    application_id: str,
    data: OfferLetterRequest,
    user: CurrentUser = Depends(
        require_hr_admin
    ),
):

    try:

        return generate_offer_letter(
            application_id=application_id,
            salary=data.salary,
            joining_date=data.joining_date,
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# =========================================================
# GET OFFER LETTERS
# =========================================================

@router.get("/")
async def list_offer_letters(
    user: CurrentUser = Depends(
        require_hr_admin
    ),
):

    try:

        return get_offer_letters()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )