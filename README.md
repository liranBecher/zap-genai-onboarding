# GenAI Customer Onboarding Prototype

## Overview

This project demonstrates an AI-assisted onboarding flow for a new business customer.

The prototype simulates a scenario in which Zap onboard a new business customer (an air conditioner technician operating in the Krayot area) by scanning the customer’s digital assets, extracting relevant business information, and generating onboarding materials for internal operational use.

The system produces:
- an initial structured business profile
- an AI-enriched business profile
- a customer card for internal onboarding use
- an internal onboarding call script for the onboarding representative
- a customer-facing onboarding message for automated sending
- a CRM-ready payload

In addition, the prototype includes an optional external reputation enrichment layer, represented here with mocked Google review signals.

---

## Approach

The solution is intentionally split into two layers:

### 1. Deterministic extraction
Traditional code is used for:
- loading and parsing source files
- extracting contact details such as phone numbers and email addresses
- detecting service areas
- identifying core business services
- building an initial structured business profile

### 2. AI enrichment
An LLM is then used to:
- normalize and improve business/service naming
- derive cleaner product/service categories
- identify likely value propositions
- detect missing information that should be verified during onboarding
- generate more operationally useful onboarding outputs

This design was chosen deliberately: instead of relying on LLMs for everything, the prototype uses code for deterministic signals and GenAI for interpretation, normalization, and content generation.
The idea is to give the LLM a precise, noise-free task to get better results and more efficeintly

---

## Pipeline

Input: Digital Assets > Raw Text Extraction > Initial Structured Business Profile > LLM Enrichment > Output: Customer Card / Internal Onboarding Script / Customer Onboarding Message / CRM Payload

---

## Inputs


The prototype currently uses sample/mock digital assets representing:
- a 5 page website (html)
- a Dapei Zahav / listing-style page (txt)

These inputs simulate the onboarding scenario and allow the pipeline to be demonstrated end-to-end.

---

## Outputs

The system generates the following artifacts:

### `output/business_profile.json`
Initial structured profile generated from deterministic extraction logic.

### `output/enhanced_business_profile.json`
AI-enriched and normalized business profile used as the main downstream artifact.

### `output/customer_card.md`
Internal customer card summarizing the business, detected services, contact details, missing information, and onboarding focus areas.

### `output/internal_onboarding_script.md`
A detailed internal onboarding script for the producer, including verification points, business questions, asset collection prompts, and messaging opportunities.

### `output/customer_onboarding_message.md`
A concise customer-facing onboarding message (email/automated format) that summarizes identified details and requests missing information and assets.

### `output/crm_payload.json`
A CRM-ready payload representing how the onboarding package could be passed into a CRM or internal operational system.

---

## Optional: Automatic Customer Email Sending

The pipeline can automatically send `customer_onboarding_message.md` to the first email in `profile.emails`.

Enable this by setting environment variables:

- `AUTO_SEND_CUSTOMER_EMAIL=true`
- `SMTP_HOST=...`
- `SMTP_PORT=587` (or your SMTP port)
- `SMTP_USERNAME=...`
- `SMTP_PASSWORD=...`
- `SMTP_FROM=...` (optional, defaults to `SMTP_USERNAME`)
- `SMTP_USE_TLS=true`

When auto-send is disabled or configuration is missing, the pipeline continues normally and only logs a skip message.

---

## Optional Extension: External Reputation Signals

As an optional enrichment layer, the prototype includes `external_reputation_signals`, currently demonstrated through a mocked Google review-based module.

This extension is intentionally kept separate from the core business profile:
- `value_props` are derived from the customer’s owned digital assets
- `external_reputation_signals` represent customer-perceived strengths inferred from public reviews

These signals are not treated as verified facts. Instead, they are used as:
- internal preparation insights
- optional messaging suggestions
- prompts to validate themes during onboarding calls

This keeps the core onboarding flow grounded in the customer’s owned content while still demonstrating how external public data may enrich operational preparation.

---

## Why GenAI Was Used Here

GenAI is especially useful in this onboarding scenario because the source material is often:
- incomplete
- inconsistent
- unstructured
- spread across multiple digital assets

In this prototype, GenAI adds value by:
- turning messy extracted data into a normalized business profile
- identifying relevant onboarding gaps
- producing operationally useful outputs for internal teams
- helping transform raw digital content into a more scalable onboarding process

The prompt was structed using the commonly used *CO-STAR framework*. It ensures prompts are clear, relevant, and consistent.

---

## Human-in-the-Loop Design

The prototype is designed to accelerate onboarding preparation, while keeping a human producer in the loop for final validation.

Human review is still important for:
- confirming uncertain or inferred business details
- validating public-review-based messaging themes
- approving final CRM updates
- making judgment calls on positioning and content emphasis


## Summary

This prototype demonstrates a pragmatic GenAI-assisted onboarding workflow that combines deterministic extraction with AI enrichment to generate useful operational outputs.

The main idea was to show how we can take existing raw data, and by using GenAI, RESTful APIs and new technologies, we can take daily, time consuming tasks and shorten them while making them richer in content to return more value.