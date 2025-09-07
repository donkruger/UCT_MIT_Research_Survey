from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="closed_corporation",
    title="Closed Corporation",
    sections=[
        # GENERAL ENTITY DETAILS
        Section(
            title="Entity Details",
            fields=create_entity_details_fields("Entity Name (CC Registered Name)")
        ),
        Section(
            title="Physical Address",
            component_id="address",
            component_args={
                "instance_id": "physical_address",
                "title": "Physical Address"
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
            fields=create_entity_document_upload_fields("CLOSED_CORPORATION")
        ),
        
        # Required Roles per Entity Roles Rules Specification - Closed Corporations
        Section(
            title="CC Members",
            component_id="natural_persons",
            component_args={
                "instance_id": "members",
                "title": "CC Members (Natural Persons Only)",
                "role_label": "Member",
                "min_count": 1,           # At least one Member required
                "show_uploads": True,
                "help_text": "All CC Members must be natural persons. Member Interest Percentage and Executive Control are required."
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
