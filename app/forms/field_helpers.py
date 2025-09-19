"""
Field helper utilities for survey forms.

This module provides helper functions to generate common field patterns
and reduce duplication across survey specifications.
"""

from typing import List, Optional
from app.forms.engine import Field
from app.controlled_lists import (
    get_yes_no_options,
    get_agreement_scale,
    get_satisfaction_scale,
    get_frequency_scale,
    get_title_options,
    get_gender_options,
    get_marital_status_options
)

def create_contact_fields(required: bool = False) -> List[Field]:
    """
    Generate standard contact information fields.
    
    Args:
        required: Whether fields should be required
        
    Returns:
        List of Field objects for contact information
    """
    return [
        Field("contact_name", "Full Name", "text", required=required),
        Field("contact_email", "Email Address", "text", required=required),
        Field("contact_phone", "Phone Number", "text", required=required),
        Field("contact_organization", "Organization", "text", required=False),
    ]

def create_demographic_fields(include_optional: bool = True) -> List[Field]:
    """
    Generate demographic information fields.
    
    Args:
        include_optional: Whether to include optional demographic fields
        
    Returns:
        List of Field objects for demographic information
    """
    fields = [
        Field("age", "Age", "number", required=False),
        Field("gender", "Gender", "select", required=False, options=get_gender_options()),
    ]
    
    if include_optional:
        fields.extend([
            Field("marital_status", "Marital Status", "select", 
                  required=False, options=get_marital_status_options()),
            Field("education", "Highest Education Level", "select", required=False,
                  options=["", "High School", "Associate Degree", "Bachelor's Degree", 
                          "Master's Degree", "Doctorate", "Other"]),
            Field("employment", "Employment Status", "select", required=False,
                  options=["", "Employed Full-time", "Employed Part-time", "Self-employed",
                          "Unemployed", "Student", "Retired", "Other"]),
        ])
    
    return fields

def create_likert_scale_field(
    key: str, 
    label: str, 
    scale_type: str = "agreement",
    required: bool = True
) -> Field:
    """
    Create a Likert scale field.
    
    Args:
        key: Field key for session state
        label: Field label to display
        scale_type: Type of scale ('agreement', 'satisfaction', 'frequency')
        required: Whether field is required
        
    Returns:
        Field object with appropriate scale options
    """
    scale_options = {
        "agreement": get_agreement_scale(),
        "satisfaction": get_satisfaction_scale(),
        "frequency": get_frequency_scale(),
        "yes_no": get_yes_no_options(),
    }
    
    options = scale_options.get(scale_type, get_agreement_scale())
    return Field(key, label, "select", required=required, options=options)

def create_rating_fields(
    topics: List[str],
    scale_type: str = "satisfaction",
    required: bool = False
) -> List[Field]:
    """
    Generate a set of rating fields for multiple topics.
    
    Args:
        topics: List of topics to rate
        scale_type: Type of rating scale to use
        required: Whether ratings are required
        
    Returns:
        List of Field objects for ratings
    """
    fields = []
    for topic in topics:
        key = topic.lower().replace(" ", "_").replace("-", "_")
        fields.append(
            create_likert_scale_field(
                f"rating_{key}",
                f"Rate: {topic}",
                scale_type=scale_type,
                required=required
            )
        )
    return fields

def create_feedback_fields(required: bool = False) -> List[Field]:
    """
    Generate standard feedback fields.
    
    Args:
        required: Whether fields should be required
        
    Returns:
        List of Field objects for feedback
    """
    return [
        Field("feedback_positive", "What did you like most?", "textarea", required=required),
        Field("feedback_improve", "What could be improved?", "textarea", required=required),
        Field("feedback_additional", "Any additional comments?", "textarea", required=False),
        Field("feedback_recommend", "Would you recommend this to others?", "select",
              required=required, options=get_yes_no_options()),
    ]

def create_file_upload_field(
    key: str,
    label: str,
    required: bool = False,
    accept_multiple: bool = False
) -> Field:
    """
    Create a file upload field.
    
    Args:
        key: Field key for session state
        label: Field label to display
        required: Whether upload is required
        accept_multiple: Whether to accept multiple files
        
    Returns:
        Field object for file upload
    """
    return Field(
        key=key,
        label=label,
        kind="file",
        required=required,
        accept_multiple=accept_multiple
    )

def create_yes_no_field(key: str, label: str, required: bool = True) -> Field:
    """
    Create a simple yes/no selection field.
    
    Args:
        key: Field key for session state
        label: Field label to display
        required: Whether field is required
        
    Returns:
        Field object with yes/no options
    """
    return Field(key, label, "select", required=required, options=get_yes_no_options())

def create_date_range_fields(
    prefix: str,
    start_label: str = "Start Date",
    end_label: str = "End Date",
    required: bool = False
) -> List[Field]:
    """
    Create a pair of date fields for date ranges.
    
    Args:
        prefix: Prefix for field keys
        start_label: Label for start date
        end_label: Label for end date
        required: Whether dates are required
        
    Returns:
        List with two date Field objects
    """
    return [
        Field(f"{prefix}_start_date", start_label, "date", required=required),
        Field(f"{prefix}_end_date", end_label, "date", required=required),
    ]