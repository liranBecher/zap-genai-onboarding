import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# Prefer project .env over stale terminal/session variables.
load_dotenv(override=True)


def enrich_business_profile(raw_assets: list[dict], initial_profile: dict) -> dict:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env")
    if "your_api_key_here" in api_key.lower():
        raise ValueError("OPENAI_API_KEY is still a placeholder. Put your real key in .env")

    client = OpenAI(api_key=api_key)

    asset_summaries = []
    for asset in raw_assets:
        asset_summaries.append({
            "source_name": asset["source_name"],
            "content": asset["content"][:4000]
        })

    prompt = f"""
Context:
You are helping prepare onboarding materials for a new business client of ZAP.
You have two input sources:
1. Raw text collected from the client's digital assets
2. An initial structured business profile extracted programmatically

Objective:
Produce an enriched, clean, and consistent business profile ready for an onboarding call.
Complete the following tasks:
- Clean and normalize the business profile
- Improve service naming
- Improve product/service categories
- Identify reasonable value propositions from the source texts
- Identify missing information that should be verified during onboarding
- Add reliability notes when information is uncertain or inferred
- Be conservative and do not invent facts not grounded in the text

Writing style:
Use concise, professional, and clear CRM-friendly phrasing.
Prefer consistent, normalized naming across fields and values.

Tone:
Be factual, careful, and reliable.
When information is partial or inferred, state that explicitly in the relevant fields.

Audience:
ZAP onboarding and sales teams who will use this output to prepare for a client call.

Response format:
Return valid JSON only, with exactly these fields:
business_name
business_type
region
phone_numbers
emails
address
service_areas
services
product_categories
digital_assets
value_props
external_reputation_signals
missing_information
confidence_notes

If no external reputation signals are available, return external_reputation_signals as an empty object.

All text values in the JSON must be in Hebrew only.
Allowed exceptions: email addresses, phone numbers, URLs, and filenames.
Do not use English sentences in value content.

Raw assets:
{json.dumps(asset_summaries, ensure_ascii=False, indent=2)}

Initial profile:
{json.dumps(initial_profile, ensure_ascii=False, indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You extract and normalize business onboarding data into strict JSON, and all text values must be in Hebrew."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content
    return json.loads(content)