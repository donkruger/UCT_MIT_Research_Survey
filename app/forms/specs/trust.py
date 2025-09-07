from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="trust",
    title="Trust",
    sections=[
        # GENERAL ENTITY DETAILS
        Section(
            title="Entity Details",
            fields=create_entity_details_fields("Entity Name (Trust Name)", include_trust_fields=True)
        ),
        Section(
            title="Trust Physical Address",
            component_id="address",
            component_args={
                "instance_id": "physical_address",
                "title": "Trust Physical Address"
            }
        ),
        Section(
            title="Authorised Representative",
            component_id="authorised_representative",
            component_args={
                "instance_id": "auth_rep",
                "title": "Authorised Representative"
            }
        ),
        Section(
            title="Entity Documents",
            fields=create_entity_document_upload_fields("TRUST")
        ),
        
        # Required Roles per Entity Roles Rules Specification - Trusts
        Section(
            title="Trust Founder / Settlor",
            component_id="natural_persons",
            component_args={
                "instance_id": "founder",
                "title": "Trust Founder / Settlor (Natural Person Only)",
                "role_label": "Founder",
                "min_count": 1,           # Required
                "show_uploads": True,
                "help_text": "The Trust Founder/Settlor must be a natural person."
            }
        ),
        Section(
            title="Trustees (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "trustees_natural",
                "title": "Natural Person Trustees",
                "role_label": "Trustee",
                "min_count": 1,           # At least one Trustee required
                "show_uploads": True,
                "help_text": "Natural person trustees."
            }
        ),
        Section(
            title="Trustees (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "trustees_juristic", 
                "title": "Juristic Entity Trustees",
                "role_label": "Trustee",
                "min_count": 0,
                "help_text": "Juristic entity trustees. Beneficial owners must be captured."
            }
        ),
        Section(
            title="Beneficiaries (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "beneficiaries_natural",
                "title": "Natural Person Beneficiaries",
                "role_label": "Beneficiary",
                "min_count": 1,           # At least one Beneficiary required
                "show_uploads": True,
                "help_text": "Natural person beneficiaries."
            }
        ),
        Section(
            title="Beneficiaries (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "beneficiaries_juristic", 
                "title": "Juristic Entity Beneficiaries",
                "role_label": "Beneficiary",
                "min_count": 0,
                "help_text": "Juristic entity beneficiaries. Beneficial owners must be captured."
            }
        ),
        
        # FATCA / CRS - Always last (different exercise from ReFICA)
        Section(
            title="FATCA Classification",
            component_id="fatca_section",
            component_args={
                "instance_id": "fatca_info",
                "title": "FATCA Classification"
            }
        ),
        Section(
            title="CRS Classification",
            component_id="crs_section",
            component_args={
                "instance_id": "crs_info",
                "title": "CRS Classification"
            }
        ),
    ]
)
