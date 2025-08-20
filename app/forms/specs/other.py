from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="other",
    title="Other",
    sections=[
        Section(
            title="Entity Details",
            fields=create_entity_details_fields()
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
            title="Authorised Representative Address",
            component_id="address",
            component_args={
                "instance_id": "auth_rep_address",
                "title": "Authorised Representative Address"
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
            fields=create_entity_document_upload_fields("OTHER")
        ),
        
        Section(title="Associated People", component_id="natural_persons", component_args={
            "instance_id": "associated", "role_label": "Person", "min_count": 0
        }),
    ]
)
