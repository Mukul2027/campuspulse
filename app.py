import streamlit as st
import pandas as pd
from logic import clean_data, calculate_risk
from llm import generate_risk_explanation

st.set_page_config(page_title="CampusPulse", layout="wide")

st.title("CampusPulse")
st.caption("AI-Powered Academic Early-Warning Tool — Upload student data to flag at-risk students")
st.divider()

uploaded_file = st.file_uploader(
    "Upload Student Data (CSV)",
    type=["csv"],
    help="Expected columns: student_id, student_name, attendance_percent, previous_gpa, current_gpa, "
         "assignments_total, assignments_submitted, subject1_marks, subject2_marks, subject3_marks",
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    df = clean_data(df)
    df["risk_level"] = df.apply(calculate_risk, axis=1)

    # ---- Overview ----
    st.subheader("Overview")
    total = len(df)
    high = int((df["risk_level"] == "High Risk").sum())
    moderate = int((df["risk_level"] == "Moderate Risk").sum())
    on_track = int((df["risk_level"] == "On Track").sum())
    avg_attendance = round(df["attendance_percent"].mean(), 1) if df["attendance_percent"].notna().any() else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", total)
    col2.metric("High Risk", high)
    col3.metric("Moderate Risk", moderate)
    col4.metric("Avg Attendance", f"{avg_attendance}%")

    st.divider()

    # ---- Risk Table ----
    st.subheader("Student Risk Summary")

    def color_risk(val):
        if val == "High Risk":
            return "color: red; font-weight: bold"
        elif val == "Moderate Risk":
            return "color: orange; font-weight: bold"
        else:
            return "color: green; font-weight: bold"

    display_cols = [
        "student_id", "student_name", "attendance_percent", "previous_gpa", "current_gpa",
        "assignments_submitted", "assignments_total", "risk_level",
    ]
    display_df = df[display_cols]
    styled = display_df.style.map(color_risk, subset=["risk_level"])
    st.dataframe(styled, use_container_width=True)

    st.divider()

    # ---- Charts ----
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Attendance by Student")
        st.bar_chart(df.set_index("student_name")["attendance_percent"])
    with chart_col2:
        st.subheader("GPA Trend (Current vs Previous)")
        st.bar_chart(df.set_index("student_name")[["previous_gpa", "current_gpa"]])

    st.divider()

    # ---- High Risk Students + AI Explanations ----
    st.subheader("High Risk Students — AI-Generated Explanations")
    high_risk_df = df[df["risk_level"] == "High Risk"]

    if high_risk_df.empty:
        st.success("No high risk students found.")
    else:
        st.warning(f"{len(high_risk_df)} student(s) flagged as High Risk")

        if st.button("Generate AI Explanations for High Risk Students"):
            with st.spinner("Asking Gemini for advisor-ready explanations..."):
                for _, row in high_risk_df.iterrows():
                    explanation = generate_risk_explanation(row.to_dict())
                    with st.expander(f"{row['student_name']} ({row['student_id']})"):
                        st.write(f"**Attendance:** {row['attendance_percent']}%")
                        st.write(f"**GPA:** {row['previous_gpa']} → {row['current_gpa']}")
                        st.write(
                            f"**Assignments:** {row['assignments_submitted']}/{row['assignments_total']}"
                        )
                        st.info(explanation)
        else:
            st.dataframe(
                high_risk_df[["student_id", "student_name", "attendance_percent", "current_gpa"]],
                use_container_width=True,
            )
            st.caption("Click the button above to generate plain-English explanations via Gemini.")

else:
    st.info(
        "Please upload a CSV with columns: student_id, student_name, attendance_percent, previous_gpa, "
        "current_gpa, assignments_total, assignments_submitted, subject1_marks, subject2_marks, subject3_marks"
    )

    st.subheader("Expected Format")
    sample = pd.DataFrame(
        {
            "student_id": ["S001", "S002", "S003"],
            "student_name": ["Riya Sharma", "Aman Verma", "Rohit Gupta"],
            "attendance_percent": [92, 45, 30],
            "previous_gpa": [3.6, 3.0, 2.8],
            "current_gpa": [3.7, 1.9, 2.0],
            "assignments_total": [20, 20, 20],
            "assignments_submitted": [19, 10, 6],
            "subject1_marks": [85, 40, 35],
            "subject2_marks": [88, 38, 32],
            "subject3_marks": [90, 42, 30],
        }
    )
    st.dataframe(sample, use_container_width=True)
