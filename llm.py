import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None
    print("Warning: GEMINI_API_KEY not found in environment variables.")

def _fallback_explanation(student_data: dict) -> str:
    """
    Rule-based plain-English explanation used when Gemini is unavailable
    (e.g. API errors, quota issues, network problems). Keeps the app usable
    for demos even if the live AI call fails.
    """
    name = student_data.get("student_name", "This student")
    reasons = []

    attendance = student_data.get("attendance_percent")
    if attendance is not None and attendance < 75:
        reasons.append(f"attendance has dropped to {attendance}%")

    prev_gpa = student_data.get("previous_gpa")
    curr_gpa = student_data.get("current_gpa")
    if prev_gpa is not None and curr_gpa is not None and (prev_gpa - curr_gpa) >= 1.0:
        reasons.append(f"GPA has fallen from {prev_gpa} to {curr_gpa}")

    total = student_data.get("assignments_total")
    submitted = student_data.get("assignments_submitted")
    if total and submitted is not None and (submitted / total) < 0.60:
        reasons.append(f"only {submitted} of {total} assignments have been submitted")

    marks = [
        student_data.get("subject1_marks"),
        student_data.get("subject2_marks"),
        student_data.get("subject3_marks"),
    ]
    marks = [m for m in marks if m is not None]
    if marks and (sum(marks) / len(marks)) < 50:
        reasons.append("average subject marks are below 50")

    if not reasons:
        return f"{name} has been flagged for review; metrics are borderline across multiple factors."

    reason_text = "; ".join(reasons)
    return f"{name} is flagged at risk primarily because {reason_text}. Recommend early advisor check-in."


def generate_risk_explanation(student_data: dict) -> str:
    """
    Generates a 1-2 sentence explanation of why a student is flagged as at-risk
    using Gemini. Falls back to a rule-based explanation if the Gemini call
    fails for any reason (invalid key, quota, network, API outage, etc.)
    so the app stays usable during demos.
    """
    if client is None:
        return _fallback_explanation(student_data)

    prompt = f"""
You are an AI assistant for an academic advisor.
A student named {student_data.get('student_name', 'Unknown')} has been flagged as '{student_data.get('risk_level', 'Unknown')}'.
Here are their current metrics:
- Attendance: {student_data.get('attendance_percent')}%
- Previous GPA: {student_data.get('previous_gpa')}
- Current GPA: {student_data.get('current_gpa')}
- Assignments Submitted: {student_data.get('assignments_submitted')} out of {student_data.get('assignments_total')}
- Subject Marks: {student_data.get('subject1_marks')}, {student_data.get('subject2_marks')}, {student_data.get('subject3_marks')}

Based on this data, write a 1-2 sentence, professional, plain-English explanation of why this student is at risk and what the primary areas of concern are. This will be used by an academic advisor for quick intervention.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=150,
                temperature=0.3,
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error, using fallback explanation: {e}")
        return _fallback_explanation(student_data)

def main():
    try:
        df = pd.read_csv('students_with_risk.csv')
    except FileNotFoundError:
        print("Error: students_with_risk.csv not found. Please run logic.py first.")
        return
        
    high_risk_students = df[df['risk_level'] == 'High Risk']
    
    if high_risk_students.empty:
        print("No High Risk students found.")
        return
        
    target_student = high_risk_students.iloc[0].to_dict()
    
    print(f"Generating explanation for: {target_student['student_name']}...")
    explanation = generate_risk_explanation(target_student)
    
    print("\n--- AI-Generated Risk Explanation ---")
    print(explanation)
    print("---------------------------------------")

if __name__ == "__main__":
    main()
