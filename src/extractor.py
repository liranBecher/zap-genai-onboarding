import re
from typing import Optional
import html

from src.models import BusinessProfile


def normalize_source_text(text: str) -> str:
	# Remove script/style blocks and tags so extraction works for HTML inputs.
	text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', text, flags=re.IGNORECASE | re.DOTALL)
	text = re.sub(
		r'</?(?:h[1-6]|p|li|br|section|article|main|header|footer|nav|title|ul|ol|div|tr|td)[^>]*>',
		'\n',
		text,
		flags=re.IGNORECASE,
	)
	text = re.sub(r'<[^>]+>', ' ', text)
	text = html.unescape(text)
	text = re.sub(r'\r\n?', '\n', text)
	text = re.sub(r'[ \t]+', ' ', text)
	text = re.sub(r'\n{3,}', '\n\n', text)
	return text.strip()


def extract_phones(text: str) -> list[str]:
	# Supports international and local-like phone formats.
	pattern = r'(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3,4}[\s.-]?\d{3,4}(?!\w)'
	matches = re.findall(pattern, text)

	normalized = []
	for match in matches:
		cleaned = re.sub(r'\s+', ' ', match).strip(' .-')
		digits = re.sub(r'\D', '', cleaned)
		if 8 <= len(digits) <= 15:
			normalized.append(cleaned)

	return sorted(set(normalized))


def extract_emails(text: str) -> list[str]:
	pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
	matches = re.findall(pattern, text)
	return sorted(set(matches))


def detect_services(text: str) -> list[str]:
	service_hints = [
		"השירותים שלנו", "קטגוריות שירות", "פירוט שירותים", "תחומי שירות",
		"שירותים:", "שירותים שלנו:",
	]
	service_section_end_hints = ["שעות פעילות", "יצירת קשר", "כתובת", "אודות", "אזורי שירות", "צור קשר"]
	service_keywords = ["תיקון", "התקנה", "ניקוי", "תחזוקה", "מילוי", "מזגן", "מיזוג", "שירות"]

	def clean_part(part: str) -> str:
		cleaned = part.strip(" \t-•*|,.;:")
		cleaned = re.sub(r'\s+', ' ', cleaned)
		return cleaned

	lines = [line.strip() for line in text.splitlines() if line.strip()]
	found = []
	in_service_section = False

	for line in lines:
		line_lower = line.lower()
		if any(end_hint in line for end_hint in service_section_end_hints):
			in_service_section = False

		if any(hint in line_lower for hint in service_hints):
			in_service_section = True
			if ":" in line:
				candidate = line.split(":", 1)[1].strip()
				if candidate:
					parts = re.split(r'[,/|]', candidate)
					for part in parts:
						item = clean_part(part)
						if 3 <= len(item) <= 90 and "@" not in item:
							found.append(item)
			continue

		is_bullet_or_numbered = line.startswith(("-", "•", "*")) or re.match(r'^\d+[\).\-]\s*', line)
		is_service_line = in_service_section and any(keyword in line for keyword in service_keywords)
		if not (in_service_section and (is_bullet_or_numbered or is_service_line)):
			continue

		candidate = line
		candidate = re.sub(r'^\d+[\).\-]\s*', '', candidate)
		for separator in [":", "-", "–", "—"]:
			if separator in candidate:
				candidate = candidate.split(separator, 1)[1]
				break

		parts = re.split(r'[,/|]', candidate)
		for part in parts:
			item = clean_part(part)
			if 3 <= len(item) <= 90 and "@" not in item and item not in service_section_end_hints:
				found.append(item)

	return sorted(set(found))


def detect_regions(text: str) -> list[str]:
	location_hints = [
		"אזור", "אזורי שירות", "משרתים", "פעילים ב", "פועלים ב",
		"כתובת", "עיר", "מחוז", "מיקום", "ישוב", "יישוב",
	]

	lines = [line.strip() for line in text.splitlines() if line.strip()]
	found = []

	for line in lines:
		line_lower = line.lower()
		if any(hint in line_lower for hint in location_hints):
			if ":" not in line and not line.startswith(("-", "•", "*")):
				continue
			candidate = line.split(":", 1)[1] if ":" in line else line
			candidate = re.sub(r'\s+', ' ', candidate).strip(" -•*|,.;")
			if 2 <= len(candidate) <= 80:
				found.append(candidate)

	return sorted(set(found))


def detect_address(text: str) -> Optional[str]:
	lines = [line.strip() for line in text.splitlines() if line.strip()]
	address_hints = [
		"כתובת",
	]

	for line in lines:
		line_lower = line.lower()
		if any(hint in line_lower for hint in address_hints):
			candidate = line
			if ":" in candidate:
				candidate = candidate.split(":", 1)[1].strip()
			if candidate and candidate != "כתובת":
				return candidate
			continue

		# Fallback for plain address-like patterns in Hebrew context.
		if re.search(r'\b(?:רחוב|רח׳|שד(?:רות)?|שכונה|בניין|כניסה|קומה|ת\.?ד\.?)\b', line):
			if len(line) <= 120:
				return line

	return None


def detect_business_name(text: str) -> Optional[str]:
	lines = [line.strip() for line in text.splitlines() if line.strip()]
	business_indicators = ["מיזוג", "טכנאי", "שירותי"]
	noise_indicators = ["דף בית", "אודות", "שירותים", "צור קשר", "אזורי שירות"]

	for line in lines:
		if any(indicator in line for indicator in business_indicators) and len(line) <= 80 and "|" not in line:
			candidate = re.sub(r'^(אודות|דף בית|דף|צור קשר|שירותים)\s+', '', line).strip()
			return candidate

	for line in lines:
		line_lower = line.lower()
		if "@" in line_lower:
			continue
		if line.startswith("<!") or line.startswith("<"):
			continue
		if line_lower.startswith(("http://", "https://", "www.")):
			continue
		if any(noise in line for noise in noise_indicators):
			continue
		if "|" in line:
			continue
		if re.search(r'(טלפון|נייד|דוא"ל|דואל|אימייל|יצירת קשר|וואטסאפ|פייסבוק|אינסטגרם)', line):
			continue
		if 2 <= len(line) <= 80:
			return line

	return None


def infer_business_type(text: str, services: list[str]) -> Optional[str]:
	text_lower = text.lower()
	service_blob = " ".join(services).lower()

	category_hints = {
		"מסחר וקמעונאות": ["חנות", "קמעונאות", "קטלוג", "מוצרים", "רכישה", "משלוחים"],
		"שירותים מקצועיים": ["ייעוץ", "משרד", "סוכנות", "ראיית חשבון", "עריכת דין", "עצמאי"],
		"בריאות": ["מרפאה", "רופא", "רפואי", "טיפול", "שיניים", "בריאות"],
		"מזון ומשקאות": ["מסעדה", "בית קפה", "מאפייה", "תפריט", "משלוח", "בר"],
		"שירותי בית": ["תיקון", "התקנה", "תחזוקה", "ניקוי", "חשמל", "אינסטלציה", "מזגן", "מיזוג"],
		"חינוך והדרכה": ["קורס", "הדרכה", "בית ספר", "אקדמיה", "מורה", "סדנה"],
	}

	for category, hints in category_hints.items():
		if any(hint in text_lower or hint in service_blob for hint in hints):
			return category

	return None


def derive_product_categories(services: list[str]) -> list[str]:
	categories = []
	for service in services:
		normalized = service.strip()
		if normalized and normalized not in categories:
			categories.append(normalized)
		if len(categories) >= 6:
			break

	return categories


def build_initial_profile(assets: list[dict]) -> BusinessProfile:
	normalized_assets = [
		{
			"source_name": asset["source_name"],
			"content": normalize_source_text(asset["content"]),
		}
		for asset in assets
	]

	combined_text = "\n".join(asset["content"] for asset in normalized_assets)

	business_name = detect_business_name(normalized_assets[0]["content"]) if normalized_assets else None
	phones = extract_phones(combined_text)
	emails = extract_emails(combined_text)
	services = detect_services(combined_text)
	regions = detect_regions(combined_text)
	address = detect_address(combined_text)
	business_type = infer_business_type(combined_text, services)
	categories = derive_product_categories(services)

	profile = BusinessProfile(
		business_name=business_name,
		business_type=business_type,
		region=regions[0] if regions else None,
		phone_numbers=phones,
		emails=emails,
		address=address,
		service_areas=regions,
		services=services,
		product_categories=categories,
		digital_assets=[asset["source_name"] for asset in normalized_assets],
	)

	if not profile.phone_numbers:
		profile.missing_information.append("מספר טלפון")
	if not profile.emails:
		profile.missing_information.append("כתובת אימייל")
	if not profile.services:
		profile.missing_information.append("שירותים")
	if not profile.region:
		profile.missing_information.append("אזור שירות ראשי")

	return profile
