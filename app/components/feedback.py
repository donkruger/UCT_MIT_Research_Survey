# app/components/feedback.py

import streamlit as st
import re
from typing import Dict, Any, Optional
from app.utils import persist_text_input, persist_selectbox, persist_text_area

def _is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    email = email.strip()
    if not email:
        return False
    # Basic regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def render_feedback_component() -> Optional[Dict[str, Any]]:
    """
    Renders optional feedback form following project UI conventions.
    Returns: dict with feedback data or None if not submitted
    """
    with st.expander("💬 Share Your Feedback (Optional)", expanded=False):
        st.markdown("""
        <div class="callout-info">
            <p><strong>Help us improve our service</strong></p>
            <p>Your feedback is valuable and completely optional. It will be included with your submission.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Use project's persist_* helpers for session state management
        # Pre-populate entity name if not already set
        if "feedback_entity_name" not in st.session_state and "entity_display_name" in st.session_state:
            st.session_state["feedback_entity_name"] = st.session_state["entity_display_name"]
            
        entity_name = persist_text_input("Entity Name", "feedback_entity_name")
        
        email = persist_text_input("Email", "feedback_email", help="Valid email format required if provided")
        
        category = persist_selectbox(
            "Feedback Category", 
            "feedback_category", 
            options=["", "Bug Report", "Feature Request", "Improvement", "Other"]
        )
        
        # Custom rating component with project styling
        rating = render_satisfaction_rating()
        
        message = persist_text_area(
            "Your Message", 
            "feedback_message", 
            placeholder="Tell us more about your experience..."
        )
        
        # Validate email format if provided
        email_valid = True
        if email and email.strip() and not _is_valid_email(email):
            st.error("⚠️ Please enter a valid email address format.")
            email_valid = False
        
        # Return feedback data if any field is filled and email is valid
        if any([entity_name, email, category, rating, message]) and email_valid:
            return {
                'entity_name': entity_name or "Not provided",
                'email': email or "Not provided",
                'category': category or "Not specified",
                'satisfaction_rating': rating or "Not rated",
                'message': message or "No message provided",
                'submitted': True
            }
    
    return None

def render_satisfaction_rating() -> Optional[int]:
    """Simple dropdown satisfaction rating component."""
    st.markdown("**How satisfied are you with our service?**")
    
    # Simple, reliable dropdown selection
    rating_options = [
        (None, "Select your satisfaction level..."),
        (1, "1 - Very Dissatisfied"),
        (2, "2 - Dissatisfied"), 
        (3, "3 - Neutral"),
        (4, "4 - Satisfied"),
        (5, "5 - Very Satisfied")
    ]
    
    # Get current rating from session state
    current_rating = st.session_state.get("feedback_rating_value", None)
    
    # Determine the index for the current rating
    try:
        default_index = next(i for i, (val, _) in enumerate(rating_options) if val == current_rating)
    except StopIteration:
        default_index = 0
    
    # Use persist_selectbox to maintain consistency with project patterns
    rating_selectbox = st.selectbox(
        "Satisfaction Rating:",
        options=[val for val, _ in rating_options],
        index=default_index,
        format_func=lambda x: next(label for val, label in rating_options if val == x),
        key="feedback_rating_selectbox",
        label_visibility="collapsed"
    )
    
    # Update session state and return the rating
    if rating_selectbox is not None:
        st.session_state["feedback_rating_value"] = rating_selectbox
        return rating_selectbox
    
    return None

def get_rating_text(rating: Optional[int]) -> str:
    """Get descriptive text for rating value."""
    rating_texts = {
        1: "Very Dissatisfied",
        2: "Dissatisfied", 
        3: "Neutral",
        4: "Satisfied",
        5: "Very Satisfied"
    }
    return rating_texts.get(rating, "Click an emoji above to rate your satisfaction")
