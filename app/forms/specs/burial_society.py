from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="burial_society",
    title="Burial Society",
    sections=[
        # GENERAL ENTITY DETAILS
        Section(
            title="Entity Details",
            fields=create_entity_details_fields()
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
            fields=create_entity_document_upload_fields("BURIAL_SOCIETY")
        ),

        # Required Roles per Entity Roles Rules Specification - Informal Associations
        Section(
            title="Members (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "members_natural",
                "title": "Natural Person Members",
                "role_label": "Member",
                "min_count": 1,           # At least one Member required
                "show_uploads": True,
                "show_member_roles": True,  # Enable Member Role selection for informal associations
                "help_text": "Natural person members with Member Role selection required."
            }
        ),
        Section(
            title="Members (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "members_juristic", 
                "title": "Juristic Entity Members",
                "role_label": "Member",
                "min_count": 0,
                "help_text": "Juristic entity members (beneficial owners not required for informal associations)."
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