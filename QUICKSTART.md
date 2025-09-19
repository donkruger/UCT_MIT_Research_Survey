# Quick Start Guide - Investment Research Survey

## 🚀 Get Started in 3 Minutes

### 1. Install & Run
```bash
# Install dependencies
pip install streamlit reportlab

# Run the application
streamlit run app/main.py
```

The survey opens at `http://localhost:8501`

### 2. Complete the Survey
1. The **Investment Decision-Making Research Survey** loads automatically
2. Answer the 8 research dimensions (Likert scales + text)
3. Click **"Review & Submit"** in the sidebar
4. Confirm and submit

### 3. Data Collection
- Responses are emailed to: **don.kruger123@gmail.com**
- PDF and CSV files are generated automatically
- Download copies for your records

---

## 📊 Research Questions Overview

The survey evaluates 8 key dimensions:

1. **Prescriptive Knowledge** - Structured recommendations
2. **Human vs. Non-Human Actors** - System explanations
3. **Complexity and Decomposition** - Component transparency
4. **Types of Causality** - Deterministic vs. probabilistic
5. **Mechanisms for Goal Achievement** - Verification capabilities
6. **Justificatory Knowledge** - Metric explanations
7. **Boundary Conditions** - Appropriate contexts
8. **Trust** - Confidence in insights

Each dimension includes:
- 📈 **Likert Scale (1-5)** with specific anchors
- 💭 **Open Text** for detailed feedback

---

## 🔧 Quick Configuration

### Email Setup (Optional)

Create `.streamlit/secrets.toml`:
```toml
[email_credentials]
email_address = "your-email@gmail.com"
app_password = "xxxx-xxxx-xxxx-xxxx"  # Gmail app password
recipient_address = "don.kruger123@gmail.com"
```

**Gmail App Password:**
1. Enable 2FA: https://myaccount.google.com/security
2. Generate password: https://myaccount.google.com/apppasswords

### Development Mode

For quick testing without validation:
1. Click **"🔧 Development Options"** on main page
2. Toggle **"Dev Mode"**
3. Submit with minimal data

---

## 📋 Research Methodology

### Likert Scale Interpretation
- **1** = Strongly Disagree / Completely Negative
- **2** = Disagree / Somewhat Negative
- **3** = Neutral
- **4** = Agree / Somewhat Positive
- **5** = Strongly Agree / Completely Positive

### Response Guidelines
- Be specific in text responses
- Provide examples where possible
- All text fields are optional
- Skip questions if not applicable

---

## 📊 Data Export

### PDF Format
- Professional summary report
- All responses included
- Timestamp and metadata
- Print-ready format

### CSV Format
```csv
Section,Record #,Field,Value
Prescriptive Knowledge,1,prescriptive_structured,4 - Agree
Prescriptive Knowledge,1,prescriptive_missing,Need more risk indicators
```

---

## 🆘 Troubleshooting

### Survey Not Loading?
```bash
# Check Python version (needs 3.8+)
python --version

# Reinstall dependencies
pip install --upgrade streamlit reportlab
```

### Email Not Sending?
1. Check `.streamlit/secrets.toml` exists
2. Verify app password (not regular password)
3. Check spam folder for responses

### Validation Errors?
- Enable Dev Mode for testing
- Check required fields (Likert scales)
- Text fields are optional

---

## 📚 Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Research Questions**: [RESEARCH_QUESTIONS.md](RESEARCH_QUESTIONS.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Support**: don.kruger123@gmail.com

---

## ⚡ One-Line Setup

```bash
pip install streamlit reportlab && streamlit run app/main.py
```

Survey runs immediately - no configuration required for basic use!