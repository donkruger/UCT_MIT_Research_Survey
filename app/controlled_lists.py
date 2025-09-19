"""
Generic controlled lists for survey forms.

This module provides common lists of options that can be used in survey questions.
"""

# Gender options
GENDER_OPTIONS = [
    "",
    "Male",
    "Female", 
    "Other",
    "Prefer not to say"
]

# Title options
TITLE_OPTIONS = [
    "",
    "Mr",
    "Ms", 
    "Mrs",
    "Miss",
    "Dr",
    "Prof"
]

# Marital status options  
MARITAL_STATUS_OPTIONS = [
    "",
    "Single",
    "Married",
    "Divorced",
    "Widowed",
    "Other"
]

# Yes/No options
YES_NO_OPTIONS = [
    "",
    "Yes",
    "No"
]

# Agreement scale
AGREEMENT_SCALE = [
    "",
    "Strongly Disagree",
    "Disagree", 
    "Neutral",
    "Agree",
    "Strongly Agree"
]

# Satisfaction scale
SATISFACTION_SCALE = [
    "",
    "Very Dissatisfied",
    "Dissatisfied",
    "Neutral", 
    "Satisfied",
    "Very Satisfied"
]

# Frequency scale
FREQUENCY_SCALE = [
    "",
    "Never",
    "Rarely",
    "Sometimes",
    "Often", 
    "Always"
]

def get_gender_options():
    """Get the list of gender options."""
    return GENDER_OPTIONS.copy()

def get_title_options():
    """Get the list of title options."""
    return TITLE_OPTIONS.copy()

def get_marital_status_options():
    """Get the list of marital status options."""
    return MARITAL_STATUS_OPTIONS.copy()

def get_yes_no_options():
    """Get the list of yes/no options."""
    return YES_NO_OPTIONS.copy()

def get_agreement_scale():
    """Get the agreement scale options."""
    return AGREEMENT_SCALE.copy()

def get_satisfaction_scale():
    """Get the satisfaction scale options."""
    return SATISFACTION_SCALE.copy()

def get_frequency_scale():
    """Get the frequency scale options."""
    return FREQUENCY_SCALE.copy()