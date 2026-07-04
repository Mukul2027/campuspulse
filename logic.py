import pandas as pd
import numpy as np

def calculate_risk(row):
    flags = 0
    if pd.notna(row['attendance_percent']) and row['attendance_percent'] < 75:
        flags += 1
    
    if pd.notna(row['previous_gpa']) and pd.notna(row['current_gpa']):
        if (row['previous_gpa'] - row['current_gpa']) >= 1.0:
            flags += 1
        
    if pd.notna(row['assignments_total']) and row['assignments_total'] > 0:
        if pd.notna(row['assignments_submitted']):
            if (row['assignments_submitted'] / row['assignments_total']) < 0.60:
                flags += 1
    elif pd.notna(row['assignments_total']) and row['assignments_total'] == 0:
         pass
    else:
        pass
    
    marks = []
    for col in ['subject1_marks', 'subject2_marks', 'subject3_marks']:
        if pd.notna(row[col]):
            marks.append(row[col])
            
    if len(marks) > 0:
        avg_marks = sum(marks) / len(marks)
        if avg_marks < 50:
            flags += 1
    else:
        flags += 1
        
    if flags >= 2:
        return "High Risk"
    elif flags == 1:
        return "Moderate Risk"
    else:
        return "On Track"

def clean_data(df):
   
    numeric_cols = [
        'attendance_percent', 'previous_gpa', 'current_gpa', 
        'assignments_total', 'assignments_submitted', 
        'subject1_marks', 'subject2_marks', 'subject3_marks'
    ]
    
    for col in numeric_cols:
        if col not in df.columns:
            print(f"Warning: Missing expected column '{col}'. Adding it with missing values.")
            df[col] = np.nan
            
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    if 'student_name' not in df.columns:
        df['student_name'] = "Unknown Student"
    else:
        df['student_name'] = df['student_name'].fillna("Unknown Student").astype(str)
        
    if 'student_id' not in df.columns:
        df['student_id'] = "Unknown ID"
    else:
        df['student_id'] = df['student_id'].fillna("Unknown ID").astype(str)
        
    return df

def main():
    try:
        df = pd.read_csv('sample_students.csv')
    except FileNotFoundError:
        print("Error: sample_students.csv not found.")
        return

    df = clean_data(df)

    df['risk_level'] = df.apply(calculate_risk, axis=1)

    df.to_csv('students_with_risk.csv', index=False)
    
    print("--- Risk Level Summary ---")
    print(df['risk_level'].value_counts().to_string())
    print("\nProcessing complete. Enhanced data saved to 'students_with_risk.csv'.")

if __name__ == "__main__":
    main()
