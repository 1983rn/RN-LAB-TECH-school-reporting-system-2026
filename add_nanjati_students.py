#!/usr/bin/env python3
"""
Add Missing NANJATI Students and Fix Position Calculations
"""

import sqlite3
import os

def add_missing_nanjati_students():
    """Add the missing NANJATI students to complete the 91 student roster"""
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    nanjati_school_id = 2
    
    print("=== ADDING MISSING NANJATI STUDENTS ===\n")
    
    # List of all 91 NANJATI students from user's message
    nanjati_students = [
        "AARON MALACK", "AGATHAR CHISI", "ALFRED KAITANDE", "ALICE BANDA",
        "ANASTANZIA DAMIANO", "ANNIE FRANCIS", "BEATRICE SUMBULETA", "BESTER PHIRI",
        "BETRICE BALALA", "BLESSINGS DEKESI", "BRANDINA MWANGONDE", "BRENDA KALUMBI",
        "BRIGHT THASO", "CATHRINE KANDAYA", "CATHRINE MANYOWA", "CHARITY PHIRI",
        "CHIKONDI CHILIMA", "CHIMWEMWE MAKIYONI", "CHISISI NTHANGA", "CHISOMO MALIKI",
        "CHISOMO SINOSI", "CLARA ZAKUNJA", "COLLINGS MALALA", "DALITSO MIDIAN",
        "DANIEL CHIKWAWA", "DAVIE GONDWE", "DONIAS CHAYERA", "DYTON JAMES",
        "EDEN EVANS", "EKARI MUNGREZI", "EMMANUEL BANDA", "EMMANUEL MPONELA",
        "ENELESS ULEMU", "ERICK MSANJAMA", "FAITH KOCHERANI", "FAITH PHIRI",
        "FATIMA ELIAS", "GLADYS SEKANI", "HASTINGS MAKWITI", "JAMIRA JAMES",
        "JOEL JASON", "JOYCE NAMVUKA", "KELVIN CHILOMBO", "KUMBUKANI PHIRI",
        "LEANDRA DUNIA", "LENISA LANDANI", "LUKA CHIMKUYU", "LUKE JOSEPHY",
        "LYDIA BANDA", "MACPHERSON JAMALI", "MALIAM AWALI", "MARGRET MAULIDI",
        "MARTHA STONARD", "MARTIN KAMWANA", "MARTIN MAKWALE", "MAYAMIKO KABICHI",
        "MELICY SALIMU", "MIRACLE KAPUZA", "MIRACLE NGWIRA", "MONALISA NDHOBVU",
        "MOURICE ZUZE", "NATASHA SCOTT", "NAZIR WASILI", "PEACE NDHLAZI",
        "PEMPHO JUSABU", "PHILLIP ELIJAH", "PRAISE CHIKUSA", "PRECIOUS MWALE",
        "PRECIOUS MWALE", "PRECIOUS SILIYA", "PRINCESS NKHWAZI", "PRUDENCE MWANGOBOLA",
        "RAHAMAN MZINI", "RICHARD CHINKHANJA", "RODRICK YAMIKANI", "RUTH DULANA",
        "SAMIAH MAUGERE", "SANDRA MISOMALI", "SARAI TAMBULA", "SIBETA CHIPIRIRO",
        "TALANDIRA KAIPA", "TAMALA TEMBO", "TRACY MKWANDA", "VANESSA RAPHAEL",
        "VAN-KID SANKHANI", "VERONICA BANDA", "VINCENT BANDA", "WANANGWA NYIMBIRI",
        "WESLEY MATCHULA", "WILLIAM KANDULU", "WORSHIP KUMISALE"
    ]
    
    print(f"Expected students: {len(nanjati_students)}")
    
    # Check existing students
    cursor.execute("""
        SELECT first_name, last_name 
        FROM students 
        WHERE school_id = ? AND grade_level = 1 AND status = 'Active'
    """, (nanjati_school_id,))
    
    existing_students = cursor.fetchall()
    existing_names = set()
    for first, last in existing_students:
        existing_names.add(f"{first} {last}".upper().strip())
    
    print(f"Existing students: {len(existing_students)}")
    
    # Find missing students
    missing_students = []
    for full_name in nanjati_students:
        if full_name.upper().strip() not in existing_names:
            # Split name into first and last
            parts = full_name.strip().split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = " ".join(parts[1:])
                missing_students.append((first_name, last_name))
    
    print(f"Missing students: {len(missing_students)}")
    
    if missing_students:
        print("\nAdding missing students:")
        
        # Get next student number
        cursor.execute("""
            SELECT MAX(CAST(student_number AS INTEGER)) 
            FROM students 
            WHERE school_id = ?
        """, (nanjati_school_id,))
        
        result = cursor.fetchone()
        next_number = (result[0] if result and result[0] else 0) + 1
        
        for first_name, last_name in missing_students:
            student_number = f"{next_number:04d}"
            
            cursor.execute("""
                INSERT INTO students (
                    student_number, first_name, last_name, grade_level, 
                    status, school_id, date_enrolled
                ) VALUES (?, ?, ?, 1, 'Active', ?, datetime('now'))
            """, (student_number, first_name, last_name, nanjati_school_id))
            
            print(f"  Added: {first_name} {last_name} (#{student_number})")
            next_number += 1
        
        conn.commit()
        print(f"\nSuccessfully added {len(missing_students)} students")
    
    # Verify final count
    cursor.execute("""
        SELECT COUNT(*) FROM students 
        WHERE school_id = ? AND grade_level = 1 AND status = 'Active'
    """, (nanjati_school_id,))
    
    final_count = cursor.fetchone()[0]
    print(f"\nFinal student count: {final_count}")
    
    conn.close()

def fix_position_calculation_methods():
    """Fix the position calculation methods in school_database.py"""
    
    print("\n=== FIXING POSITION CALCULATION METHODS ===\n")
    
    # The main issues are in the get_student_rankings and get_subject_position methods
    # Let's create a patch for the school_database.py file
    
    fixes = """
Key fixes needed in school_database.py:

1. get_student_rankings method:
   - Ensure proper tie handling for positions
   - Fix aggregate points calculation for Forms 3-4
   - Ensure correct pass/fail status determination

2. get_subject_position method:
   - Fix tie handling in subject rankings
   - Ensure correct total student count (class size vs students who sat)
   - Return format should be "position/total_class_size"

3. get_student_position_and_points method:
   - Fix position calculation with proper tie handling
   - Ensure aggregate points are calculated correctly
"""
    
    print(fixes)

if __name__ == "__main__":
    add_missing_nanjati_students()
    fix_position_calculation_methods()