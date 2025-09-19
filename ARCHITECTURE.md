# Research Survey Template - Technical Architecture

## Overview

This document describes the technical architecture of the Research Survey Template application. The system implements a **specification-driven architecture** that provides maximum modularity, reusability, and maintainability for creating custom surveys.

## Core Principles

1. **📋 Specification-Driven**: Surveys are defined declaratively in Python specifications
2. **🔧 Component Reusability**: Common form sections (address, phone) are implemented once and reused
3. **🔒 Instance Isolation**: Multiple instances of the same component can exist without state collisions
4. **📦 Namespace Separation**: Each survey type maintains isolated session state
5. **⚙️ Declarative Configuration**: Surveys are defined using simple field definitions and reusable components
6. **🎯 Consistent Interface**: All components implement the same interface (render/validate/serialize)

## Architecture Flow

```
Survey Specs → Form Engine → Components → Streamlit UI → User
     ↓            ↓             ↓              ↓          ↓
   Define     Orchestrate   Render/      Display    Interact
   Fields     & Validate    Validate     Forms     & Submit
```

## System Components

### 1. Survey Specifications (`app/forms/specs/`)
- **Purpose**: Define survey structure and fields
- **Pattern**: Declarative `FormSpec` objects with sections and fields
- **Example**: `example_survey.py` demonstrates a complete survey

### 2. Form Engine (`app/forms/engine.py`)
- **Purpose**: Orchestrates form rendering, validation, and serialization
- **Core Classes**:
  - `Field`: Individual form field definition
  - `Section`: Group of related fields or component reference
  - `FormSpec`: Complete survey specification
- **Functions**:
  - `render_form()`: Displays the survey UI
  - `validate()`: Checks all validation rules
  - `serialize_answers()`: Converts responses to structured data

### 3. Reusable Components (`app/common_form_sections/`)
- **Base Interface** (`base.py`):
  ```python
  class SectionComponent(ABC):
      def render(ns, instance_id, **config)
      def validate(ns, instance_id, **config) 
      def serialize(ns, instance_id, **config)
  ```
- **Implemented Components**:
  - `AddressComponent`: Physical address collection
  - `PhoneComponent`: Phone number with international support

### 4. Session State Management (`app/utils.py`)
- **Namespace System**: Isolates data per survey type
- **Widget Persistence**: Maintains values across page navigation
- **Key Functions**:
  - `ns_key()`: Creates namespaced keys
  - `inst_key()`: Creates instance-specific keys
  - `persist_*()`: Widget wrapper functions

### 5. Submission Pipeline
- **PDF Generation** (`pdf_generator.py`): Creates formatted PDF summaries
- **CSV Export** (`csv_generator.py`): Exports data in machine-readable format
- **Email Sending** (`email_sender.py`): Sends submissions with attachments
- **Submission Handler** (`components/submission.py`): Orchestrates the submission process

## Data Flow

1. **User Input** → Streamlit widgets with session state persistence
2. **Validation** → Real-time and submission-time validation
3. **Serialization** → Convert UI state to structured dictionary
4. **Export** → Generate PDF/CSV from structured data
5. **Submission** → Email with attachments

## File Structure

```
app/
├── main.py                    # Entry point
├── forms/
│   ├── engine.py             # Core form logic
│   ├── field_helpers.py      # Field generation utilities
│   └── specs/                # Survey definitions
├── common_form_sections/      # Reusable components
├── components/               # UI components
├── pages/                    # Multi-page navigation
└── utils.py                  # Utilities
```

## Adding New Surveys

1. Create specification in `app/forms/specs/`
2. Register in `app/forms/specs/__init__.py`
3. Survey automatically appears in UI

## Adding New Components

1. Create class extending `SectionComponent`
2. Implement `render()`, `validate()`, `serialize()`
3. Register in `app/common_form_sections/__init__.py`
4. Reference in survey specs with `component_id`

## Development Mode

Toggle development mode to:
- Bypass all validation for testing
- Configure custom email recipients
- Test submission workflows quickly

## Best Practices

1. **Field Keys**: Use descriptive, lowercase, underscore-separated keys
2. **Validation**: Add validation rules at field definition level
3. **Help Text**: Provide clear help text for complex fields
4. **Error Messages**: Write user-friendly validation error messages
5. **Component Reuse**: Use existing components before creating new ones
