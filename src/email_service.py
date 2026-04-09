import os
import smtplib
from email.message import EmailMessage

from src.models import BusinessProfile


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _markdown_like_text_to_rtl_html(content: str) -> str:
    lines = content.splitlines()
    html_parts = [
        "<html>",
        '<body dir="rtl" style="direction: rtl; text-align: right; font-family: Arial, sans-serif; line-height: 1.6;">',
    ]

    in_list = False
    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append('<div style="height: 8px;"></div>')
            continue

        if line.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h1>{line[2:].strip()}</h1>")
            continue

        if line.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h2>{line[3:].strip()}</h2>")
            continue

        if line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{line[2:].strip()}</li>")
            continue

        if in_list:
            html_parts.append("</ul>")
            in_list = False
        html_parts.append(f"<p>{line}</p>")

    if in_list:
        html_parts.append("</ul>")

    html_parts.append("</body>")
    html_parts.append("</html>")
    return "\n".join(html_parts)


def try_send_customer_onboarding_email(
    profile: BusinessProfile,
    customer_onboarding_message: str,
) -> tuple[bool, str]:
    if not _is_truthy(os.getenv("AUTO_SEND_CUSTOMER_EMAIL", "false")):
        return False, "Customer email auto-send is disabled (AUTO_SEND_CUSTOMER_EMAIL=false)."

    if not profile.emails:
        return False, "No customer email found in profile; skipping auto-send."

    smtp_host = (os.getenv("SMTP_HOST") or "").strip()
    smtp_port = int((os.getenv("SMTP_PORT") or "587").strip())
    smtp_user = (os.getenv("SMTP_USERNAME") or "").strip()
    smtp_password = (os.getenv("SMTP_PASSWORD") or "").strip()
    smtp_from = (os.getenv("SMTP_FROM") or smtp_user).strip()
    use_tls = _is_truthy(os.getenv("SMTP_USE_TLS", "true"))

    if not smtp_host or not smtp_from:
        return False, "Missing SMTP_HOST or SMTP_FROM/SMTP_USERNAME; skipping auto-send."

    if smtp_user and not smtp_password:
        return False, "SMTP_USERNAME is set but SMTP_PASSWORD is missing; skipping auto-send."

    to_email = profile.emails[0]

    message = EmailMessage()
    message["Subject"] = f"המשך תהליך הטמעה - {profile.business_name or 'העסק שלכם'}"
    message["From"] = smtp_from
    message["To"] = to_email
    message.set_content(customer_onboarding_message)
    message.add_alternative(
        _markdown_like_text_to_rtl_html(customer_onboarding_message),
        subtype="html",
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            if use_tls:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
    except Exception as exc:
        return False, f"Email send failed: {exc}"

    return True, f"Customer onboarding email sent to {to_email}."