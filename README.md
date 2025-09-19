# Investment Decision-Making Research Survey Application

A professional survey application for conducting research on investment recommendation systems, focusing on transparency, trust, and explainability of AI-driven financial advice.

## 🎯 Research Focus

This application captures user feedback across eight key dimensions:
- **Prescriptive Knowledge** - Structure and clarity of recommendations
- **Human vs. Non-Human Actors** - Understanding system vs. human decision roles
- **Complexity and Decomposition** - Transparency of system components
- **Types of Causality** - Distinguishing deterministic from probabilistic factors
- **Mechanisms for Goal Achievement** - Verification capabilities
- **Justificatory Knowledge** - Understanding of financial metrics
- **Boundary Conditions** - Appropriate application contexts
- **Trust** - Confidence in system insights

## Features

- 📊 **Structured Research Questions**: Likert scales (1-5) and open-text responses
- 💾 **Automatic Data Persistence**: Responses saved across navigation
- 📧 **Email Submission**: Automated delivery to don.kruger123@gmail.com
- 📄 **PDF Export**: Professional summary reports
- 📊 **CSV Export**: Machine-readable data format
- 🔧 **Development Mode**: Test submissions without full validation
- 🎨 **Professional UI**: Clean, research-focused design

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd survey-applet
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure email settings by creating `.streamlit/secrets.toml`:
```toml
[email_credentials]
email_address = "your-email@gmail.com"
app_password = "your-app-password"
recipient_address = "don.kruger123@gmail.com"  # Default recipient
```

**Note**: For Gmail, you need to:
- Enable 2-factor authentication
- Generate an app password at https://myaccount.google.com/apppasswords

4. Run the application:
```bash
streamlit run app/main.py
# OR use the startup script:
./run.sh
```

## 📋 Survey Content

### Investment Decision-Making Research Survey
The research instrument with questions covering all eight research dimensions. Each dimension includes:
- A 5-point Likert scale question with detailed anchors
- An open-text field for qualitative feedback

The survey is automatically loaded when you start the application.

## 🔬 Research Methodology

### Question Structure
Each research dimension follows a consistent pattern:
- **Quantitative**: 5-point Likert scale with specific anchors
- **Qualitative**: Open-text for detailed feedback and suggestions

### Scale Anchors
- 1 = Strongly Disagree / Completely Negative
- 5 = Strongly Agree / Completely Positive
- Each question includes dimension-specific anchor descriptions

## Development Mode

Enable development mode for testing:

1. Expand "🔧 Development Options" on the main page
2. Click "Toggle Dev Mode"
3. Submit with minimal data for testing
4. Configure test email recipients

## Data Export

### PDF Format
- Professional formatted summary
- All responses included
- Timestamp and reference information
- Suitable for records and review

### CSV Format
- Machine-readable format
- Section/Record#/Field/Value structure
- Easy import to analysis tools
- Preserves all response data

## Project Structure

```
survey-applet/
├── app/
│   ├── main.py                    # Main application entry
│   ├── forms/
│   │   ├── engine.py             # Form rendering engine
│   │   ├── field_helpers.py      # Field utilities
│   │   └── specs/                # Survey specifications
│   │       └── investment_research.py  # Investment research survey
│   ├── common_form_sections/      # Reusable components
│   ├── components/
│   │   ├── sidebar.py           # Navigation
│   │   └── submission.py        # Submission handler
│   ├── pages/
│   │   └── 3_Declaration_and_Submit.py  # Review page
│   ├── email_sender.py          # Email functionality
│   ├── pdf_generator.py         # PDF generation
│   └── utils.py                 # Utilities
├── requirements.txt              # Python dependencies
├── ARCHITECTURE.md              # Technical documentation
├── QUICKSTART.md               # Quick start guide
└── README.md                   # This file
```

## Customization

### Modifying Research Questions

Edit `app/forms/specs/investment_research.py` to:
- Adjust question wording
- Add/remove questions
- Change scale options
- Modify help text

### Adding New Surveys

1. Create new spec in `app/forms/specs/`
2. Register in `app/forms/specs/__init__.py`
3. Restart application

### Email Configuration

Update recipient in `.streamlit/secrets.toml`:
```toml
[email_credentials]
recipient_address = "your-email@example.com"
```

## Privacy & Ethics

- All responses are confidential
- Data used for research purposes only
- No personally identifiable information required
- Participation is voluntary
- Participants can skip optional questions

## Support

For technical issues or questions about the research:
- Email: don.kruger123@gmail.com
- Include error messages and steps to reproduce

## License

This research tool is provided for academic and research purposes.