from typing import Optional

from pydantic import BaseModel, Field


class BusinessProfile(BaseModel):
	business_name: Optional[str] = None
	business_type: Optional[str] = None
	region: Optional[str] = None
	phone_numbers: list[str] = Field(default_factory=list)
	emails: list[str] = Field(default_factory=list)
	address: Optional[str] = None
	service_areas: list[str] = Field(default_factory=list)
	services: list[str] = Field(default_factory=list)
	product_categories: list[str] = Field(default_factory=list)
	digital_assets: list[str] = Field(default_factory=list)
	value_props: list[str] = Field(default_factory=list)
	missing_information: list[str] = Field(default_factory=list)
	external_reputation_signals: dict = Field(default_factory=dict)
	confidence_notes: list[str] = Field(default_factory=list)
