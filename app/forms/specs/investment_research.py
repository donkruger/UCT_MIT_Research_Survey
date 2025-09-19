"""
Investment Decision-Making Research Survey

This survey evaluates user experience with investment recommendation systems,
focusing on transparency, trust, and explainability of AI-driven financial advice.
"""

from app.forms.engine import FormSpec, Section, Field

# Likert scale for the research questions
RESEARCH_LIKERT_SCALE = [
    "",
    "1 - Strongly Disagree",
    "2 - Disagree", 
    "3 - Neutral",
    "4 - Agree",
    "5 - Strongly Agree"
]

# Trust scale
TRUST_SCALE = [
    "",
    "1 - Completely Untrustworthy",
    "2 - Somewhat Untrustworthy",
    "3 - Neutral",
    "4 - Somewhat Trustworthy",
    "5 - Completely Trustworthy"
]

SPEC = FormSpec(
    name="investment_research",
    title="Investment Decision-Making Research Survey",
    sections=[
        # Participant Characterization for Research Classification
        Section(
            title="Participant Characterization (referring to you, not EasyAI)",
            fields=[
                Field("investment_experience_years", 
                      "How many years of investment experience do you have?", 
                      "select", 
                      required=True, 
                      options=["", "Less than 1 year", "1-3 years", "3-5 years", 
                              "5-10 years", "10-15 years", "More than 15 years"],
                      help_text="Please indicate your total duration of active investment participation"),
                
                Field("investment_proficiency", 
                      "Investment Proficiency Self-Assessment", 
                      "select", 
                      required=True, 
                      options=["", "Nascent (Limited knowledge, learning fundamentals)",
                              "Developing (Growing competence, understanding core concepts)",
                              "Competent (Solid understanding, independent decision-making)",
                              "Proficient (Advanced knowledge, sophisticated strategies)",
                              "Expert (Comprehensive mastery, professional-level expertise)"],
                      help_text="Please assess your current investment knowledge and decision-making capability"),
                
                Field("investment_frequency", 
                      "What is your investment decision frequency?", 
                      "select", 
                      required=True, 
                      options=["", "Daily", "Weekly", "Monthly", 
                              "Quarterly", "Annually", "Rarely"],
                      help_text="How often do you typically make investment decisions or portfolio adjustments?"),
                
                Field("portfolio_complexity", 
                      "Portfolio Complexity", 
                      "select", 
                      required=True, 
                      options=["", "Single asset class (e.g., stocks only)",
                              "Limited diversification (2-3 asset classes)",
                              "Moderate diversification (4-5 asset classes)",
                              "Extensive diversification (6+ asset classes)",
                              "Complex strategies (derivatives, alternatives, etc.)"],
                      help_text="Please characterize the complexity of your investment portfolio"),
            ]
        ),
        
        # PRESCRIPTIVE KNOWLEDGE
        Section(
            title="Prescriptive Knowledge",
            fields=[
                Field("prescriptive_structured", 
                      "Did you see structured recommendations (including timely data, risk indicators, etc.) that guided your decision-making?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = Completely unstructured recommendations; 5 = Extremely clear, well-structured recommendations with disclaimers"),
                Field("prescriptive_missing", 
                      "Describe any missing or unclear elements in the recommendations.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # HUMAN VS. NON-HUMAN ACTORS
        Section(
            title="Human vs. Non-Human Actors",
            fields=[
                Field("human_explanations", 
                      "Did the system provide meaningful explanations for its recommendations and clearly indicate when human intervention might be required?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = Explanations absent or confusing; 5 = Very clear, transparent reasoning and role delineation"),
                Field("human_difficulties", 
                      "Mention any difficulties in understanding or trusting the system's explanations.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # COMPLEXITY AND DECOMPOSITION
        Section(
            title="Complexity and Decomposition",
            fields=[
                Field("complexity_components", 
                      "Were you aware of the different components (risk profiling, data retrieval, disclaimers) used to generate advice?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = No clear breakdown of how decisions were made; 5 = Very transparent breakdown of multiple system components"),
                Field("complexity_improvements", 
                      "Suggest improvements for additional clarity or decomposition.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # TYPES OF CAUSALITY
        Section(
            title="Types of Causality",
            fields=[
                Field("causality_differentiation", 
                      "Did the system differentiate between deterministic data (e.g., Piotroski scores) and probabilistic/subjective factors (e.g., sentiment)?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = No clear distinction; 5 = Very clear, helpful distinction between certain and uncertain data"),
                Field("causality_confusion", 
                      "Note any confusion about which factors were \"fixed\" vs. \"variable.\"", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # MECHANISMS FOR GOAL ACHIEVEMENT
        Section(
            title="Mechanisms for Goal Achievement",
            fields=[
                Field("mechanisms_verification", 
                      "Could you verify the advice (e.g., underlying data sources, or rationales)?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = System gave no verification channels; 5 = System provided extensive verification tools and disclaimers"),
                Field("mechanisms_improvements", 
                      "Propose improvements to disclaimers, data presentation, or verification.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # JUSTIFICATORY KNOWLEDGE
        Section(
            title="Justificatory Knowledge",
            fields=[
                Field("justification_metrics", 
                      "Did the system justify the financial metrics it used (e.g., Piotroski F-score) and explain and substantiate why they matter for investment decisions?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = No justification of metrics; 5 = Clear, robust rationale behind each metric's significance"),
                Field("justification_clarifications", 
                      "Suggest any clarifications or additional theoretical context needed.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # BOUNDARY CONDITIONS
        Section(
            title="Boundary Conditions",
            fields=[
                Field("boundary_understanding", 
                      "Did you understand when and where AVA's recommendations were appropriate (e.g., single-stock buy & hold investment philosophy, vs. high frequency trading)?", 
                      "select", 
                      required=True, 
                      options=RESEARCH_LIKERT_SCALE,
                      help_text="1 = Boundaries not explained; 5 = Extremely clear explanations and investment philosophies"),
                Field("boundary_features", 
                      "Indicate any features or capabilities that would improve your investment research experience.", 
                      "textarea", 
                      required=False),
                Field("boundary_misunderstanding", 
                      "Indicate any ways in which the scope was misunderstood or might be misapplied.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # TRUST
        Section(
            title="Trust",
            fields=[
                Field("trust_insights", 
                      "Would you trust insights provided to inform your investment decisions?", 
                      "select", 
                      required=True, 
                      options=TRUST_SCALE,
                      help_text="1 = Untrustworthy and uninformed; 5 = Trustworthy and informed"),
                Field("trust_improvements", 
                      "Indicate any features or capabilities that would improve your investment research experience.", 
                      "textarea", 
                      required=False),
            ]
        ),
        
        # Additional Comments
        Section(
            title="Additional Comments (Optional)",
            fields=[
                Field("overall_experience", 
                      "Please share any additional thoughts about your overall experience with the investment recommendation system.", 
                      "textarea", 
                      required=False),
                Field("future_participation", 
                      "Would you be interested in participating in future research studies?", 
                      "select", 
                      required=False,
                      options=["", "Yes", "No", "Maybe"]),
            ]
        ),
    ]
)
