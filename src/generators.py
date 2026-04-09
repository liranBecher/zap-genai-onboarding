from src.models import BusinessProfile


def generate_customer_card(profile: BusinessProfile) -> str:
    phones = ", ".join(profile.phone_numbers) if profile.phone_numbers else "לא נמצא"
    emails = ", ".join(profile.emails) if profile.emails else "לא נמצא"
    service_areas = ", ".join(profile.service_areas) if profile.service_areas else "לא נמצא"
    services = ", ".join(profile.services) if profile.services else "לא נמצא"
    categories = ", ".join(profile.product_categories) if profile.product_categories else "לא נמצא"
    assets = ", ".join(profile.digital_assets) if profile.digital_assets else "לא נמצא"
    missing = ", ".join(profile.missing_information) if profile.missing_information else "אין"

    external = profile.external_reputation_signals or {}

    external_section = ""
    if external:
        review_themes = ", ".join(external.get("review_themes", [])) or "אין"
        positive_themes = ", ".join(external.get("top_positive_themes", [])) or "אין"
        risk_themes = ", ".join(external.get("possible_risk_themes", [])) or "אין"
        rating = external.get("rating", "לא זמין")
        sample_count = external.get("sample_count", 0)
        confidence_note = external.get("confidence_note", "")

        external_section = f"""
## איתותי מוניטין חיצוניים
- **מקור:** {external.get("source", "לא ידוע")}
- **דירוג:** {rating}
- **כמות ביקורות שנדגמו:** {sample_count}
- **נושאים מרכזיים בביקורות:** {review_themes}
- **נקודות חיוביות מובילות:** {positive_themes}
- **סיכונים אפשריים:** {risk_themes}
- **הערת אמינות:** {confidence_note}
"""

    return f"""# כרטיס לקוח

## סקירה עסקית
- **שם העסק:** {profile.business_name or "לא נמצא"}
- **סוג העסק:** {profile.business_type or "לא נמצא"}
- **אזור פעילות ראשי:** {profile.region or "לא נמצא"}
- **כתובת:** {profile.address or "לא נמצא"}

## פרטי קשר
- **מספרי טלפון:** {phones}
- **אימיילים:** {emails}

## נכסים דיגיטליים שנסרקו
- {assets}

## שירותים שאותרו
- {services}

## קטגוריות מוצרים ושירותים
- {categories}

## אזורי שירות
- {service_areas}

## מידע חסר לאימות
- {missing}

{external_section}

## דגשים מומלצים לאונבורדינג
- לאשר את מספר הטלפון הראשי ללידים
- לאמת ערוץ קשר מועדף (טלפון / וואטסאפ / אימייל)
- לאשר את השירותים החשובים ביותר לקידום
- לאמת את אזורי השירות והאם יש פעילות גם מחוץ לאזור הראשי
- לבקש שעות פעילות, תמונות, לוגו וחומרי שיווק קיימים
"""


def generate_internal_onboarding_script(profile: BusinessProfile) -> str:
    business_name = profile.business_name or "העסק"
    primary_region = profile.region or "אזור השירות שלכם"
    services = ", ".join(profile.services) if profile.services else "השירותים שלכם"

    external = profile.external_reputation_signals or {}

    reputation_section = ""
    if external:
        positive_themes = ", ".join(external.get("top_positive_themes", [])) or "אין"
        reputation_section = (
            "## הזדמנויות מסרים מבוססות מוניטין\n"
            f"- ביקורות ציבוריות עשויות להעיד על חוזקות כמו: **{positive_themes}**\n"
            "- יש לאמת מול הלקוח שחוזקות אלה אכן משקפות את העסק\n"
            "- לאחר אימות, ניתן לשלב את הנושאים הללו במסרים באתר ובמיני-סייט\n"
        )

    verification_questions = []
    if not profile.phone_numbers:
        verification_questions.append("- מהו מספר הטלפון הראשי ליצירת קשר?")
    if not profile.emails:
        verification_questions.append("- מהי כתובת האימייל הראשית לפניות לקוחות?")
    if not profile.address:
        verification_questions.append("- מהי כתובת העסק או המיקום המרכזי לפעילות?")
    if not profile.region:
        verification_questions.append("- באיזה אזור גיאוגרפי אתם משרתים בעיקר?")
    if not profile.services:
        verification_questions.append("- אילו שירותים הכי חשוב לכם לקדם אונליין?")

    if not verification_questions:
        verification_questions.append(
            "- מצאנו אונליין את פרטי הקשר והשירותים המרכזיים שלכם, ונרצה לאמת שהמידע עדיין מעודכן."
        )

    return f"""# תסריט אונבורדינג פנימי

## פתיחה
שלום, כאן [שם הנציג/ה] מזאפ.  
עברנו על הנכסים הדיגיטליים שלכם והכנו טיוטת אונבורדינג עבור **{business_name}**.  
נרצה לאמת כמה פרטים עסקיים כדי לבנות עבורכם את חבילת האונבורדינג המתאימה ביותר.

## מה זיהינו
זיהינו שהעסק פועל בעיקר באזור **{primary_region}** ומציע שירותים כגון **{services}**.

## אימות מידע
{chr(10).join(verification_questions)}
מספרי הטלפון שמצאנו: {", ".join(profile.phone_numbers) if profile.phone_numbers else "לא נמצא"}  
כתובות האימייל שמצאנו: {", ".join(profile.emails) if profile.emails else "לא נמצא"}  
כתובת שמצאנו: {profile.address or "לא נמצא"}

## מטרות עסקיות
- אילו שירותים הכי חשוב לכם לקדם לצורך יצירת לידים?
- האם אתם מכוונים בעיקר ללקוחות פרטיים, עסקיים או לשניהם?
- האם יש שירות מסוים שתרצו להבליט ראשון באתר ובמיני-סייט?
- האם תרצו להתמקד בקריאות דחופות, התקנות או תחזוקה שוטפת?

## תוכן ונכסים
- האם יש לכם לוגו עסקי שניתן להשתמש בו?
- האם יש לכם תמונות של עבודות, צוות או פרויקטים שבוצעו?
- האם יש לכם טקסטים שיווקיים קיימים, הצעות מחיר או תיאורי שירות?
- האם תרצו להדגיש זמינות, מקצועיות, מהירות או מחיר תחרותי?

{reputation_section}

## שאלות תפעוליות
- מהן שעות הפעילות שלכם?
- האם אתם מספקים שירות חירום?
- האם וואטסאפ הוא ערוץ מועדף לקבלת לידים?
- האם אתם משרתים רק את האזור הראשי או גם ערים ואזורים סמוכים?
- האם השירות ניתן בשפות נוספות מלבד עברית?

## השלבים הבאים
- נסגור את כרטיס הלקוח והגדרת האונבורדינג במערכת ניהול הלקוחות
- נעדכן פרטים חסרים או מתוקנים
- נכין את תוכן האתר והמיני-סייט לפי סדר העדיפויות שלכם
- נאשר יחד את אבן הדרך הבאה ולוחות הזמנים המשוערים
"""


def generate_customer_onboarding_message(profile: BusinessProfile) -> str:
    business_name = profile.business_name or "העסק שלכם"
    business_type = profile.business_type or "הפעילות העסקית"
    region = profile.region or "אזור הפעילות שלכם"
    services = ", ".join(profile.services[:4]) if profile.services else "השירותים שאתם מספקים"
    assets_scanned = ", ".join(profile.digital_assets[:5]) if profile.digital_assets else "נכסים דיגיטליים זמינים"

    missing_lines = [f"- {item}" for item in profile.missing_information[:5]]
    if not missing_lines:
        missing_lines.append("- אימות קצר של פרטי הקשר והשירותים המרכזיים")

    return f"""שלום {business_name},

תודה שהצטרפתם לתהליך האונבורדינג (הטמעה) איתנו.
ביצענו סקירה ראשונית של הנכסים הדיגיטליים שלכם ({assets_scanned}) כדי להכיר טוב יותר את העסק.

מהסקירה זיהינו שמדובר ב-{business_type}, עם פעילות באזור {region}, ושירותים מרכזיים כגון: {services}.

כדי להשלים את ההקמה בצורה מדויקת ומהירה, נשמח לקבל מכם את הפרטים הבאים:
{chr(10).join(missing_lines)}

בנוסף, אם יש ברשותכם לוגו, תמונות עדכניות של עבודות או העסק, וטקסטים שיווקיים קיימים,
נשמח שתשלחו אותם כדי שנוכל לשלב אותם בתהליך.

הצוות שלנו ידאג להמשיך איתכם את התהליך באופן אישי ויעדכן אתכם בשלבים הבאים בקרוב.

ברוכים הבאים למשפחת זאפ,
צוות Customer Support
"""


def generate_crm_payload(
    profile: BusinessProfile,
    internal_onboarding_script: str,
    customer_onboarding_message: str,
) -> dict:
    summary_note = (
        f"נבנה פרופיל אונבורדינג לעסק {profile.business_name or 'לא ידוע'}. "
        f"סוג עסק מזוהה: {profile.business_type or 'לא ידוע'}. "
        f"אזור פעילות ראשי: {profile.region or 'לא ידוע'}. "
        f"שירותים מזוהים: {', '.join(profile.services) if profile.services else 'לא זוהו שירותים'}."
    )

    return {
        "customer_name": profile.business_name,
        "business_type": profile.business_type,
        "region": profile.region,
        "contact_details": {
            "phones": profile.phone_numbers,
            "emails": profile.emails,
            "address": profile.address,
        },
        "service_areas": profile.service_areas,
        "services": profile.services,
        "product_categories": profile.product_categories,
        "value_props": profile.value_props,
        "missing_information": profile.missing_information,
        "confidence_notes": profile.confidence_notes,
        "digital_assets": profile.digital_assets,
        "internal_summary_note": summary_note,
        "internal_onboarding_script": internal_onboarding_script,
        "customer_onboarding_message": customer_onboarding_message,
        "onboarding_status": "מוכן_לבדיקה",
        "next_action": "בדיקת_מפיק_ותיאום_שיחה_עם_לקוח",
    }
