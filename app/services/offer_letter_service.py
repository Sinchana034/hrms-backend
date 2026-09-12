import io
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.database import get_service_client
from app.services import gmail_client

COMPANY_NAME = "RGT Vertex Recruitment"


# =========================================================
# BUILD OFFER LETTER PDF
# =========================================================

def _build_offer_letter_pdf(
    candidate_name: str,
    position: str,
    salary: str,
    joining_date: str,
) -> bytes:
    """
    Renders a simple one-page offer letter as a PDF and returns the raw
    bytes, ready to attach to an email or store. Kept intentionally plain
    (no logo/letterhead) since none was specified — swap this out for a
    styled template later if a design is provided.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 1 * inch
    top = height - 1 * inch
    line_height = 0.3 * inch

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, top, COMPANY_NAME)

    c.setFont("Helvetica", 10)
    c.drawString(left_margin, top - line_height, today)

    y = top - line_height * 3
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left_margin, y, "Offer of Employment")

    y -= line_height * 1.5
    c.setFont("Helvetica", 11)

    paragraphs = [
        f"Dear {candidate_name},",
        "",
        f"We are pleased to offer you the position of {position} at "
        f"{COMPANY_NAME}. This letter confirms the key details of your "
        "offer below.",
        "",
        f"Position: {position}",
        f"Annual Salary: {salary}",
        f"Joining Date: {joining_date}",
        "",
        "This offer is contingent upon successful completion of any "
        "remaining pre-employment requirements. A formal employment "
        "agreement with complete terms and conditions will follow "
        "separately.",
        "",
        "We are excited about the prospect of you joining our team and "
        "look forward to your confirmation.",
        "",
        "Congratulations once again.",
        "",
        "Sincerely,",
        f"{COMPANY_NAME} — HR Team",
    ]

    max_width = width - 2 * left_margin

    for para in paragraphs:
        if para == "":
            y -= line_height
            continue

        words = para.split(" ")
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 11) > max_width:
                c.drawString(left_margin, y, line)
                y -= line_height
                line = word
            else:
                line = test_line
        if line:
            c.drawString(left_margin, y, line)
            y -= line_height

    c.showPage()
    c.save()

    return buffer.getvalue()


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
        .select("application_id,candidate_name,email,position")
        .eq("application_id", application_id)
        .single()
        .execute()
    )

    application = application_result.data

    if not application:
        raise RuntimeError("Candidate not found")

    # -----------------------------------------------------
    # CHECK FINAL SELECTION
    # -----------------------------------------------------

    selection_result = (
        client
        .table("final_selections")
        .select("prediction,final_score")
        .eq("application_id", application_id)
        .single()
        .execute()
    )

    selection = selection_result.data

    if not selection:
        raise RuntimeError("Final selection not found")

    if selection["prediction"] != "Selected":
        raise RuntimeError(
            "Offer letters can only be generated for selected candidates"
        )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    pdf_bytes = _build_offer_letter_pdf(
        candidate_name=application["candidate_name"],
        position=application["position"],
        salary=salary,
        joining_date=joining_date,
    )

    # -----------------------------------------------------
    # SAVE OFFER LETTER RECORD
    # -----------------------------------------------------

    offer_data = {
        "application_id": application_id,
        "salary": salary,
        "joining_date": joining_date,
        "status": "Generated",
    }

    result = (
        client
        .table("offer_letters")
        .upsert(offer_data, on_conflict="application_id")
        .execute()
    )

    if not result.data:
        raise RuntimeError("Failed to generate offer letter")

    # -----------------------------------------------------
    # EMAIL THE OFFER LETTER TO THE CANDIDATE
    #
    # A send failure must not undo the saved offer letter record —
    # HR can retry sending without regenerating the offer.
    # -----------------------------------------------------

    notification_sent = False
    notification_error = None

    subject = f"Offer of Employment - {application['position']}"
    body = (
        f"Dear {application['candidate_name']},\n\n"
        "Congratulations! Please find your offer letter attached to "
        "this email.\n\n"
        "If you have any questions, please reach out to our HR team.\n\n"
        f"{COMPANY_NAME} — HR Team"
    )

    try:
        creds, account_email = gmail_client.get_ready_credentials("gmail")
        gmail_client.send_email_with_attachment(
            creds,
            from_email=account_email,
            to_email=application["email"],
            subject=subject,
            body_text=body,
            attachment_bytes=pdf_bytes,
            attachment_filename=f"Offer_Letter_{application['candidate_name'].replace(' ', '_')}.pdf",
            attachment_mimetype="application/pdf",
        )
        notification_sent = True

        client.table("offer_letters").update(
            {"status": "Sent"}
        ).eq("application_id", application_id).execute()

    except Exception as exc:
        notification_error = str(exc)
        print("Offer letter email failed:", notification_error)

    return {
        "message": "Offer letter generated successfully",
        "candidate_name": application["candidate_name"],
        "email": application["email"],
        "position": application["position"],
        "offer": result.data[0],
        "notification_sent": notification_sent,
        "notification_error": notification_error,
    }


# =========================================================
# GET OFFER LETTERS
# =========================================================

def get_offer_letters():
    client = get_service_client()
    result = client.table("offer_letters").select("*").execute()
    return result.data or []