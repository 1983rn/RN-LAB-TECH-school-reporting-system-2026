import pandas as pd
import os

# Define the subjects
subjects = ['Agriculture', 'Bible Knowledge', 'Biology', 'Business Studies', 'Chemistry', 'Chichewa', 'Clothing & Textiles', 'Computer Studies', 'English', 'Geography', 'History', 'Home Economics', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Technical Drawing']

def test_excel_parsing(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(col).strip() for col in df.columns]
    
    # Required columns
    required_columns = ['First Name', 'Last Name']
    found_columns = {}
    for req in required_columns:
        req_normalized = req.lower().replace(' ', '')
        for col in df.columns:
            col_normalized = str(col).lower().replace(' ', '').replace('_', '')
            if col_normalized == req_normalized:
                found_columns[req] = col
                break
    
    if len(found_columns) < len(required_columns):
        print(f"Missing required columns: {required_columns}")
        return

    # Find subject columns
    subject_columns = {}
    for subject in subjects:
        subj_normalized = subject.lower().replace(' ', '').replace('/', '').replace('&', '')
        for col in df.columns:
            col_normalized = str(col).lower().replace(' ', '').replace('/', '').replace('&', '').replace('_', '')
            if col_normalized == subj_normalized:
                subject_columns[subject] = col
                break
    
    print(f"Found subject columns: {list(subject_columns.keys())}")

    for index, row in df.iterrows():
        first_name = row[found_columns['First Name']]
        last_name = row[found_columns['Last Name']]
        print(f"Student: {first_name} {last_name}")
        for subject, col_name in subject_columns.items():
            mark = row[col_name]
            if pd.notnull(mark):
                try:
                    mark_val = int(mark)
                    print(f"  {subject}: {mark_val}")
                except (ValueError, TypeError):
                    print(f"  {subject}: Invalid mark '{mark}'")

# Create a sample excel file
data = {
    'First Name': ['John', 'Jane', 'Peter'],
    'Last Name': ['Doe', 'Smith', 'Parker'],
    'English': [85, 90, 75],
    'Mathematics': [70, 80, 95],
    'Biology': [60, None, 80]
}
df_sample = pd.DataFrame(data)
sample_path = 'scratch/sample_marks.xlsx'
os.makedirs('scratch', exist_ok=True)
df_sample.to_excel(sample_path, index=False)

print("Testing with sample_marks.xlsx")
test_excel_parsing(sample_path)
