#!/usr/bin/env python3

import sqlite3
import os

def cleanup_nanjati_form1_students():
    """Keep only specified Form 1 students for NANJATI CDSS, delete the rest"""
    
    # List of students to keep (exactly as provided)
    students_to_keep = [
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
        "PRECIOUS SILIYA", "PRINCESS NKHWAZI", "PRUDENCE MWANGOBOLA", "RAHAMAN MZINI",
        "RICHARD CHINKHANJA", "RODRICK YAMIKANI", "RUTH DULANA", "SAMIAH MAUGERE",
        "SANDRA MISOMALI", "SARAI TAMBULA", "SIBETA CHIPIRIRO", "TALANDIRA KAIPA",
        "TAMALA TEMBO", "TRACY MKWANDA", "VANESSA RAPHAEL", "VAN-KID SANKHANI",
        "VERONICA BANDA", "VINCENT BANDA", "WANANGWA NYIMBIRI", "WESLEY MATCHULA",
        "WILLIAM KANDULU", "WORSHIP KUMISALE"
    ]
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get NANJATI school ID
    cursor.execute("SELECT school_id FROM schools WHERE school_name LIKE '%NANJATI%'")
    school = cursor.fetchone()
    if not school:
        print("NANJATI school not found")
        return
    
    school_id = school[0]
    print(f"NANJATI school ID: {school_id}")
    
    # Get all Form 1 students for NANJATI
    cursor.execute("""
        SELECT student_id, first_name, last_name
        FROM students 
        WHERE school_id = ? AND grade_level = 1
    """, (school_id,))
    
    all_students = cursor.fetchall()
    print(f"Total Form 1 students before cleanup: {len(all_students)}")
    
    # Find students to delete
    students_to_delete = []
    students_kept = []
    
    for student_id, first_name, last_name in all_students:
        full_name = f"{first_name} {last_name}".upper().strip()
        
        if full_name in students_to_keep:
            students_kept.append((student_id, full_name))
        else:
            students_to_delete.append((student_id, full_name))
    
    print(f"Students to keep: {len(students_kept)}")
    print(f"Students to delete: {len(students_to_delete)}")
    
    if students_to_delete:
        print("\nStudents being deleted:")
        for student_id, name in students_to_delete:
            print(f"  {name} (ID: {student_id})")
        
        # Delete marks first (foreign key constraint)
        student_ids_to_delete = [str(s[0]) for s in students_to_delete]
        placeholders = ','.join(['?' for _ in student_ids_to_delete])
        
        cursor.execute(f"DELETE FROM student_marks WHERE student_id IN ({placeholders})", student_ids_to_delete)
        marks_deleted = cursor.rowcount
        print(f"\nDeleted {marks_deleted} mark records")
        
        # Delete students
        cursor.execute(f"DELETE FROM students WHERE student_id IN ({placeholders})", student_ids_to_delete)
        students_deleted = cursor.rowcount
        print(f"Deleted {students_deleted} student records")
        
        conn.commit()
        print("\nCleanup completed successfully!")
    else:
        print("No students to delete")
    
    # Verify final count
    cursor.execute("SELECT COUNT(*) FROM students WHERE school_id = ? AND grade_level = 1", (school_id,))
    final_count = cursor.fetchone()[0]
    print(f"Final Form 1 student count: {final_count}")
    
    conn.close()

if __name__ == "__main__":
    cleanup_nanjati_form1_students()