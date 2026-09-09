from app.database import get_service_client


# =========================================================
# GENERATE OFFER LETTER
# =========================================================

def generate_offer_letter(
    application_id: str,
    salary: str,
    joining_date: str,
):

    client = get_service_client()


    # -----------------------------------------------------
    # CHECK APPLICATION
    # -----------------------------------------------------

    application_result = (

        client
        .table("applications")
        .select(
            "application_id,"
            "candidate_name,"
            "email,"
            "position"
        )
        .eq(
            "application_id",
            application_id
        )
        .single()
        .execute()

    )


    application = application_result.data


    if not application:

        raise RuntimeError(
            "Candidate not found"
        )


    # -----------------------------------------------------
    # CHECK FINAL SELECTION
    # -----------------------------------------------------

    selection_result = (

        client
        .table("final_selections")
        .select(
            "prediction,"
            "final_score"
        )
        .eq(
            "application_id",
            application_id
        )
        .single()
        .execute()

    )


    selection = selection_result.data


    if not selection:

        raise RuntimeError(
            "Final selection not found"
        )


    if selection["prediction"] != "Selected":

        raise RuntimeError(
            "Offer letters can only be generated for selected candidates"
        )


    # -----------------------------------------------------
    # SAVE OFFER LETTER
    # -----------------------------------------------------

    offer_data = {

        "application_id":
            application_id,

        "salary":
            salary,

        "joining_date":
            joining_date,

        "status":
            "Generated",

    }


    result = (

        client
        .table("offer_letters")
        .upsert(
            offer_data,
            on_conflict="application_id"
        )
        .execute()

    )


    if not result.data:

        raise RuntimeError(
            "Failed to generate offer letter"
        )


    return {

        "message":
            "Offer letter generated successfully",

        "candidate_name":
            application["candidate_name"],

        "email":
            application["email"],

        "position":
            application["position"],

        "offer":
            result.data[0],

    }


# =========================================================
# GET OFFER LETTERS
# =========================================================

def get_offer_letters():

    client = get_service_client()


    result = (

        client
        .table("offer_letters")
        .select("*")
        .execute()

    )


    return result.data or []