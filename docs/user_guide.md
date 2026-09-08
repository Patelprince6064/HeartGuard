# HeartGuard Patient User Guide

## What Is HeartGuard?

HeartGuard is an academic research prototype that estimates cardiovascular heart disease risk using an artificial intelligence model. It combines clinical measurements (such as blood pressure, cholesterol, and age) with lifestyle information (such as smoking habits, diet, and exercise) to produce a combined risk score.

**Important Disclaimer:** HeartGuard is NOT a medical diagnostic system. It does not diagnose heart disease, prescribe treatment, or replace the advice of a qualified healthcare professional. All risk scores, recommendations, and explanations produced by HeartGuard are experimental estimates based on statistical models. They should never be used as the sole basis for medical decisions. Always consult a licensed healthcare provider for any health concerns.

---

## How to Register

1. Open the HeartGuard application in your web browser.
2. Click **"Register as a Patient"** on the login page.
3. Fill in the registration form:
   - **Full Name** — Your real name or a display name.
   - **Email** — A valid email address (this becomes your login).
   - **Password** — Must be at least 8 characters.
   - **Confirm Password** — Re-enter the same password.
4. Click **"Create Account"**.
5. You will see a confirmation message. Click **"Go to Login"** to sign in.

All self-registered accounts are automatically assigned the **Patient** role. Admin accounts cannot be created through this form.

---

## How to Log In

1. Enter your **email** and **password** on the login page.
2. Click **"Log In"**.
3. If your credentials are correct, you will be redirected to your Dashboard.

If you enter the wrong password too many times, the system will temporarily lock you out for a short period. This protects your account from unauthorized access attempts.

The system always shows the same error message ("Invalid email or password") whether the email exists or not. This prevents someone from guessing which email addresses are registered.

---

## Dashboard Overview

After logging in, you see your personal Dashboard. This is your home screen and shows:

### Top Metric Cards (KPI Row)
- **Model-Based Risk** — Your latest AI-estimated risk percentage (0-100%).
- **Risk Category** — Your current risk tier (Lower Risk, Elevated, or Critical).
- **Total Assessments** — How many assessments you have completed.
- **Professional Review** — Whether a reviewer has looked at your latest assessment.
- **Alert Status** — Whether an emergency notification was triggered.

### Latest Assessment Summary
Shows your most recent assessment details including overall risk, clinical risk, and lifestyle risk, plus a comparison with your previous assessment if you have more than one.

### Risk Component Breakdown
Displays how your clinical (70% weight) and lifestyle (30% weight) scores combine into your overall risk. A bar chart visualizes these components.

### Risk Trend Chart
A line chart showing how your risk score has changed across multiple assessments. You need at least two assessments to see a trend line.

### Top Model Factors (SHAP)
Shows which clinical features had the most influence on your latest risk score. This uses SHAP (SHapley Additive exPlanations), a method for explaining AI predictions. These are statistical feature contributions, not medical causes.

### Lifestyle Insights
Extracts and displays lifestyle risk factors identified from your self-reported lifestyle narrative.

### Recent Assessments Table
A table of your most recent assessments with a link to view your full history.

### Quick Actions
Shortcuts to start a new assessment, view your history, or access analytics (depending on your role).

### System Health (Collapsible)
Shows whether the ML model, data preprocessor, and multimodal engine are operational.

---

## How to Create a Risk Assessment (Step by Step)

1. Navigate to **"Risk Assessment"** from the sidebar or quick actions.
2. **Section 1 — Clinical Information:** Fill in your clinical measurements:
   - **Age** (years)
   - **Sex** (Female or Male)
   - **Chest Pain Type** (Typical Angina, Atypical Angina, Non-anginal Pain, or Asymptomatic)
   - **Resting Blood Pressure** (mm Hg)
   - **Serum Cholesterol** (mg/dl)
   - **Maximum Heart Rate** achieved during exercise
   - **ST Depression** (Oldpeak) — exercise-induced ST depression relative to rest
   - **Fasting Blood Sugar** — whether above 120 mg/dl
   - **Resting ECG** result (Normal, ST-T Wave Abnormality, or Left Ventricular Hypertrophy)
   - **Exercise-Induced Angina** (Yes or No)
   - **Number of Major Vessels** colored by fluoroscopy (0-4)
3. **Section 2 — Lifestyle Narrative:** Describe your daily habits in your own words. Include information about smoking, diet, exercise, sleep, alcohol, and family cardiac history. For example: *"I smoke about 10 cigarettes a day, eat oily food, work a desk job, sleep 5 hours, drink occasionally, and do not exercise regularly."*
4. **Section 3 — Acknowledgement:** Check the box confirming you understand this is an informational assessment, not medical advice.
5. Click **"Calculate Overall Risk"**.

The system will process your inputs and display your results.

---

## Understanding Your Risk Results

After calculation, you see your results in several sections:

### Overall Risk Score
A percentage from 0-100%. Higher percentages indicate higher estimated cardiovascular risk according to the AI model.

### Risk Category
Your score is placed into one of three categories:
- **Lower Risk (Green)** — Regular monitoring recommended.
- **Elevated Risk (Yellow)** — Appointment with a healthcare professional recommended.
- **Critical Risk (Red)** — Urgent medical attention recommended.

### Clinical Risk (70%)
The risk estimate from the clinical ML model alone, weighted at 70% of the overall score.

### Lifestyle Risk (30%)
The risk estimate from lifestyle analysis alone, weighted at 30% of the overall score.

### Weighted Formula
The system shows the calculation: Clinical Risk × 0.70 + Lifestyle Risk × 0.30 = Overall Risk.

### Clinical Interpretation Narrative
A plain-language explanation of what your results mean in context.

**Disclaimer:** Changes in HeartGuard risk scores represent changes in the model's inputs and outputs. They do not by themselves establish a medical diagnosis or disease progression.

---

## Understanding the Explanation (SHAP)

HeartGuard uses SHAP (SHapley Additive exPlanations) to show you which clinical features most influenced your risk prediction.

### What You See
- **Top Clinical Risk Drivers** — Features that pushed your risk higher, with their SHAP values.
- **SHAP Waterfall Plot** — A visual showing how each feature contributed to your final score.
- **Base Value** — The average model output across all patients.
- **Feature Values** — Your actual input values for each contributing factor.

### Important Notes
- SHAP values show how the AI model weighs each feature. They describe **model behavior**, not medical causation.
- A positive SHAP value means the feature pushed the prediction higher. A negative value means it pushed the prediction lower.
- This is a research tool for understanding model predictions, not a clinical diagnosis tool.

---

## Viewing Your History

Navigate to **"Assessment History"** from the sidebar.

### What You Can Do
- **View all past assessments** in a filterable table (by date range, category, and sort order).
- **Compare your latest assessment with your previous one** — see the delta (change) in risk scores and categories.
- **View longitudinal trend charts** — line charts showing your risk trajectory over time (requires at least 2 assessments).
- **See category distribution** — a bar chart of how many assessments fell into each risk category.
- **Export to CSV** — download your complete assessment history as a CSV file.

Your history is private and only accessible through your authenticated account.

---

## Generating Reports

From the Assessment History page:

1. Select an assessment from the dropdown list.
2. Expand the **"View Assessment Diagnostics & Factors"** section to see detailed information including SHAP factors, AI insights, and professional review status (if any).
3. Click **"Generate Assessment Report"** to create a professional PDF report.
4. Once generated, click **"Download PDF Report"** to save it.

The PDF includes your assessment details, risk scores, and model information.

---

## Lifestyle Analysis

Navigate to **"Lifestyle Risk Analyzer"** from the sidebar.

This tool analyzes your lifestyle narrative independently (without clinical data) and identifies risk factors based on a predefined cardiovascular risk lexicon.

### How to Use It
1. Describe your daily habits in the text area. Include smoking, diet, exercise, sleep, alcohol, and family history.
2. Click **"Analyze Lifestyle"**.
3. Review the results:
   - **Lifestyle Risk Score** (0-100)
   - **Risk Category** (Low, Moderate, High, or Critical)
   - **Detected Risk Factors** — a table showing each factor, its severity, matched terms, and evidence.
   - **Risk Contribution Breakdown** — a bar chart of each factor's contribution.
   - **Clinical Interpretation Narrative** — a plain-language summary.

### Predefined Risk Factors
| Category | Points | Severity | Example Triggers |
|---|---|---|---|
| Smoking | +25 | High | smoke, cigarette, tobacco, nicotine |
| Physical Inactivity | +15 | High | no exercise, sedentary, desk job |
| Unhealthy Diet | +18 | Moderate | oily food, junk, fast food, fried |
| Poor Sleep | +12 | Moderate | sleep < 6 hours, insomnia |
| Family History | +20 | High | family history, heart attack |
| Alcohol Use | +10 | Low | drink alcohol, beer, wine |

The score is capped at 100. This analysis checks for predefined indicators only and does not represent a complete cardiovascular evaluation.

---

## Your Analytics

Navigate to **"My Analytics"** from the sidebar.

This page provides a personal analytics dashboard with:

### KPI Row
- Total Assessments, Latest Risk, Risk Category, and Average Risk across all assessments.

### Risk Trend
A chart showing your model-based risk over time (requires at least 2 assessments).

### Risk Category Distribution
Shows how many of your assessments fall into each risk category.

### Risk Score Statistics
Mean, minimum, maximum, and total count of your risk scores, filterable by time range (All Time, Last 7 Days, Last 30 Days, Last 90 Days).

### Assessment History
A table of your recent assessments with date, risk, category, clinical risk, lifestyle risk, and alert status.

**Disclaimer:** These analytics are model-based statistical summaries. They do not constitute medical diagnosis or disease progression assessment. Changes in risk scores reflect changes in model inputs and outputs, not necessarily changes in health status.

---

## Privacy and Data Rights

HeartGuard takes your privacy seriously:

### Data Minimization
Only clinical and lifestyle metrics strictly required for the ML model are requested. No raw clinical vectors or free-text descriptions are stored in audit logs.

### Field Masking
Personal identifiers (email, phone, name) are pseudonymized or masked in public views.

### Self-Service Data Export
Under GDPR Article 15 (Right of Access), you can export your complete personal data:
1. Navigate to the **"Security & Privacy Center"** page.
2. Click **"Generate My Data Export"**.
3. Download the JSON file containing your assessment history, recommendations, and account profile.
4. Sensitive authentication tokens are excluded from the export.

### Access Control
Your data is only accessible through your authenticated account. The system enforces strict role-based access control — other patients cannot see your data, and only authorized reviewers can view assessment records in the review portal.

### No Training on Your Data
Your input parameters are evaluated dynamically; your data is never stored into training sets.

---

## Frequently Asked Questions

**Q: Is HeartGuard a medical device?**
A: No. HeartGuard is an academic research prototype. It is not certified as a medical device and should not be used for clinical diagnosis or treatment decisions.

**Q: Should I trust the risk score?**
A: The risk score is a statistical estimate based on the Cleveland Heart Disease dataset and lifestyle NLP analysis. It is experimental. Always consult a qualified healthcare professional for medical advice.

**Q: What do the SHAP values mean?**
A: SHAP values explain how the AI model weighed each feature when making its prediction. They describe model behavior, not medical causation. A feature with a high SHAP value contributed more to the model's prediction for your specific case.

**Q: Can I delete my account?**
A: Contact the system administrator. Under GDPR Article 17 (Right to Erasure), you have the right to request deletion of your personal data.

**Q: Why do I need to enter clinical data?**
A: HeartGuard combines clinical measurements (70%) with lifestyle information (30%) to produce a multimodal risk estimate. The clinical data provides the primary risk signal, while lifestyle adds context.

**Q: What if I see a Critical risk result?**
A: If your result shows CRITICAL risk, an emergency notification may be triggered. Regardless of the result, you should always seek professional medical evaluation. A Critical result does not mean you are having a heart attack — it means the model's statistical estimate is high.

**Q: Can I see what a reviewer thought of my assessment?**
A: Yes. Your dashboard and history page show the professional review status of your assessments. If a reviewer has added notes, you can see their review status (though detailed reviewer notes are primarily visible to the reviewer portal).

**Q: Is my lifestyle text stored?**
A: No. Your lifestyle narrative is processed by the NLP engine but is never logged or stored in audit logs. Only the extracted risk factors and scores are persisted.

**Q: How often should I take an assessment?**
A: There is no fixed schedule. You may take assessments when you want to track changes in your risk profile. Completing multiple assessments over time allows you to see trends and compare results.
