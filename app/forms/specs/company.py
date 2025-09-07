from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields, create_entity_document_upload_fields

SPEC = FormSpec(
    name="company",
    title="Company",
    sections=[
        # GENERAL ENTITY DETAILS
        Section(
            title="Entity Details",
            fields=create_entity_details_fields()
        ),
        Section(
            title="Entity Physical Address",
            component_id="address",
            component_args={
                "instance_id": "physical_address",
                "title": "Entity Physical Address"
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
            fields=create_entity_document_upload_fields("COMPANY")
        ),
        
        # Required Roles per Entity Roles Rules Specification - Companies
        Section(
            title="Company Directors",
            component_id="natural_persons",
            component_args={
                "instance_id": "directors",
                "title": "Company Directors (Natural Persons Only)",
                "role_label": "Director",
                "min_count": 1,           # At least one Director required
                "show_uploads": True,
                "help_text": "All Company Directors must be natural persons. Executive Control field is required."
            }
        ),
        
        # Additional Roles - Shareholders (Natural Person or Juristic Entity)
        Section(
            title="Shareholders (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "shareholders_natural",
                "title": "Natural Person Shareholders",
                "role_label": "Shareholder",
                "min_count": 0,
                "show_uploads": True,
                "show_poa_uploads": False,  # Disable POA uploads for shareholders
                "help_text": "Natural person shareholders with percentage shareholding capture. Only ID document required."
            }
        ),
        Section(
            title="Shareholders (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "shareholders_juristic", 
                "title": "Juristic Entity Shareholders",
                "role_label": "Shareholder",
                "min_count": 0,
                "help_text": "Juristic entity shareholders with percentage shareholding capture."
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
