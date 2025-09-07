from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="partnership",
    title="Partnership",
    sections=[
        # GENERAL ENTITY DETAILS
        Section(
            title="Entity Details",
            fields=create_entity_details_fields("Entity Name (Partnership Name)")
        ),
        Section(
            title="Partnership Physical Address",
            component_id="address",
            component_args={
                "instance_id": "physical_address",
                "title": "Partnership Physical Address"
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
            fields=create_entity_document_upload_fields("PARTNERSHIP")
        ),
        
        # Required Roles per Entity Roles Rules Specification - Partnerships
        Section(
            title="Partners (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "partners_natural",
                "title": "Natural Person Partners",
                "role_label": "Partner",
                "min_count": 1,           # At least one Partner required (can be natural or juristic)
                "show_uploads": True,
                "help_text": "Natural person partners with Partner Interest and Executive Control capture."
            }
        ),
        Section(
            title="Partners (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "partners_juristic", 
                "title": "Juristic Entity Partners",
                "role_label": "Partner",
                "min_count": 0,
                "help_text": "Juristic entity partners with Partner Interest and Executive Control capture."
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
