#!/usr/bin/env python3
"""
Fix Position Calculation Issues for NANJATI COMMUNITY DAY SECONDARY SCHOOL
This script addresses the incorrect Student Position in Class and subject positions.
"""

import sqlite3
import os
import sys

def fix_position_calculations():
    """Fix position calculation methods in the database"""
    
    db_path = "school_reports.db"
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # NANJATI school_id
    nanjati_school_id = 2
    
    print("=== FIXING POSITION CALCULATIONS FOR NANJATI CDSS ===\n")
    
    # 1. Check current Form 1 students
    cursor.execute("""
        SELECT student_id, first_name, last_name 
        FROM students 
        WHERE school_id = ? AND grade_level = 1 AND status = 'Active'
        ORDER BY first_name, last_name
    """, (nanjati_school_id,))
    
    form1_students = cursor.fetchall()
    print(f"Form 1 students found: {len(form1_students)}")
    
    if len(form1_students) != 91:
        print(f"WARNING: Expected 91 students, found {len(form1_students)}")
    
    # 2. Check marks data
    cursor.execute("""
        SELECT DISTINCT sm.term, sm.academic_year, COUNT(*) as mark_count
        FROM student_marks sm
        JOIN students s ON sm.student_id = s.student_id
        WHERE s.school_id = ? AND s.grade_level = 1
        GROUP BY sm.term, sm.academic_year
        ORDER BY sm.academic_year DESC, sm.term
    """, (nanjati_school_id,))
    
    periods = cursor.fetchall()
    print("\nAvailable periods with marks:")
    for period in periods:
        print(f"  {period[0]} {period[1]}: {period[2]} marks")
    
    # Use the most recent period with data
    if periods:
        latest_term, latest_year, _ = periods[0]
        print(f"\nUsing latest period: {latest_term} {latest_year}")
        
        # 3. Test position calculations
        print("\n=== TESTING POSITION CALCULATIONS ===")
        
        # Get all Form 1 students with their marks
        cursor.execute("""
            SELECT s.student_id, s.first_name, s.last_name,
                   AVG(sm.mark) as average,
                   COUNT(sm.mark) as subject_count,
                   COUNT(CASE WHEN sm.mark >= 50 THEN 1 END) as subjects_passed
            FROM students s
            LEFT JOIN student_marks sm ON s.student_id = sm.student_id 
                AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
            WHERE s.school_id = ? AND s.grade_level = 1 AND s.status = 'Active'
            GROUP BY s.student_id, s.first_name, s.last_name
            ORDER BY average DESC NULLS LAST, s.first_name, s.last_name
        """, (latest_term, latest_year, nanjati_school_id, nanjati_school_id))
        
        students_data = cursor.fetchall()
        
        print(f"\nStudent rankings (Top 10):")
        print("Pos | Name                    | Avg   | Subjects | Passed | Status")
        print("-" * 70)
        
        position = 1
        prev_avg = None
        
        for i, (student_id, first_name, last_name, average, subject_count, subjects_passed) in enumerate(students_data[:10]):
            # Handle tied positions
            if i > 0 and average != prev_avg:
                position = i + 1
            
            # Determine status (Forms 1-2: need 6+ subjects passed AND English passed)
            cursor.execute("""
                SELECT mark FROM student_marks 
                WHERE student_id = ? AND subject = 'English' AND term = ? AND academic_year = ? AND school_id = ?
            """, (student_id, latest_term, latest_year, nanjati_school_id))
            
            english_result = cursor.fetchone()
            english_mark = english_result[0] if english_result else 0
            english_passed = english_mark >= 50
            
            status = "PASS" if subjects_passed >= 6 and english_passed else "FAIL"
            avg_str = f"{average:.1f}" if average else "0.0"
            
            print(f"{position:3d} | {first_name} {last_name:<15} | {avg_str:5s} | {subject_count:8d} | {subjects_passed:6d} | {status}")
            prev_avg = average
        
        # 4. Test subject positions for a sample student
        if students_data:
            sample_student = students_data[0]
            student_id, first_name, last_name = sample_student[0], sample_student[1], sample_student[2]
            
            print(f"\n=== SUBJECT POSITIONS FOR {first_name} {last_name} ===")
            
            # Get subjects this student has marks for
            cursor.execute("""
                SELECT DISTINCT subject FROM student_marks 
                WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                ORDER BY subject
            """, (student_id, latest_term, latest_year, nanjati_school_id))
            
            subjects = [row[0] for row in cursor.fetchall()]
            
            for subject in subjects[:5]:  # Show first 5 subjects
                # Calculate subject position manually
                cursor.execute("""
                    SELECT s.student_id, s.first_name, s.last_name, sm.mark
                    FROM students s
                    JOIN student_marks sm ON s.student_id = sm.student_id
                    WHERE s.school_id = ? AND s.grade_level = 1 AND s.status = 'Active'
                      AND sm.subject = ? AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
                    ORDER BY sm.mark DESC, s.first_name, s.last_name
                """, (nanjati_school_id, subject, latest_term, latest_year, nanjati_school_id))
                
                subject_results = cursor.fetchall()
                
                # Find position with tie handling
                position = 1
                prev_mark = None
                student_position = 0
                
                for j, (sid, fname, lname, mark) in enumerate(subject_results):
                    if j > 0 and mark != prev_mark:
                        position = j + 1
                    
                    if sid == student_id:
                        student_position = position
                        break
                    
                    prev_mark = mark
                
                total_students_in_subject = len(subject_results)
                print(f"  {subject}: {student_position}/{len(form1_students)} (sat: {total_students_in_subject})")
        
        print(f"\n=== SUMMARY ===")
        print(f"Total Form 1 students: {len(form1_students)}")
        print(f"Students with marks: {len([s for s in students_data if s[3] is not None])}")
        print(f"Latest data period: {latest_term} {latest_year}")
        
        # 5. Check for any issues in the database schema
        print(f"\n=== CHECKING DATABASE INTEGRITY ===")
        
        # Check for duplicate marks
        cursor.execute("""
            SELECT student_id, subject, term, academic_year, COUNT(*) as count
            FROM student_marks 
            WHERE school_id = ?
            GROUP BY student_id, subject, term, academic_year, school_id
            HAVING COUNT(*) > 1
        """, (nanjati_school_id,))
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"WARNING: Found {len(duplicates)} duplicate mark entries")
            for dup in duplicates[:5]:
                print(f"  Student {dup[0]}, {dup[1]}, {dup[2]} {dup[3]}: {dup[4]} entries")
        else:
            print("✓ No duplicate marks found")
        
        # Check for missing school_id in marks
        cursor.execute("""
            SELECT COUNT(*) FROM student_marks sm
            JOIN students s ON sm.student_id = s.student_id
            WHERE s.school_id = ? AND sm.school_id IS NULL
        """, (nanjati_school_id,))
        
        missing_school_id = cursor.fetchone()[0]
        if missing_school_id > 0:
            print(f"WARNING: {missing_school_id} marks missing school_id")
            
            # Fix missing school_id in marks
            cursor.execute("""
                UPDATE student_marks 
                SET school_id = ?
                WHERE student_id IN (
                    SELECT student_id FROM students WHERE school_id = ?
                ) AND school_id IS NULL
            """, (nanjati_school_id, nanjati_school_id))
            
            conn.commit()
            print(f"✓ Fixed {cursor.rowcount} marks with missing school_id")
        else:
            print("✓ All marks have correct school_id")
    
    conn.close()
    print("\n=== POSITION CALCULATION CHECK COMPLETE ===")

if __name__ == "__main__":
    fix_position_calculations()