## This module simulates an API service that retrieves external reputation signals for a business profile.
## In a real implementation, this would involve making HTTP requests to Google Maps to gather reviews, ratings, and other relevant data.

def get_external_reputation_signals(profile: dict) -> dict:
    business_name = profile.get("business_name")
    region = profile.get("region")

    return {
        "source": "גוגל מפות",
        "matched_place_name": business_name,
        "matched_address": region,
        "sample_count": 5,
        "rating": 4.6,
        "review_themes": [
            "שירות מהיר",
            "מקצועיות",
            "אדיבות"
        ],
        "top_positive_themes": [
            "תגובה מהירה",
            "שירות מקצועי",
            "יחס טוב"
        ],
        "possible_risk_themes": [
            "לא מספיק מידע שלילי כדי לזהות דפוס מובהק"
        ],
        "confidence_note": "האיתותים מבוססים על ביקורות ציבוריות חיצוניות ויש לאמת אותם לפני שימוש במסרים מול לקוחות."
    }