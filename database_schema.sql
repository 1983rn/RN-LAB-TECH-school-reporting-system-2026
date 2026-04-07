-- School Reporting System Database Schema
-- Created: 2025-08-06

-- Students table
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE,
    grade_level INTEGER NOT NULL,
    enrollment_date DATE DEFAULT (date('now')),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    parent_guardian_name VARCHAR(100),
    parent_guardian_phone VARCHAR(20),
    parent_guardian_email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Graduated', 'Transferred'))
);

-- Teachers table
CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    department VARCHAR(50),
    hire_date DATE DEFAULT (date('now')),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive'))
);

-- Subjects/Courses table
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code VARCHAR(10) UNIQUE NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    description TEXT,
    grade_level INTEGER NOT NULL,
    credits DECIMAL(3,2) DEFAULT 1.0
);

-- Class assignments (which teacher teaches which subject)
CREATE TABLE class_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    academic_year VARCHAR(9) NOT NULL, -- e.g., "2024-2025"
    semester VARCHAR(20) NOT NULL,     -- e.g., "Fall", "Spring", "Term 1", etc.
    class_section VARCHAR(10) DEFAULT 'A',
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    UNIQUE(teacher_id, subject_id, academic_year, semester, class_section)
);

-- Student enrollments in classes
CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    enrollment_date DATE DEFAULT (date('now')),
    status VARCHAR(20) DEFAULT 'Enrolled' CHECK (status IN ('Enrolled', 'Dropped', 'Completed')),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (assignment_id) REFERENCES class_assignments(assignment_id),
    UNIQUE(student_id, assignment_id)
);

-- Assessment types (exams, quizzes, homework, projects, etc.)
CREATE TABLE assessment_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    default_weight DECIMAL(5,2) DEFAULT 100.0, -- percentage weight in final grade
    show_on_report_card BOOLEAN DEFAULT TRUE, -- TRUE for items that appear on report card
    is_internal_tracking BOOLEAN DEFAULT FALSE -- TRUE for internal tracking only
);

-- Individual assessments
CREATE TABLE assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    assessment_name VARCHAR(100) NOT NULL,
    description TEXT,
    max_points DECIMAL(6,2) NOT NULL DEFAULT 100.0,
    weight DECIMAL(5,2) DEFAULT 100.0,
    due_date DATE,
    created_date DATE DEFAULT (date('now')),
    FOREIGN KEY (assignment_id) REFERENCES class_assignments(assignment_id),
    FOREIGN KEY (type_id) REFERENCES assessment_types(type_id)
);

-- Student grades
CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL,
    points_earned DECIMAL(6,2),
    points_possible DECIMAL(6,2),
    percentage DECIMAL(5,2),
    letter_grade VARCHAR(2),
    date_graded DATE DEFAULT (date('now')),
    comments TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id),
    UNIQUE(student_id, assessment_id)
);

-- Attendance records
CREATE TABLE attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
    notes TEXT,
    recorded_by INTEGER, -- teacher_id
    recorded_date DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (assignment_id) REFERENCES class_assignments(assignment_id),
    FOREIGN KEY (recorded_by) REFERENCES teachers(teacher_id),
    UNIQUE(student_id, assignment_id, attendance_date)
);

-- Grade point scale
CREATE TABLE grade_scale (
    scale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_grade VARCHAR(2) NOT NULL,
    min_percentage DECIMAL(5,2) NOT NULL,
    max_percentage DECIMAL(5,2) NOT NULL,
    gpa_points DECIMAL(3,2) NOT NULL,
    description VARCHAR(50)
);

-- Academic years and terms
CREATE TABLE academic_periods (
    period_id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year VARCHAR(9) NOT NULL,
    period_name VARCHAR(50) NOT NULL, -- "Fall Semester", "Term 1", etc.
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE
);

-- Insert default grade scale
INSERT INTO grade_scale (letter_grade, min_percentage, max_percentage, gpa_points, description) VALUES
('A', 80, 100, A, 'Excellent'),
('B', 70, 79, B, 'Very Good'),
('C', 60, 69, C, 'Good'),
('D', 50, 59, D, 'Average'),
('F', 0, 49, F, 'Fail');

-- Insert assessment types for REPORT CARD (show_on_report_card = TRUE)
-- Only end-of-term examinations appear on school reports
INSERT INTO assessment_types (type_name, description, default_weight, show_on_report_card, is_internal_tracking) VALUES
('Term 1 Exam', 'End of Term 1 Examination', 100.0, TRUE, FALSE),
('Term 2 Exam', 'End of Term 2 Examination', 100.0, TRUE, FALSE),
('Term 3 Exam', 'End of Term 3 Examination', 100.0, TRUE, FALSE);

-- Insert assessment types for INTERNAL TRACKING ONLY (show_on_report_card = FALSE)
INSERT INTO assessment_types (type_name, description, default_weight, show_on_report_card, is_internal_tracking) VALUES
('Quiz', 'Short quizzes', 15.0, FALSE, TRUE),
('Homework', 'Daily assignments', 20.0, FALSE, TRUE),
('Project', 'Long-term projects', 15.0, FALSE, TRUE),
('Class Participation', 'Class participation and engagement', 10.0, FALSE, TRUE),
('Assignment', 'Class assignments', 15.0, FALSE, TRUE),
('Presentation', 'Student presentations', 10.0, FALSE, TRUE),
('Lab Work', 'Laboratory practical work', 15.0, FALSE, TRUE);

-- Insert standard subjects for Forms 1-4 (Secondary School)
INSERT INTO subjects (subject_code, subject_name, description, grade_level, credits) VALUES
-- Form 1 subjects
('AGRI1', 'Agriculture', 'Agricultural Science for Form 1', 1, 1.0),
('BIOL1', 'Biology', 'Biological Science for Form 1', 1, 1.0),
('BIBK1', 'Bible Knowledge', 'Religious Education for Form 1', 1, 1.0),
('CHEM1', 'Chemistry', 'Chemical Science for Form 1', 1, 1.0),
('CHIC1', 'Chichewa', 'Chichewa Language for Form 1', 1, 1.0),
('COMP1', 'Computer Studies', 'Computer Science for Form 1', 1, 1.0),
('ENGL1', 'English', 'English Language for Form 1', 1, 1.0),
('GEOG1', 'Geography', 'Geography for Form 1', 1, 1.0),
('HIST1', 'History', 'History for Form 1', 1, 1.0),
('LIFE1', 'Life Skills/SOS', 'Life Skills/Social Studies for Form 1', 1, 1.0),
('MATH1', 'Mathematics', 'Mathematics for Form 1', 1, 1.0),
('PHYS1', 'Physics', 'Physics for Form 1', 1, 1.0),

-- Form 2 subjects
('AGRI2', 'Agriculture', 'Agricultural Science for Form 2', 2, 1.0),
('BIOL2', 'Biology', 'Biological Science for Form 2', 2, 1.0),
('BIBK2', 'Bible Knowledge', 'Religious Education for Form 2', 2, 1.0),
('CHEM2', 'Chemistry', 'Chemical Science for Form 2', 2, 1.0),
('CHIC2', 'Chichewa', 'Chichewa Language for Form 2', 2, 1.0),
('COMP2', 'Computer Studies', 'Computer Science for Form 2', 2, 1.0),
('ENGL2', 'English', 'English Language for Form 2', 2, 1.0),
('GEOG2', 'Geography', 'Geography for Form 2', 2, 1.0),
('HIST2', 'History', 'History for Form 2', 2, 1.0),
('LIFE2', 'Life Skills/SOS', 'Life Skills/Social Studies for Form 2', 2, 1.0),
('MATH2', 'Mathematics', 'Mathematics for Form 2', 2, 1.0),
('PHYS2', 'Physics', 'Physics for Form 2', 2, 1.0),

-- Form 3 subjects
('AGRI3', 'Agriculture', 'Agricultural Science for Form 3', 3, 1.0),
('BIOL3', 'Biology', 'Biological Science for Form 3', 3, 1.0),
('BIBK3', 'Bible Knowledge', 'Religious Education for Form 3', 3, 1.0),
('CHEM3', 'Chemistry', 'Chemical Science for Form 3', 3, 1.0),
('CHIC3', 'Chichewa', 'Chichewa Language for Form 3', 3, 1.0),
('COMP3', 'Computer Studies', 'Computer Science for Form 3', 3, 1.0),
('ENGL3', 'English', 'English Language for Form 3', 3, 1.0),
('GEOG3', 'Geography', 'Geography for Form 3', 3, 1.0),
('HIST3', 'History', 'History for Form 3', 3, 1.0),
('LIFE3', 'Life Skills/SOS', 'Life Skills/Social Studies for Form 3', 3, 1.0),
('MATH3', 'Mathematics', 'Mathematics for Form 3', 3, 1.0),
('PHYS3', 'Physics', 'Physics for Form 3', 3, 1.0),

-- Form 4 subjects
('AGRI4', 'Agriculture', 'Agricultural Science for Form 4', 4, 1.0),
('BIOL4', 'Biology', 'Biological Science for Form 4', 4, 1.0),
('BIBK4', 'Bible Knowledge', 'Religious Education for Form 4', 4, 1.0),
('CHEM4', 'Chemistry', 'Chemical Science for Form 4', 4, 1.0),
('CHIC4', 'Chichewa', 'Chichewa Language for Form 4', 4, 1.0),
('COMP4', 'Computer Studies', 'Computer Science for Form 4', 4, 1.0),
('ENGL4', 'English', 'English Language for Form 4', 4, 1.0),
('GEOG4', 'Geography', 'Geography for Form 4', 4, 1.0),
('HIST4', 'History', 'History for Form 4', 4, 1.0),
('LIFE4', 'Life Skills/SOS', 'Life Skills/Social Studies for Form 4', 4, 1.0),
('MATH4', 'Mathematics', 'Mathematics for Form 4', 4, 1.0),
('PHYS4', 'Physics', 'Physics for Form 4', 4, 1.0);

-- Insert academic terms for the year
INSERT INTO academic_periods (academic_year, period_name, start_date, end_date, is_current) VALUES
('2024-2025', 'Term 1', '2024-09-01', '2024-12-15', FALSE),
('2024-2025', 'Term 2', '2025-01-15', '2025-04-30', FALSE),
('2024-2025', 'Term 3', '2025-05-15', '2025-08-15', TRUE),
('2025-2026', 'Term 1', '2025-09-01', '2025-12-15', FALSE),
('2025-2026', 'Term 2', '2026-01-15', '2026-04-30', FALSE),
('2025-2026', 'Term 3', '2026-05-15', '2026-08-15', FALSE);

-- Create indexes for better performance
CREATE INDEX idx_students_grade_level ON students(grade_level);
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_grades_student_id ON grades(student_id);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, attendance_date);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
