# CampusPulse

AI-powered academic early-warning tool. Upload student attendance, GPA, and assignment data — CampusPulse flags at-risk students and uses Gemini to generate a plain-English explanation for advisors.

Built for **Gen AI Academy — APAC Edition** (Google Cloud x H2S), Team **Tech-ni-kaal**.

## Team
- Mukul (Team Leader)
- Abhilasha Nautiyal
- Abhishek Nayyar

## How it works
1. Upload a CSV of student records (see format below)
2. `logic.py` cleans the data and scores each student's risk (High / Moderate / On Track) based on attendance, GPA trend, assignment submission rate, and subject marks
3. `llm.py` sends flagged students to Gemini, which generates a short, advisor-ready explanation
4. `app.py` (Streamlit) displays the dashboard, charts, and explanations

## Expected CSV columns
```
student_id, student_name, attendance_percent, previous_gpa, current_gpa,
assignments_total, assignments_submitted, subject1_marks, subject2_marks, subject3_marks
```

## Run locally
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
streamlit run app.py
```

## Deployment
Deployed on Streamlit Community Cloud. Set `GEMINI_API_KEY` under app Secrets.
