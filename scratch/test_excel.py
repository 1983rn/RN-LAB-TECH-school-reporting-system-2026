
import pandas as pd
import os

try:
    # Create a dummy excel file
    df = pd.DataFrame({'First Name': ['Test'], 'Last Name': ['Student']})
    df.to_excel('test_excel.xlsx', index=False)
    print("Successfully created test excel file using openpyxl")
    
    # Try reading it back
    df2 = pd.read_excel('test_excel.xlsx')
    print("Successfully read test excel file")
    print(df2)
    
    # Cleanup
    os.remove('test_excel.xlsx')
except Exception as e:
    print(f"Error testing excel functionality: {e}")
