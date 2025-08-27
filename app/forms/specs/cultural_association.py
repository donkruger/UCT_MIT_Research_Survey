from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="cultural_association",
    title="Cultural Association",
    sections=[
        Section(
            title="Entity Details",
            fields=create_entity_details_fields()
        ),
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

        Section(
            title="Authorised Representative",
            component_id="authorised_representative",
            component_args={
                "instance_id": "auth_rep",
                "title": "Authorised Representative"
            }
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
            title="Entity Documents",
            fields=create_entity_document_upload_fields("CULTURAL_ASSOCIATION")
        ),
        
        Section(
            title="Committee Members",
            component_id="natural_persons",
            component_args={
                "instance_id": "committee_members",
                "title": "Committee Members",
                "role_label": "Committee Member",
                "min_count": 1,
                "show_uploads": True
            }
        ),
    ]
)