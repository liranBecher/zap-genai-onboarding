from dotenv import load_dotenv

from src.extractor import build_initial_profile
from src.email_service import try_send_customer_onboarding_email
from src.generators import (
    generate_crm_payload,
    generate_customer_card,
    generate_customer_onboarding_message,
    generate_internal_onboarding_script,
)
from src.llm_enricher import enrich_business_profile
from src.models import BusinessProfile
from src.utils import ensure_output_dir, load_input_files, save_json, save_markdown
from src.APIservice import get_external_reputation_signals


load_dotenv(override=True)


def main():
    ensure_output_dir()

    assets = load_input_files()
    print(f"Loaded {len(assets)} input files.")

    save_json("raw_assets.json", assets)
    print("Saved raw_assets.json")

    profile = build_initial_profile(assets)
    save_json("business_profile.json", profile.model_dump())
    print("Saved business_profile.json")

    enhanced_profile_dict = enrich_business_profile(assets, profile.model_dump())

    external_signals = get_external_reputation_signals(enhanced_profile_dict)
    enhanced_profile_dict["external_reputation_signals"] = external_signals

    save_json("enhanced_business_profile.json", enhanced_profile_dict)
    print("Saved enhanced_business_profile.json")

    enhanced_profile = BusinessProfile(**enhanced_profile_dict)
    customer_card = generate_customer_card(enhanced_profile)
    save_markdown("customer_card.md", customer_card)
    print("Saved customer_card.md")

    internal_onboarding_script = generate_internal_onboarding_script(enhanced_profile)
    save_markdown("internal_onboarding_script.md", internal_onboarding_script)
    print("Saved internal_onboarding_script.md")

    customer_onboarding_message = generate_customer_onboarding_message(enhanced_profile)
    save_markdown("customer_onboarding_message.md", customer_onboarding_message)
    print("Saved customer_onboarding_message.md")

    email_sent, email_status = try_send_customer_onboarding_email(
        enhanced_profile,
        customer_onboarding_message,
    )
    print(email_status)

    crm_payload = generate_crm_payload(
        enhanced_profile,
        internal_onboarding_script,
        customer_onboarding_message,
    )
    save_json("crm_payload.json", crm_payload)
    print("Saved crm_payload.json")

if __name__ == "__main__":
    main()