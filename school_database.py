#!/usr/bin/env python3
"""
School Reporting Database System
Main application for managing student records, grades, and reports
With separate tracking for Report Card items vs Internal Assessment items
Created: 2025-08-06
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
import os
from typing import List, Dict, Optional, Tuple, Any
import logging

# Optional Postgres support (psycopg2)
try:
    import psycopg2
    HAVE_PSYCOPG2 = True
except ImportError:
    psycopg2 = None
    HAVE_PSYCOPG2 = False

# Import persistent data manager for Render deployment
try:
    from persistent_data_manager import PersistentDataManager
    PERSISTENT_MANAGER = PersistentDataManager()
except ImportError:
    PERSISTENT_MANAGER = None
    logging.warning("Persistent data manager not available - using default storage")

class SchoolDatabase:
    """Main class for managing school database operations"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and setup logging"""
        # Detect whether to use Postgres (DATABASE_URL) or SQLite file
        self.use_postgres = False
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Prefer Postgres when DATABASE_URL is set
            if not HAVE_PSYCOPG2:
                raise ImportError("psycopg2 is required for Postgres support. Install psycopg2-binary in requirements.txt")
            self.use_postgres = True
            self.db_path = database_url
        else:
            if db_path is None:
                # Use persistent storage in production, local file in development
                if PERSISTENT_MANAGER:
                    db_path = PERSISTENT_MANAGER.get_database_path()
                else:
                    db_path = os.environ.get('DATABASE_PATH', 'school_reports.db')
                
                # Ensure directory exists for persistent storage
                if db_path != 'school_reports.db':
                    os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.db_path = db_path

        self.setup_logging()
        self.init_database()
        
        # Setup persistent storage features
        if PERSISTENT_MANAGER:
            PERSISTENT_MANAGER.setup_auto_backup()
            
            # Log whether we are using persistent disk
            using_disk = PERSISTENT_MANAGER.is_using_persistent_disk()
            self.logger.info(f"Persistent disk in use: {using_disk}")
            self.logger.info(f"Database path: {self.db_path}")

            # Verify data integrity on startup
            integrity_status = self.verify_data_integrity_on_startup()
            self.logger.info(f"Data integrity check: {integrity_status['status']} - {integrity_status['message']}")
            
            # Create initial backup if database exists and has data
            if os.path.exists(self.db_path) and integrity_status.get('status') == 'valid':
                self.logger.info("Creating initial backup of existing database")
                PERSISTENT_MANAGER.create_backup(self.db_path)
                self.create_data_protection_checkpoint()

            # If the persistent manager indicates we are not using persistent disk, warn the operator
            if not PERSISTENT_MANAGER.is_using_persistent_disk():
                self.logger.warning("PersistentDataManager detected that the configured DATABASE_PATH may not be on a persistent disk. Please ensure DATABASE_PATH points to a persistent volume on Render.")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('school_database.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize the database with schema if it doesn't exist"""
        try:
            # Check for data protection before initializing
            if not self.protect_against_data_wipe():
                self.logger.error("Database initialization blocked by data protection")
                raise Exception("Database operation blocked to prevent data loss")
            
            # If running with Postgres, initialize Postgres-compatible schema
            if getattr(self, 'use_postgres', False):
                self.init_postgres_database()
                return

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tables if they don't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_number TEXT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        date_of_birth TEXT,
                        grade_level INTEGER NOT NULL,
                        email TEXT,
                        phone TEXT,
                        address TEXT,
                        parent_guardian_name TEXT,
                        parent_guardian_phone TEXT,
                        parent_guardian_email TEXT,
                        status TEXT DEFAULT 'Active',
                        date_enrolled TEXT DEFAULT CURRENT_TIMESTAMP,
                        school_id INTEGER NOT NULL,
                        UNIQUE(student_number, school_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_marks (
                        mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        subject TEXT NOT NULL,
                        mark INTEGER NOT NULL,
                        grade TEXT NOT NULL,
                        term TEXT NOT NULL,
                        academic_year TEXT NOT NULL,
                        form_level INTEGER NOT NULL,
                        date_entered TEXT DEFAULT CURRENT_TIMESTAMP,
                        school_id INTEGER NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES students (student_id),
                        UNIQUE(student_id, subject, term, academic_year, school_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS school_settings (
                        setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        school_name TEXT,
                        school_address TEXT,
                        school_phone TEXT,
                        school_email TEXT,
                        pta_fund TEXT,
                        sdf_fund TEXT,
                        boarding_fee TEXT,
                        next_term_begins TEXT,
                        boys_uniform TEXT,
                        girls_uniform TEXT,
                        selected_term TEXT,
                        selected_academic_year TEXT,
                        updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        school_id INTEGER,
                        UNIQUE(school_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS academic_periods (
                        period_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        academic_year TEXT NOT NULL,
                        period_name TEXT NOT NULL,
                        start_date TEXT,
                        end_date TEXT,
                        is_active INTEGER DEFAULT 0,
                        school_id INTEGER,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(academic_year, period_name, school_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subject_teachers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject TEXT NOT NULL,
                        form_level INTEGER NOT NULL,
                        teacher_name TEXT NOT NULL,
                        updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        school_id INTEGER,
                        UNIQUE(subject, form_level, school_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS school_fees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pta_fund TEXT,
                        sdf_fund TEXT,
                        boarding_fee TEXT,
                        updated_date TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schools (
                        school_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        school_name TEXT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        subscription_status TEXT DEFAULT 'trial',
                        subscription_start_date TEXT,
                        subscription_end_date TEXT,
                        days_remaining INTEGER DEFAULT 90,
                        must_change_password INTEGER DEFAULT 0,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        last_login TEXT
                    )
                """)
                
                # Add school_id columns to existing tables if they don't exist
                try:
                    cursor.execute("ALTER TABLE students ADD COLUMN school_id INTEGER")
                except:
                    pass
                
                try:
                    cursor.execute("ALTER TABLE student_marks ADD COLUMN school_id INTEGER")
                except:
                    pass
                
                try:
                    cursor.execute("ALTER TABLE subject_teachers ADD COLUMN school_id INTEGER")
                except:
                    pass
                
                # Add missing columns to school_settings
                try:
                    cursor.execute("ALTER TABLE school_settings ADD COLUMN sdf_fund TEXT")
                except:
                    pass
                
                try:
                    cursor.execute("ALTER TABLE school_settings ADD COLUMN boarding_fee TEXT")
                except:
                    pass
                
                # Fix UNIQUE constraint for student_number to be per school
                try:
                    # Check if we need to recreate the students table
                    cursor.execute("PRAGMA table_info(students)")
                    columns = cursor.fetchall()
                    
                    # Create new table with correct constraints
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS students_new (
                            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_number TEXT,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            date_of_birth TEXT,
                            grade_level INTEGER NOT NULL,
                            email TEXT,
                            phone TEXT,
                            address TEXT,
                            parent_guardian_name TEXT,
                            parent_guardian_phone TEXT,
                            parent_guardian_email TEXT,
                            status TEXT DEFAULT 'Active',
                            date_enrolled TEXT DEFAULT CURRENT_TIMESTAMP,
                            school_id INTEGER,
                            UNIQUE(student_number, school_id)
                        )
                    """)
                    
                    # Copy data from old table
                    cursor.execute("""
                        INSERT OR IGNORE INTO students_new 
                        SELECT * FROM students
                    """)
                    
                    # Drop old table and rename new one
                    cursor.execute("DROP TABLE students")
                    cursor.execute("ALTER TABLE students_new RENAME TO students")
                    
                except Exception as e:
                    # If recreation fails, just continue - table might already be correct
                    pass
                
                # Add subscription columns to existing schools table if they don't exist
                try:
                    cursor.execute("ALTER TABLE schools ADD COLUMN subscription_status TEXT DEFAULT 'trial'")
                except:
                    pass
                
                try:
                    cursor.execute("ALTER TABLE schools ADD COLUMN subscription_start_date TEXT")
                except:
                    pass
                
                try:
                    cursor.execute("ALTER TABLE schools ADD COLUMN subscription_end_date TEXT")
                except:
                    pass
                
                try:
                    cursor.execute("ALTER TABLE schools ADD COLUMN days_remaining INTEGER DEFAULT 90")
                except:
                    pass

                try:
                    cursor.execute("ALTER TABLE schools ADD COLUMN must_change_password INTEGER DEFAULT 0")
                except:
                    pass
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subscription_notifications (
                        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        school_id INTEGER,
                        message TEXT NOT NULL,
                        notification_type TEXT DEFAULT 'reminder',
                        sent_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_read INTEGER DEFAULT 0,
                        FOREIGN KEY (school_id) REFERENCES schools (school_id)
                    )
                """)
                
                # Update existing schools with default subscription values
                cursor.execute("""
                    UPDATE schools 
                    SET subscription_status = 'trial', days_remaining = 90 
                    WHERE subscription_status IS NULL OR subscription_status = ''
                """)
                
                # Add selected_term and selected_academic_year columns if they don't exist
                cursor.execute("PRAGMA table_info(school_settings)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'selected_term' not in columns:
                    try:
                        cursor.execute("ALTER TABLE school_settings ADD COLUMN selected_term TEXT")
                        self.logger.info("Added selected_term column to school_settings")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e):
                            self.logger.error(f"Error adding selected_term column: {e}")
                
                if 'selected_academic_year' not in columns:
                    try:
                        cursor.execute("ALTER TABLE school_settings ADD COLUMN selected_academic_year TEXT")
                        self.logger.info("Added selected_academic_year column to school_settings")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e):
                            self.logger.error(f"Error adding selected_academic_year column: {e}")
                
                # Create default settings for existing schools that don't have settings
                cursor.execute("""
                    SELECT s.school_id, s.school_name, s.username 
                    FROM schools s 
                    LEFT JOIN school_settings ss ON s.school_id = ss.school_id 
                    WHERE ss.school_id IS NULL
                """)
                schools_without_settings = cursor.fetchall()
                
                for school_id, school_name, username in schools_without_settings:
                    # Create blank settings for existing schools - waiting for admin to edit
                    cursor.execute("""
                        INSERT INTO school_settings 
                        (school_name, school_address, school_phone, school_email, pta_fund, sdf_fund, boarding_fee, next_term_begins, boys_uniform, girls_uniform, selected_term, selected_academic_year, school_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        '',  # Blank - admin will fill in
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',  # selected_term - blank initially
                        '',  # selected_academic_year - blank initially
                        school_id
                    ))
                
                # Insert default fees if none exist
                cursor.execute("SELECT COUNT(*) FROM school_fees")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO school_fees (pta_fund, sdf_fund, boarding_fee)
                        VALUES (?, ?, ?)
                    """, ("", "", "MK 150,000"))
                
                # Insert default subject teachers if none exist
                cursor.execute("SELECT COUNT(*) FROM subject_teachers")
                if cursor.fetchone()[0] == 0:
                    subjects = ['Agriculture', 'Bible Knowledge', 'Biology', 'Chemistry', 
                               'Chichewa', 'Computer Studies', 'English', 'Geography', 
                               'History', 'Life Skills/SOS', 'Mathematics', 'Physics', 'Business Studies', 'Home Economics']

                    # Determine whether subject_teachers.school_id allows NULL
                    cursor.execute("PRAGMA table_info(subject_teachers)")
                    cols = cursor.fetchall()
                    school_id_notnull = 0
                    for c in cols:
                        # PRAGMA table_info returns: cid,name,type,notnull,dflt_value,pk
                        if c[1] == 'school_id':
                            school_id_notnull = c[3]
                            break

                    default_school_id = None if school_id_notnull == 0 else 0

                    for form_level in [1, 2, 3, 4]:
                        for subject in subjects:
                            cursor.execute("""
                                INSERT INTO subject_teachers (subject, form_level, teacher_name, school_id)
                                VALUES (?, ?, ?, ?)
                            """, (subject, form_level, f"{subject} Teacher F{form_level}", default_school_id))
                
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def init_postgres_database(self):
        """Initialize Postgres database with tables compatible with current schema."""
        try:
            if not HAVE_PSYCOPG2:
                self.logger.error("psycopg2 not available; cannot initialize Postgres database")
                raise ImportError("psycopg2 not available")
            conn = psycopg2.connect(self.db_path)
            cur = conn.cursor()

            # Use Postgres-compatible table definitions
            cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id SERIAL PRIMARY KEY,
                student_number TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT,
                grade_level INTEGER NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                parent_guardian_name TEXT,
                parent_guardian_phone TEXT,
                parent_guardian_email TEXT,
                status TEXT DEFAULT 'Active',
                date_enrolled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                school_id INTEGER,
                UNIQUE(student_number, school_id)
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS student_marks (
                mark_id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                mark INTEGER NOT NULL,
                grade TEXT NOT NULL,
                term TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                form_level INTEGER NOT NULL,
                date_entered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                school_id INTEGER NOT NULL
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS school_settings (
                setting_id SERIAL PRIMARY KEY,
                school_name TEXT,
                school_address TEXT,
                school_phone TEXT,
                school_email TEXT,
                pta_fund TEXT,
                sdf_fund TEXT,
                boarding_fee TEXT,
                next_term_begins TEXT,
                boys_uniform TEXT,
                girls_uniform TEXT,
                selected_term TEXT,
                selected_academic_year TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                school_id INTEGER UNIQUE
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS academic_periods (
                period_id SERIAL PRIMARY KEY,
                academic_year TEXT NOT NULL,
                period_name TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                is_active INTEGER DEFAULT 0,
                school_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (academic_year, period_name, school_id)
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS subject_teachers (
                id SERIAL PRIMARY KEY,
                subject TEXT NOT NULL,
                form_level INTEGER NOT NULL,
                teacher_name TEXT NOT NULL,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                school_id INTEGER
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS school_fees (
                id SERIAL PRIMARY KEY,
                pta_fund TEXT,
                sdf_fund TEXT,
                boarding_fee TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                school_id SERIAL PRIMARY KEY,
                school_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                subscription_status TEXT DEFAULT 'trial',
                subscription_start_date TEXT,
                subscription_end_date TEXT,
                days_remaining INTEGER DEFAULT 90,
                must_change_password INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS subscription_notifications (
                notification_id SERIAL PRIMARY KEY,
                school_id INTEGER,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'reminder',
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0
            )
            """)

            conn.commit()
            cur.close()
            conn.close()
            self.logger.info("Postgres database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Postgres database: {e}")
            raise

    def create_schema(self, conn):
        """Create database schema from SQL file"""
        try:
            with open('database_schema.sql', 'r') as file:
                schema_sql = file.read()
                conn.executescript(schema_sql)
        except FileNotFoundError:
            self.logger.error("database_schema.sql file not found!")
            raise
    
    def _adapt_query(self, query: str) -> str:
        """Adapt SQL query placeholders for the selected DB backend"""
        if getattr(self, 'use_postgres', False):
            return query.replace('?', '%s')
        return query

    def get_connection(self):
        """Get database connection. Uses psycopg2 for Postgres when configured, else SQLite."""
        if getattr(self, 'use_postgres', False):
            # psycopg2 accepts a DSN-style URL in connect()
            conn = psycopg2.connect(self.db_path)

            # Wrap the cursor factory to adapt SQLite-style queries (?), to postgres (%s)
            dbself = self
            class CursorAdapter:
                def __init__(self, cursor):
                    self._cursor = cursor
                    self._lastrowid = None

                def execute(self, query, params=None):
                    q = query.replace('?', '%s') if dbself.use_postgres else query
                    self._cursor.execute(q, params or ())
                    # If insert, attempt to capture lastval
                    try:
                        if dbself.use_postgres and q.strip().lower().startswith('insert'):
                            # Use a separate cursor to fetch LASTVAL so we don't disturb results
                            with conn.cursor() as c2:
                                c2.execute('SELECT LASTVAL()')
                                res = c2.fetchone()
                                self._lastrowid = res[0] if res else None
                    except Exception:
                        self._lastrowid = None
                    return self._cursor

                def executemany(self, query, seq_of_params):
                    q = query.replace('?', '%s') if dbself.use_postgres else query
                    return self._cursor.executemany(q, seq_of_params)

                def fetchone(self):
                    return self._cursor.fetchone()

                def fetchall(self):
                    return self._cursor.fetchall()

                def __getattr__(self, name):
                    return getattr(self._cursor, name)

                @property
                def lastrowid(self):
                    if dbself.use_postgres:
                        return self._lastrowid
                    return getattr(self._cursor, 'lastrowid', None)

            # Replace cursor method to return adapter
            def cursor_factory(*args, **kwargs):
                return CursorAdapter(conn.cursor(*args, **kwargs))

            conn.cursor = cursor_factory
            return conn

        conn = sqlite3.connect(self.db_path, timeout=30.0)
        # Prefer DELETE journaling on Windows to avoid locking issues with temporary files
        try:
            conn.execute('PRAGMA journal_mode=DELETE')
        except sqlite3.OperationalError:
            # If the DB is briefly locked by another connection, retry once after a short delay
            import time
            time.sleep(0.05)
            try:
                conn.execute('PRAGMA journal_mode=DELETE')
            except Exception:
                # Give up changing the journal mode and proceed; caller will handle any locks
                pass
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=10000')
        conn.execute('PRAGMA temp_store=memory')
        return conn
    
    def _get_next_student_serial_number(self, school_id: Optional[int]) -> str:
        """Generate the next student serial number for a specific school"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if school_id is None:
                    cursor.execute("SELECT MAX(CAST(student_number AS INTEGER)) FROM students WHERE school_id IS NULL")
                else:
                    cursor.execute("SELECT MAX(CAST(student_number AS INTEGER)) FROM students WHERE school_id = ?", (school_id,))
                result = cursor.fetchone()
                max_num = result[0] if result and result[0] is not None else 0
                return f"{max_num + 1:04d}"
        except Exception as e:
            self.logger.error(f"Error generating next student serial number: {e}")
            # Generate a unique fallback using timestamp
            import time
            return f"{int(time.time()) % 10000:04d}"

    # STUDENT MANAGEMENT METHODS
    def add_student(self, student_data: Dict, school_id: Optional[int] = None) -> int:
        """Add a new student to the database for a specific school.

        `school_id` is optional for legacy or single-school setups; when omitted
        the student will be stored with a NULL `school_id`.
        """
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Generate new student serial number for this school (handles None)
                student_serial_number = self._get_next_student_serial_number(school_id)
                
                insert_sql = """
                    INSERT INTO students (
                        student_number, first_name, last_name, date_of_birth,
                        grade_level, email, phone, address, parent_guardian_name,
                        parent_guardian_phone, parent_guardian_email, school_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(self._adapt_query(insert_sql), (
                    student_serial_number,
                    student_data.get('first_name'),
                    student_data.get('last_name'),
                    student_data.get('date_of_birth'),
                    student_data.get('grade_level') or student_data.get('form_level'),
                    student_data.get('email'),
                    student_data.get('phone'),
                    student_data.get('address'),
                    student_data.get('parent_guardian_name'),
                    student_data.get('parent_guardian_phone'),
                    student_data.get('parent_guardian_email'),
                    school_id
                ))
                if getattr(self, 'use_postgres', False):
                    # Get the last inserted id in Postgres
                    cursor.execute("SELECT LASTVAL()")
                    student_id = cursor.fetchone()[0]
                else:
                    student_id = cursor.lastrowid
                self.logger.info(f"Added student: {student_data.get('first_name')} {student_data.get('last_name')} (ID: {student_id}, School: {school_id})")
                return student_id
        except Exception as e:
            self.logger.error(f"Error adding student: {e}")
            raise
    
    def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        """Get student information by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(self._adapt_query("SELECT * FROM students WHERE student_id = ?"), (student_id,))
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving student {student_id}: {e}")
            raise
    
    def check_marks_exist_for_period(self, form_level: int, term: str, academic_year: str, school_id: int) -> bool:
        """Check if any marks exist for the given form, term, and academic year"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM student_marks 
                    WHERE form_level = ? AND term = ? AND academic_year = ? AND school_id = ?
                    LIMIT 1
                """, (form_level, term, academic_year, school_id))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self.logger.error(f"Error checking marks for period: {e}")
            return False
    
    def get_students_by_grade(self, grade_level: int, school_id: int = None) -> List[Dict]:
        """Get all students in a specific grade level. If `school_id` is provided, filter by school."""
            
        try:
            with self.get_connection() as conn:
                if school_id:
                    df = pd.read_sql_query(
                        "SELECT * FROM students WHERE grade_level = ? AND (status = 'Active' OR status IS NULL OR status = '') AND school_id = ? ORDER BY first_name, last_name",
                        conn, params=(grade_level, school_id)
                    )
                else:
                    df = pd.read_sql_query(
                        "SELECT * FROM students WHERE grade_level = ? AND (status = 'Active' OR status IS NULL OR status = '') ORDER BY first_name, last_name",
                        conn, params=(grade_level,)
                    )
                return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error retrieving students for grade {grade_level}: {e}")
            raise
    
    def update_student(self, student_id: int, update_data: dict, school_id: int = None):
        """Update student information with flexible field updates"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically
                update_fields = []
                update_values = []
                
                for field, value in update_data.items():
                    if field in ['first_name', 'last_name', 'date_of_birth', 'email', 'phone', 'address', 
                               'parent_guardian_name', 'parent_guardian_phone', 'parent_guardian_email']:
                        update_fields.append(f"{field} = ?")
                        update_values.append(value)
                
                if not update_fields:
                    return False
                
                # Add student_id to values
                update_values.append(student_id)
                
                # Add school filter if provided
                where_clause = "WHERE student_id = ?"
                if school_id:
                    where_clause += " AND (school_id = ? OR school_id IS NULL)"
                    update_values.append(school_id)
                
                query = f"UPDATE students SET {', '.join(update_fields)} {where_clause}"
                cursor.execute(query, update_values)
                
                self.logger.info(f"Updated student {student_id} with fields: {list(update_data.keys())}")
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Error updating student {student_id}: {e}")
            raise
    
    # ASSESSMENT TYPE MANAGEMENT
    def get_report_card_assessment_types(self) -> List[Dict]:
        """Get assessment types that appear on report cards"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM assessment_types WHERE show_on_report_card = TRUE ORDER BY type_name",
                    conn
                )
                return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error retrieving report card assessment types: {e}")
            raise
    
    def get_internal_tracking_assessment_types(self) -> List[Dict]:
        """Get assessment types for internal tracking only"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM assessment_types WHERE is_internal_tracking = TRUE ORDER BY type_name",
                    conn
                )
                return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error retrieving internal tracking assessment types: {e}")
            raise
    
    # TEACHER MANAGEMENT METHODS
    def add_teacher(self, teacher_data: Dict) -> int:
        """Add a new teacher to the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO teachers (
                        employee_id, first_name, last_name, email, phone, department
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    teacher_data.get('employee_id'),
                    teacher_data.get('first_name'),
                    teacher_data.get('last_name'),
                    teacher_data.get('email'),
                    teacher_data.get('phone'),
                    teacher_data.get('department')
                ))
                teacher_id = cursor.lastrowid
                self.logger.info(f"Added teacher: {teacher_data.get('first_name')} {teacher_data.get('last_name')} (ID: {teacher_id})")
                return teacher_id
        except Exception as e:
            self.logger.error(f"Error adding teacher: {e}")
            raise
    
    # SUBJECT MANAGEMENT METHODS
    def add_subject(self, subject_data: Dict) -> int:
        """Add a new subject to the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO subjects (subject_code, subject_name, description, grade_level, credits)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    subject_data.get('subject_code'),
                    subject_data.get('subject_name'),
                    subject_data.get('description'),
                    subject_data.get('grade_level'),
                    subject_data.get('credits', 1.0)
                ))
                subject_id = cursor.lastrowid
                self.logger.info(f"Added subject: {subject_data.get('subject_name')} (ID: {subject_id})")
                return subject_id
        except Exception as e:
            self.logger.error(f"Error adding subject: {e}")
            raise
    
    # GRADE MANAGEMENT METHODS
    def add_grade(self, grade_data: Dict) -> int:
        """Add a grade record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Calculate percentage and letter grade
                points_earned = grade_data.get('points_earned')
                points_possible = grade_data.get('points_possible')
                percentage = (points_earned / points_possible * 100) if points_possible > 0 else 0
                letter_grade = self.calculate_letter_grade(percentage)
                
                cursor.execute("""
                    INSERT INTO grades (
                        student_id, assessment_id, points_earned, points_possible,
                        percentage, letter_grade, comments
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    grade_data.get('student_id'),
                    grade_data.get('assessment_id'),
                    points_earned,
                    points_possible,
                    percentage,
                    letter_grade,
                    grade_data.get('comments')
                ))
                grade_id = cursor.lastrowid
                self.logger.info(f"Added grade record (ID: {grade_id})")
                return grade_id
        except Exception as e:
            self.logger.error(f"Error adding grade: {e}")
            raise
    
    def calculate_letter_grade(self, percentage: float) -> str:
        """Calculate letter grade based on percentage"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT letter_grade FROM grade_scale 
                    WHERE ? BETWEEN min_percentage AND max_percentage
                """, (percentage,))
                result = cursor.fetchone()
                return result[0] if result else 'F'
        except Exception as e:
            self.logger.error(f"Error calculating letter grade: {e}")
            return 'F'
    
    def save_student_mark(self, student_id: int, subject: str, mark: int, term: str, academic_year: str, form_level: int, school_id: Optional[int] = None):
        """Save student mark for a subject.

        `school_id` is optional; when omitted the method will store marks without
        a school_id (NULL) or infer from the student record when available.
        """
            
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Calculate grade based on form level
                    grade = self.calculate_grade(mark, form_level)
                    
                    # If school_id not provided, try to infer from the student record
                    if school_id is None:
                        student = self.get_student_by_id(student_id)
                        if student and 'school_id' in student:
                            school_id = student.get('school_id')
                    # If still None (legacy or single-school tests), default to 0 to satisfy NOT NULL schema
                    if school_id is None:
                        school_id = 0

                    # Begin transaction (SQLite uses BEGIN IMMEDIATE; Postgres manages transactions differently)
                    if not getattr(self, 'use_postgres', False):
                        cursor.execute("BEGIN IMMEDIATE")
                    
                    # Insert or update mark
                    insert_sql = """
                        INSERT OR REPLACE INTO student_marks 
                        (student_id, subject, mark, grade, term, academic_year, form_level, date_entered, school_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(self._adapt_query(insert_sql), (student_id, subject, mark, grade, term, academic_year, form_level, datetime.now().isoformat(), school_id))
                    
                    # Commit the transaction
                    if getattr(self, 'use_postgres', False):
                        conn.commit()
                    else:
                        conn.commit()
                    
                    self.logger.info(f"Saved mark for student {student_id}, subject {subject}: {mark} (School: {school_id})")
                    return  # Success, exit the retry loop
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and retry_count < max_retries - 1:
                    retry_count += 1
                    import time
                    time.sleep(0.1 * retry_count)  # Exponential backoff
                    self.logger.warning(f"Database locked, retrying ({retry_count}/{max_retries})")
                    continue
                else:
                    self.logger.error(f"Database locked error after {max_retries} retries: {e}")
                    raise
            except Exception as e:
                self.logger.error(f"Error saving student mark: {e}")
                raise
    
    def create_data_protection_checkpoint(self) -> bool:
        """Create a data protection checkpoint to prevent accidental wipes"""
        try:
            if PERSISTENT_MANAGER:
                # Create a protection checkpoint
                checkpoint_path = os.path.join(os.path.dirname(self.db_path), '.data_protection')
                with open(checkpoint_path, 'w') as f:
                    f.write(f"checkpoint_created:{datetime.now().isoformat()}\n")
                    f.write(f"database_path:{self.db_path}\n")
                    f.write(f"database_size:{os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0}\n")
                
                self.logger.info("Data protection checkpoint created")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to create protection checkpoint: {e}")
            return False
    
    def verify_data_integrity_on_startup(self) -> Dict:
        """Verify data integrity on application startup"""
        try:
            # For filesystem SQLite, check file existence
            if not getattr(self, 'use_postgres', False) and not os.path.exists(self.db_path):
                return {
                    'status': 'no_database',
                    'message': 'Database file not found - will create new one'
                }
            
            # Check if database is corrupted or empty
            with self.get_connection() as conn:
                cursor = conn.cursor()
                tables = []
                if getattr(self, 'use_postgres', False):
                    # Use information_schema to check for essential tables
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('students','student_marks','school_settings')")
                    tables = [row[0] for row in cursor.fetchall()]
                else:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name IN ('students', 'student_marks', 'school_settings')
                    """)
                    tables = [row[0] for row in cursor.fetchall()]
                
                if len(tables) < 3:
                    return {
                        'status': 'incomplete',
                        'message': f'Database incomplete - found {len(tables)}/3 essential tables'
                    }
                
                # Count records
                cursor.execute(self._adapt_query("SELECT COUNT(*) FROM students"))
                student_count = cursor.fetchone()[0]
                
                cursor.execute(self._adapt_query("SELECT COUNT(*) FROM student_marks"))
                marks_count = cursor.fetchone()[0]
                
                cursor.execute(self._adapt_query("SELECT COUNT(*) FROM school_settings"))
                settings_count = cursor.fetchone()[0]
                
                if student_count == 0 and marks_count == 0 and settings_count == 0:
                    return {
                        'status': 'empty',
                        'message': 'Database appears to be empty - new installation detected'
                    }
                
                return {
                    'status': 'valid',
                    'message': f'Database valid - {student_count} students, {marks_count} marks, {settings_count} settings',
                    'student_count': student_count,
                    'marks_count': marks_count,
                    'settings_count': settings_count
                }
                
        except Exception as e:
            self.logger.error(f"Data integrity verification failed: {e}")
            return {
                'status': 'error',
                'message': f'Verification failed: {str(e)}'
            }
    
    def protect_against_data_wipe(self) -> bool:
        """Protect against accidental data wipe operations"""
        try:
            # Check if this is a potential wipe operation
            if PERSISTENT_MANAGER:
                checkpoint_path = os.path.join(os.path.dirname(self.db_path), '.data_protection')
                
                if os.path.exists(checkpoint_path):
                    # Read checkpoint data
                    with open(checkpoint_path, 'r') as f:
                        lines = f.readlines()
                    
                    checkpoint_data = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            checkpoint_data[key] = value
                    
                    # Check current database size
                    current_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                    expected_size = int(checkpoint_data.get('database_size', '0'))
                    
                    # If database size suddenly drops significantly, block operation
                    if current_size < expected_size * 0.1:  # Less than 10% of expected size
                        self.logger.warning(f"Potential data wipe detected - blocking operation")
                        self.logger.warning(f"Expected size: {expected_size}, Current size: {current_size}")
                        return False
                
            return True  # Allow operation
        except Exception as e:
            self.logger.error(f"Data protection check failed: {e}")
            return True
    
    def get_student_marks(self, student_id: int, term: str, academic_year: str, school_id: int = None) -> Dict:
        """Get all marks for a student in a term for a specific school. If school_id is omitted, try to infer from the student record."""
        # If school_id is not provided, try to infer it from the student record.
        inferred_school_id = school_id
        if inferred_school_id is None:
            student = self.get_student_by_id(student_id)
            if student and 'school_id' in student and student.get('school_id') is not None:
                inferred_school_id = student['school_id']

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if inferred_school_id is None:
                    # No school filter: return marks for the student across any school_id (including NULL)
                    cursor.execute("""
                        SELECT subject, mark, grade FROM student_marks 
                        WHERE student_id = ? AND term = ? AND academic_year = ?
                    """, (student_id, term, academic_year))
                else:
                    cursor.execute("""
                        SELECT subject, mark, grade FROM student_marks 
                        WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                    """, (student_id, term, academic_year, inferred_school_id))

                marks = {}
                for row in cursor.fetchall():
                    marks[row[0]] = {'mark': row[1], 'grade': row[2]}

                return marks

        except Exception as e:
            self.logger.error(f"Error retrieving student marks: {e}")
            raise
    
    def calculate_grade(self, mark: int, form_level: int) -> str:
        """Calculate grade based on mark and form level"""
        if form_level in [1, 2]:  # Junior forms
            if mark >= 80: return 'A'
            elif mark >= 70: return 'B'
            elif mark >= 60: return 'C'
            elif mark >= 50: return 'D'
            else: return 'F'
        else:  # Senior forms (3, 4)
            if mark >= 75: return '1'
            elif mark >= 70: return '2'
            elif mark >= 65: return '3'
            elif mark >= 60: return '4'
            elif mark >= 55: return '5'
            elif mark >= 50: return '6'
            elif mark >= 45: return '7'
            elif mark >= 40: return '8'
            else: return '9'
    
    def determine_pass_fail_status(self, passed_subjects: int, english_passed: bool) -> str:
        """Determine overall pass/fail status based on school criteria"""
        # Student must pass at least 6 subjects AND English to be declared PASS
        if passed_subjects >= 6 and english_passed:
            return 'PASS'
        else:
            return 'FAIL'
    
    def is_english_passed(self, english_mark: int, form_level: int) -> bool:
        """Check if English is passed based on form level and grading system"""
        if form_level in [1, 2]:  # Junior forms
            # For junior forms, pass mark is 50% (grade D or better)
            return english_mark >= 50
        else:  # Senior forms (3, 4)
            # For senior forms, grades 1-8 are pass (40+ marks), only grade 9 is fail
            return english_mark >= 40
    
    def is_subject_passed(self, mark: int, form_level: int) -> bool:
        """Check if a subject is passed based on form level and grading system"""
        if form_level in [1, 2]:  # Junior forms
            # For junior forms, pass mark is 50% (grade D or better)
            return mark >= 50
        else:  # Senior forms (3, 4)
            # For senior forms, grades 1-8 are pass (40+ marks), only grade 9 is fail
            return mark >= 40
    
    def get_status_reason(self, passed_subjects: int, english_passed: bool) -> str:
        """Get explanation for pass/fail status"""
        if passed_subjects >= 6 and english_passed:
            return 'Passed 6 or more subjects including English'
        elif passed_subjects >= 6 and not english_passed:
            return 'Failed English (English is mandatory for pass)'
        elif passed_subjects < 6 and english_passed:
            return f'Passed only {passed_subjects} subjects (minimum 6 required)'
        else:
            return f'Passed only {passed_subjects} subjects and failed English'
    
    # REPORT GENERATION METHODS
    def generate_termly_report_card(self, student_id: int, term: str, academic_year: str = '2024-2025') -> Dict:
        """Generate termly school report card with end-of-term exam marks and teacher names"""
        try:
            with self.get_connection() as conn:
                # Get student info
                student = self.get_student_by_id(student_id)
                if not student:
                    raise ValueError(f"Student with ID {student_id} not found")
                
                # Get marks from student_marks table (simpler approach)
                marks_query = """
                    SELECT 
                        subject as subject_name,
                        subject as subject_code,
                        mark as percentage,
                        grade as letter_grade,
                        'Subject Teacher' as teacher_name,
                        '' as comments,
                        date_entered as date_graded
                    FROM student_marks
                    WHERE student_id = ?
                    AND term = ?
                    AND academic_year = ?
                    ORDER BY 
                        CASE subject
                            WHEN 'Agriculture' THEN 1
                            WHEN 'Biology' THEN 2
                            WHEN 'Bible Knowledge' THEN 3
                            WHEN 'Chemistry' THEN 4
                            WHEN 'Chichewa' THEN 5
                            WHEN 'Computer Studies' THEN 6
                            WHEN 'English' THEN 7
                            WHEN 'Geography' THEN 8
                            WHEN 'History' THEN 9
                            WHEN 'Life Skills/SOS' THEN 10
                            WHEN 'Mathematics' THEN 11
                            WHEN 'Physics' THEN 12
                            ELSE 13
                        END
                """
                
                grades_df = pd.read_sql_query(marks_query, conn, params=(
                    student_id, term, academic_year
                ))
                
                # Get attendance summary for the term
                attendance_query = """
                    SELECT 
                        COUNT(*) as total_days,
                        SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days,
                        SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_days,
                        SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_days,
                        SUM(CASE WHEN status = 'Excused' THEN 1 ELSE 0 END) as excused_days
                    FROM attendance a
                    JOIN class_assignments ca ON a.assignment_id = ca.assignment_id
                    WHERE a.student_id = ?
                    AND ca.academic_year = ?
                    AND ca.semester = ?
                """
                attendance_df = pd.read_sql_query(attendance_query, conn, params=(student_id, academic_year, term))
                
                # Calculate overall statistics
                if not grades_df.empty:
                    overall_average = grades_df['percentage'].mean()
                    total_subjects = len(grades_df)
                    # Count passed subjects based on form level
                    if student['grade_level'] in [1, 2]:
                        passed_subjects = len(grades_df[grades_df['percentage'] >= 50])
                    else:
                        passed_subjects = len(grades_df[grades_df['percentage'] >= 40])
                    
                    # Check if English is passed (critical requirement)
                    english_grade = grades_df[grades_df['subject_name'] == 'English']
                    english_passed = False
                    english_percentage = 0
                    
                    if not english_grade.empty:
                        english_percentage = english_grade.iloc[0]['percentage']
                        english_passed = self.is_english_passed(int(english_percentage), student['grade_level'])
                    
                    # Determine overall pass/fail status
                    # Student must pass at least 6 subjects AND English to be declared PASS
                    overall_status = self.determine_pass_fail_status(passed_subjects, english_passed)
                    
                else:
                    overall_average = 0
                    total_subjects = 0
                    passed_subjects = 0
                    english_passed = False
                    english_percentage = 0
                    overall_status = 'FAIL'
                

                # Calculate overall grade with fix for Forms 1-2
                if student['grade_level'] in [1, 2]:
                    # CRITICAL RULE: For Forms 1&2, ANY student who has failed MUST get F average grade
                    if overall_status == 'FAIL':
                        overall_grade = 'F'
                    else:
                        # For passing students, use grade distribution logic
                        if not grades_df.empty:
                            grades = [self.calculate_grade(int(row['percentage']), student['grade_level']) for _, row in grades_df.iterrows()]
                            grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                            for grade in grades:
                                if grade in grade_counts:
                                    grade_counts[grade] += 1
                            
                            max_count = max(grade_counts.values())
                            most_common_grades = [grade for grade, count in grade_counts.items() if count == max_count]
                            
                            if len(most_common_grades) == 1:
                                overall_grade = most_common_grades[0]
                            else:
                                overall_grade = self.calculate_grade(int(overall_average), student['grade_level'])
                            
                            # Ensure passing students don't get F grade
                            if overall_grade == 'F':
                                passing_grades = [g for g in grades if g in ['A', 'B', 'C', 'D']]
                                if passing_grades:
                                    pass_grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                                    for grade in passing_grades:
                                        pass_grade_counts[grade] += 1
                                    
                                    max_pass_count = max(pass_grade_counts.values())
                                    most_common_pass_grades = [grade for grade, count in pass_grade_counts.items() if count == max_pass_count]
                                    
                                    if len(most_common_pass_grades) == 1:
                                        overall_grade = most_common_pass_grades[0]
                                    else:
                                        calculated_grade = self.calculate_grade(int(overall_average), student['grade_level'])
                                        overall_grade = calculated_grade if calculated_grade != 'F' else 'D'
                                else:
                                    overall_grade = 'D'  # Fallback for passed student
                        else:
                            overall_grade = 'F'
                else:
                    # For senior forms, use traditional calculation
                    overall_grade = self.calculate_grade(int(overall_average), student['grade_level'])
                
                return {
                    'report_type': f'{term} School Report Card',
                    'academic_year': academic_year,
                    'term': term,
                    'student_info': student,
                    'subject_grades': grades_df.to_dict('records'),
                    'attendance_summary': attendance_df.to_dict('records')[0] if not attendance_df.empty else {},
                    'overall_statistics': {
                        'overall_average': round(overall_average, 1),
                        'total_subjects': total_subjects,
                        'passed_subjects': passed_subjects,
                        'english_passed': english_passed,
                        'english_percentage': round(english_percentage, 1),
                        'overall_grade': overall_grade,
                        'overall_status': overall_status,
                        'status_reason': self.get_status_reason(passed_subjects, english_passed)
                    },
                    'generated_date': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error generating termly report card: {e}")
            raise
    
    def generate_internal_tracking_report(self, student_id: int, academic_year: str = None) -> Dict:
        """Generate internal tracking report showing quiz, homework, projects, etc."""
        try:
            with self.get_connection() as conn:
                # Get student info
                student = self.get_student_by_id(student_id)
                if not student:
                    raise ValueError(f"Student with ID {student_id} not found")
                
                # Get internal tracking grades only (is_internal_tracking = TRUE)
                grades_query = """
                    SELECT 
                        s.subject_name, 
                        s.subject_code, 
                        at.type_name as assessment_type,
                        g.percentage, 
                        g.letter_grade,
                        a.assessment_name, 
                        g.date_graded, 
                        g.comments,
                        g.points_earned,
                        g.points_possible
                    FROM grades g
                    JOIN assessments a ON g.assessment_id = a.assessment_id
                    JOIN assessment_types at ON a.type_id = at.type_id
                    JOIN class_assignments ca ON a.assignment_id = ca.assignment_id
                    JOIN subjects s ON ca.subject_id = s.subject_id
                    WHERE g.student_id = ? 
                    AND at.is_internal_tracking = TRUE
                    ORDER BY s.subject_name, g.date_graded DESC
                """
                params = [student_id]
                
                if academic_year:
                    grades_query += " AND ca.academic_year = ?"
                    params.append(academic_year)
                
                internal_grades_df = pd.read_sql_query(grades_query, conn, params=params)
                
                return {
                    'report_type': 'Internal Tracking Report',
                    'student_info': student,
                    'internal_assessments': internal_grades_df.to_dict('records'),
                    'generated_date': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error generating internal tracking report: {e}")
            raise
    
    def generate_comprehensive_teacher_report(self, student_id: int, academic_year: str = None) -> Dict:
        """Generate comprehensive report for teachers showing both report card and internal tracking"""
        try:
            report_card_data = self.generate_official_report_card(student_id, academic_year)
            internal_data = self.generate_internal_tracking_report(student_id, academic_year)
            
            return {
                'report_type': 'Comprehensive Teacher Report',
                'student_info': report_card_data['student_info'],
                'official_report_card': report_card_data['report_card_grades'],
                'internal_assessments': internal_data['internal_assessments'],
                'attendance_summary': report_card_data['attendance_summary'],
                'generated_date': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error generating comprehensive teacher report: {e}")
            raise
    
    def generate_class_summary(self, assignment_id: int, report_type: str = 'official') -> Dict:
        """Generate class summary report (official or internal)"""
        try:
            with self.get_connection() as conn:
                if report_type == 'official':
                    condition = "AND at.show_on_report_card = TRUE"
                elif report_type == 'internal':
                    condition = "AND at.is_internal_tracking = TRUE"
                else:
                    condition = ""  # All assessments
                
                query = f"""
                    SELECT 
                        s.student_number,
                        s.first_name,
                        s.last_name,
                        AVG(g.percentage) as average_grade,
                        COUNT(g.grade_id) as total_assessments
                    FROM students s
                    JOIN enrollments e ON s.student_id = e.student_id
                    LEFT JOIN grades g ON s.student_id = g.student_id
                    LEFT JOIN assessments a ON g.assessment_id = a.assessment_id
                    LEFT JOIN assessment_types at ON a.type_id = at.type_id
                    WHERE e.assignment_id = ? AND e.status = 'Enrolled'
                    {condition}
                    GROUP BY s.student_id
                    ORDER BY s.last_name, s.first_name
                """
                df = pd.read_sql_query(query, conn, params=(assignment_id,))
                return {
                    'report_type': f'Class Summary - {report_type.title()}',
                    'class_data': df.to_dict('records'),
                    'generated_date': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error generating class summary: {e}")
            raise
    
    # UTILITY METHODS
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"school_reports_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    def export_report_to_excel(self, report_data: Dict, output_file: str):
        """Export report data to Excel file"""
        try:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Student info sheet
                student_df = pd.DataFrame([report_data['student_info']])
                student_df.to_excel(writer, sheet_name='Student Info', index=False)
                
                # Report card grades (if exists)
                if 'report_card_grades' in report_data:
                    report_df = pd.DataFrame(report_data['report_card_grades'])
                    report_df.to_excel(writer, sheet_name='Report Card', index=False)
                
                # Internal assessments (if exists)
                if 'internal_assessments' in report_data:
                    internal_df = pd.DataFrame(report_data['internal_assessments'])
                    internal_df.to_excel(writer, sheet_name='Internal Tracking', index=False)
                
                # Attendance summary (if exists)
                if 'attendance_summary' in report_data and report_data['attendance_summary']:
                    attendance_df = pd.DataFrame([report_data['attendance_summary']])
                    attendance_df.to_excel(writer, sheet_name='Attendance', index=False)
                
            self.logger.info(f"Report exported to {output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting report to Excel: {e}")
            raise
    
    def get_school_settings(self, school_id: int = None) -> Dict:
        """Get current school settings including academic periods - isolated by school_id"""
        try:
            if not school_id:
                # If no school_id provided, return blank settings
                self.logger.warning("get_school_settings called without school_id, returning blank settings")
                return {
                    'school_name': '',
                    'school_address': '',
                    'school_phone': '',
                    'school_email': '',
                    'pta_fund': '',
                    'sdf_fund': '',
                    'boarding_fee': '',
                    'next_term_begins': '',
                    'boys_uniform': '',
                    'girls_uniform': '',
                    'selected_term': '',
                    'selected_academic_year': '',
                    'academic_years': [],
                    'terms': [],
                    'academic_periods': []
                }
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic school settings - ONLY for this specific school_id
                cursor.execute("SELECT * FROM school_settings WHERE school_id = ? ORDER BY setting_id DESC LIMIT 1", (school_id,))
                
                row = cursor.fetchone()
                settings = {}
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    settings = dict(zip(columns, row))
                    # Ensure selected_term and selected_academic_year are strings (not None)
                    if settings.get('selected_term') is None:
                        settings['selected_term'] = ''
                    if settings.get('selected_academic_year') is None:
                        settings['selected_academic_year'] = ''
                else:
                    # If no settings exist for this school, return blank settings
                    settings = {
                        'school_name': '',
                        'school_address': '',
                        'school_phone': '',
                        'school_email': '',
                        'pta_fund': '',
                        'sdf_fund': '',
                        'boarding_fee': '',
                        'next_term_begins': '',
                        'boys_uniform': '',
                        'girls_uniform': '',
                        'selected_term': '',
                        'selected_academic_year': ''
                    }
                
                # Get academic periods (terms and years) - ONLY for this school_id
                academic_periods = self.get_academic_periods(school_id)
                
                # Extract unique academic years and terms
                academic_years = sorted(list(set([period['academic_year'] for period in academic_periods if period.get('academic_year')])))
                terms = sorted(list(set([period['period_name'] for period in academic_periods if period.get('period_name')])))
                
                settings['academic_years'] = academic_years
                settings['terms'] = terms
                settings['academic_periods'] = academic_periods
                
                return settings
                    
        except Exception as e:
            self.logger.error(f"Error retrieving school settings: {e}")
            return {
                'school_name': '',
                'school_address': '',
                'school_phone': '',
                'school_email': '',
                'pta_fund': '',
                'sdf_fund': '',
                'boarding_fee': '',
                'next_term_begins': '',
                'boys_uniform': '',
                'girls_uniform': '',
                'selected_term': '',
                'selected_academic_year': '',
                'academic_years': [],
                'terms': [],
                'academic_periods': []
            }
    
    def get_student_position_and_points(self, student_id: int, term: str, academic_year: str, form_level: int, school_id: int = None) -> Dict:
        """Calculate student position in class and aggregate points with tied ranking"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all students' data for ranking
                result = self.get_student_rankings(form_level, term, academic_year, school_id)
                rankings = result.get('rankings', [])
                total_students = result.get('total_students', 0)

                if not rankings:
                    return {
                        'position': 'N/A', 
                        'aggregate_points': 0, 
                        'total_students': total_students
                    }

                # Get student info
                student_info = self.get_student_by_id(student_id)
                if not student_info:
                    return {'position': 'N/A', 'aggregate_points': 0, 'total_students': total_students}
                
                student_name = f"{student_info['first_name']} {student_info['last_name']}"

                # Find the target student in rankings and get their position
                target_position = 'N/A'
                for ranking in rankings:
                    if ranking['name'] == student_name:
                        target_position = ranking.get('position', 'N/A')
                        break
                
                # Calculate aggregate points
                if school_id:
                    cursor.execute("""
                        SELECT COUNT(*) FROM student_marks 
                        WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                    """, (student_id, term, academic_year, school_id))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM student_marks 
                        WHERE student_id = ? AND term = ? AND academic_year = ?
                    """, (student_id, term, academic_year))
                
                subject_count = cursor.fetchone()[0]
                
                if subject_count <= 5:
                    aggregate_points = 54 if form_level >= 3 else 0
                else:
                    if school_id:
                        cursor.execute("""
                            SELECT mark FROM student_marks 
                            WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                            ORDER BY mark DESC LIMIT 6
                        """, (student_id, term, academic_year, school_id))
                    else:
                        cursor.execute("""
                            SELECT mark FROM student_marks 
                            WHERE student_id = ? AND term = ? AND academic_year = ?
                            ORDER BY mark DESC LIMIT 6
                        """, (student_id, term, academic_year))
                    
                    best_marks = [row[0] for row in cursor.fetchall()]
                    if form_level >= 3:
                        grade_points = []
                        for mark in best_marks:
                            grade = self.calculate_grade(mark, form_level)
                            grade_points.append(int(grade) if grade.isdigit() else 9)
                        aggregate_points = sum(grade_points)
                    else:
                        aggregate_points = sum(best_marks) if best_marks else 0
                
                return {
                    'position': target_position,
                    'aggregate_points': aggregate_points,
                    'total_students': total_students
                }
                
        except Exception as e:
            self.logger.error(f"Error calculating position and points: {e}")
            return {'position': 0, 'aggregate_points': 0, 'total_students': 0}
    
    def get_student_rankings(self, form_level: int, term: str, academic_year: str, school_id: int = None) -> Dict:
        """Get student rankings for a form level
        
        Returns:
            dict: {
                'rankings': list of student ranking dicts,
                'total_students': int,  # Total students who have marks (actual class size)
                'students_with_marks': int  # Students who sat for at least one exam
            }
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Use form-level specific pass threshold
                pass_threshold = 50 if form_level in [1, 2] else 40
                
                # Get ALL students who have marks for this form, term, and academic year
                if school_id:
                    cursor.execute("""
                        SELECT DISTINCT s.student_id, s.first_name, s.last_name 
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE sm.form_level = ? AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
                        ORDER BY s.first_name, s.last_name
                    """, (form_level, term, academic_year, school_id))
                else:
                    cursor.execute("""
                        SELECT DISTINCT s.student_id, s.first_name, s.last_name 
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE sm.form_level = ? AND sm.term = ? AND sm.academic_year = ?
                        ORDER BY s.first_name, s.last_name
                    """, (form_level, term, academic_year))
                
                all_students = cursor.fetchall()
                rankings = []
                
                # For each student, get their marks data
                for student_id, first_name, last_name in all_students:
                    # Get marks data for this student
                    if school_id:
                        cursor.execute(f"""
                            SELECT AVG(sm.mark) as average,
                                   COUNT(CASE WHEN sm.mark >= {pass_threshold} THEN 1 END) as subjects_passed,
                                   COUNT(sm.mark) as total_subjects
                            FROM student_marks sm
                            WHERE sm.student_id = ? AND sm.term = ? AND sm.academic_year = ? AND sm.school_id = ?
                        """, (student_id, term, academic_year, school_id))
                    else:
                        cursor.execute(f"""
                            SELECT AVG(sm.mark) as average,
                                   COUNT(CASE WHEN sm.mark >= {pass_threshold} THEN 1 END) as subjects_passed,
                                   COUNT(sm.mark) as total_subjects
                            FROM student_marks sm
                            WHERE sm.student_id = ? AND sm.term = ? AND sm.academic_year = ?
                        """, (student_id, term, academic_year))
                    
                    marks_data = cursor.fetchone()
                    average = marks_data[0] if marks_data and marks_data[0] is not None else 0
                    subjects_passed = marks_data[1] if marks_data else 0
                    total_subjects = marks_data[2] if marks_data else 0
                    
                    # Check if student wrote insufficient subjects (1-5)
                    if total_subjects <= 5:
                        if form_level <= 2:
                            # Forms 1&2: Give F grade
                            rankings.append({
                                'name': f"{first_name} {last_name}",
                                'average': 0,
                                'grade': 'F',
                                'subjects_passed': 0,
                                'status': 'FAIL',
                                'total_subjects': total_subjects
                            })
                        else:
                            # CRITICAL RULE: Forms 3&4 students with 1-5 subjects MUST get 54 aggregate points
                            rankings.append({
                                'name': f"{first_name} {last_name}",
                                'average': 0,
                                'aggregate_points': 54,
                                'subjects_passed': 0,
                                'status': 'FAIL',
                                'total_subjects': total_subjects
                            })
                        continue
                    
                    # Check if English is passed (school-specific)
                    if school_id:
                        cursor.execute("""
                            SELECT mark FROM student_marks 
                            WHERE student_id = ? AND subject = 'English' AND term = ? AND academic_year = ? AND school_id = ?
                        """, (student_id, term, academic_year, school_id))
                    else:
                        cursor.execute("""
                            SELECT mark FROM student_marks 
                            WHERE student_id = ? AND subject = 'English' AND term = ? AND academic_year = ?
                        """, (student_id, term, academic_year))
                    
                    english_result = cursor.fetchone()
                    english_mark = english_result[0] if english_result else 0
                    english_passed = self.is_english_passed(english_mark, form_level)
                    
                    # Determine status
                    status = self.determine_pass_fail_status(subjects_passed, english_passed)
                    
                    # Calculate aggregate points for Forms 3-4, keep grade for Forms 1-2
                    if form_level >= 3:
                        # Get best 6 marks for aggregate points calculation
                        cursor.execute("""
                            SELECT mark FROM student_marks 
                            WHERE student_id = ? AND term = ? AND academic_year = ?
                            ORDER BY mark DESC LIMIT 6
                        """, (student_id, term, academic_year))
                        best_marks = [row[0] for row in cursor.fetchall()]
                        
                        grade_points = []
                        for mark in best_marks:
                            grade = self.calculate_grade(mark, form_level)
                            grade_points.append(int(grade) if grade.isdigit() else 9)
                        aggregate_points = sum(grade_points)
                        
                        rankings.append({
                            'name': f"{first_name} {last_name}",
                            'average': average,
                            'aggregate_points': aggregate_points,
                            'subjects_passed': subjects_passed,
                            'status': status,
                            'total_subjects': total_subjects
                        })
                    else:
                        # For Forms 1&2: CRITICAL RULE - ANY failed student gets F grade
                        if status == 'FAIL':
                            grade = 'F'  # Failed students MUST get F grade
                        else:
                            # Passed students: find appropriate grade from their marks
                            cursor.execute("""
                                SELECT mark FROM student_marks 
                                WHERE student_id = ? AND term = ? AND academic_year = ?
                                ORDER BY mark DESC
                            """, (student_id, term, academic_year))
                            marks = [row[0] for row in cursor.fetchall()]
                            
                            # Find the most common passing grade
                            passing_grades = [self.calculate_grade(mark, form_level) for mark in marks if self.is_subject_passed(mark, form_level)]
                            if passing_grades:
                                grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                                for g in passing_grades:
                                    if g in grade_counts:
                                        grade_counts[g] += 1
                                
                                if any(grade_counts.values()):
                                    grade = max(grade_counts, key=grade_counts.get)
                                else:
                                    grade = 'D'  # Fallback for passed student
                            else:
                                grade = 'D'  # Fallback for passed student
                        
                        rankings.append({
                            'name': f"{first_name} {last_name}",
                            'average': average,
                            'grade': grade,
                            'subjects_passed': subjects_passed,
                            'status': status,
                            'total_subjects': total_subjects
                        })
                
                # Sort rankings based on form level
                if form_level >= 3:
                    # For Forms 3&4: Sort by status (PASS first), then aggregate points (LOWEST first)
                    rankings.sort(key=lambda x: (
                        x['status'] == 'FAIL',
                        x.get('aggregate_points', 999)
                    ))
                    
                    # Add tied positions for Forms 3&4
                    position = 1
                    for i, student in enumerate(rankings):
                        if i > 0:
                            prev_student = rankings[i-1]
                            # Same position if same status and same aggregate points
                            if (student['status'] == prev_student['status'] and 
                                student.get('aggregate_points') == prev_student.get('aggregate_points')):
                                student['position'] = prev_student['position']
                            else:
                                position = i + 1
                                student['position'] = position
                        else:
                            student['position'] = position
                else:
                    # For Forms 1&2: Sort by status (PASS first), then average marks (highest first)
                    rankings.sort(key=lambda x: (x['status'] == 'FAIL', -x['average']))
                    
                    # Add tied positions for Forms 1&2
                    position = 1
                    for i, student in enumerate(rankings):
                        if i > 0:
                            prev_student = rankings[i-1]
                            # Same position if same status and same average (rounded to 1 decimal)
                            if (student['status'] == prev_student['status'] and 
                                round(student['average'], 1) == round(prev_student['average'], 1)):
                                student['position'] = prev_student['position']
                            else:
                                position = i + 1
                                student['position'] = position
                        else:
                            student['position'] = position
                
                # Count students who sat for at least one exam
                students_with_marks = len(rankings)  # All students in rankings have marks
                
                # Return both rankings and counts
                return {
                    'rankings': rankings,
                    'total_students': len(rankings),  # Total students who have marks (actual class size)
                    'students_with_marks': students_with_marks  # Students who sat for at least one exam
                }
                
        except Exception as e:
            self.logger.error(f"Error getting student rankings: {e}")
            return {'rankings': [], 'total_students': 0, 'students_with_marks': 0}
    
    def get_top_performers(self, form_level: int, term: str, academic_year: str, limit: int = 10, school_id: int = None) -> List[Dict]:
        """Get top performing students"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if school_id:
                    cursor.execute("""
                        SELECT s.student_id, s.first_name, s.last_name, AVG(sm.mark) as average
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
                        GROUP BY s.student_id
                        HAVING COUNT(sm.mark_id) >= 6
                        ORDER BY average DESC
                        LIMIT ?
                    """, (form_level, term, academic_year, school_id, limit))
                else:
                    cursor.execute("""
                        SELECT s.student_id, s.first_name, s.last_name, AVG(sm.mark) as average
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ?
                        GROUP BY s.student_id
                        HAVING COUNT(sm.mark_id) >= 6
                        ORDER BY average DESC
                        LIMIT ?
                    """, (form_level, term, academic_year, limit))
                
                performers = []
                for row in cursor.fetchall():
                    student_id, first_name, last_name, average = row
                    grade = self.calculate_grade(int(average), form_level)
                    
                    performers.append({
                        'name': f"{first_name} {last_name}",
                        'average': round(average, 1),
                        'grade': grade if form_level <= 2 else None,
                        'aggregate_points': self.calculate_aggregate_points_for_student(student_id, term, academic_year, form_level) if form_level >= 3 else None
                    })
                
                return performers
        except Exception as e:
            self.logger.error(f"Error getting top performers: {e}")
            return []
    
    def get_subject_analysis(self, form_level: int, term: str, academic_year: str, school_id: int = None) -> Dict:
        """Get subject performance analysis"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if school_id:
                    cursor.execute("""
                        SELECT sm.subject, AVG(sm.mark) as avg_mark, COUNT(*) as student_count,
                               MIN(sm.mark) as min_mark, MAX(sm.mark) as max_mark
                        FROM student_marks sm
                        JOIN students s ON sm.student_id = s.student_id
                        WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
                        GROUP BY sm.subject
                        ORDER BY avg_mark DESC
                    """, (form_level, term, academic_year, school_id))
                else:
                    cursor.execute("""
                        SELECT sm.subject, AVG(sm.mark) as avg_mark, COUNT(*) as student_count,
                               MIN(sm.mark) as min_mark, MAX(sm.mark) as max_mark
                        FROM student_marks sm
                        JOIN students s ON sm.student_id = s.student_id
                        WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ?
                        GROUP BY sm.subject
                        ORDER BY avg_mark DESC
                    """, (form_level, term, academic_year))
                
                subjects = []
                for row in cursor.fetchall():
                    subject, avg_mark, student_count, min_mark, max_mark = row
                    
                    # Calculate pass rate
                    pass_threshold = 50 if form_level <= 2 else 40
                    if school_id:
                        cursor.execute("""
                            SELECT COUNT(*) FROM student_marks sm
                            JOIN students s ON sm.student_id = s.student_id
                            WHERE sm.subject = ? AND s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? 
                            AND sm.mark >= ? AND s.school_id = ?
                        """, (subject, form_level, term, academic_year, pass_threshold, school_id))
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) FROM student_marks sm
                            JOIN students s ON sm.student_id = s.student_id
                            WHERE sm.subject = ? AND s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? 
                            AND sm.mark >= ?
                        """, (subject, form_level, term, academic_year, pass_threshold))
                    
                    passed_count = cursor.fetchone()[0]
                    pass_rate = (passed_count / student_count * 100) if student_count > 0 else 0
                    
                    subjects.append({
                        'subject': subject,
                        'average': round(avg_mark, 1),
                        'student_count': student_count,
                        'min_mark': min_mark,
                        'max_mark': max_mark,
                        'pass_rate': round(pass_rate, 1)
                    })
                
                return {
                    'subjects': subjects,
                    'total_subjects': len(subjects)
                }
        except Exception as e:
            self.logger.error(f"Error getting subject analysis: {e}")
            return {'subjects': [], 'total_subjects': 0}
    
    def get_top_performers_by_category(self, category: str, form_level: int, term: str, academic_year: str, school_id: int = None) -> List[Dict]:

        try:
            if category == 'overall':
                # For overall, get students with best performance
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if form_level >= 3:
                        # For Forms 3&4: Sort by lowest aggregate points (best performance)
                        if school_id:
                            cursor.execute("""
                                SELECT s.student_id, s.first_name, s.last_name, AVG(sm.mark) as average
                                FROM students s
                                JOIN student_marks sm ON s.student_id = sm.student_id
                                WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
                                GROUP BY s.student_id
                                HAVING COUNT(sm.mark_id) >= 6
                            """, (form_level, term, academic_year, school_id))
                        else:
                            cursor.execute("""
                                SELECT s.student_id, s.first_name, s.last_name, AVG(sm.mark) as average
                                FROM students s
                                JOIN student_marks sm ON s.student_id = sm.student_id
                                WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ?
                                GROUP BY s.student_id
                                HAVING COUNT(sm.mark_id) >= 6
                            """, (form_level, term, academic_year))
                        
                        performers = []
                        for row in cursor.fetchall():
                            student_id, first_name, last_name, average = row
                            aggregate_points = self.calculate_aggregate_points_for_student(student_id, term, academic_year, form_level)
                            
                            performers.append({
                                'name': f"{first_name} {last_name}",
                                'average': round(average, 1),
                                'aggregate_points': aggregate_points,
                                'excellence_area': 'Overall Performance'
                            })
                        
                        # Sort by lowest aggregate points (best performance) - CRITICAL RULE for Forms 3&4
                        performers.sort(key=lambda x: x.get('aggregate_points', 999))
                        return performers[:10]
                    else:
                        # For Forms 1&2: Sort by highest average
                        if school_id:
                            cursor.execute("""
                                SELECT s.student_id, s.first_name, s.last_name, AVG(sm.mark) as average
                                FROM students s
                                JOIN student_marks sm ON s.student_id = sm.student_id
                                WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
                                GROUP BY s.student_id
                                HAVING COUNT(sm.mark_id) >= 6
                                ORDER BY average DESC
                                LIMIT 10
                            """, (form_level, term, academic_year, school_id))
                        else:
                            cursor.execute("""
                                SELECT s.student_id, s.first_name, s.last_name, AVG(sm.mark) as average
                                FROM students s
                                JOIN student_marks sm ON s.student_id = sm.student_id
                                WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ?
                                GROUP BY s.student_id
                                HAVING COUNT(sm.mark_id) >= 6
                                ORDER BY average DESC
                                LIMIT 10
                            """, (form_level, term, academic_year))
                        
                        performers = []
                        for row in cursor.fetchall():
                            student_id, first_name, last_name, average = row
                            grade = self.calculate_grade(int(average), form_level)
                            
                            performers.append({
                                'name': f"{first_name} {last_name}",
                                'average': round(average, 1),
                                'grade': grade,
                                'excellence_area': 'Overall Performance'
                            })
                        
                        return performers
            
            # Define subject groups for department-based performance (user-specified groups)
            subject_groups = {
                # Sciences include the full science list including Business Studies and Home Economics
                'sciences': ['Agriculture', 'Biology', 'Chemistry', 'Physics', 'Mathematics', 'Business Studies', 'Home Economics'],
                'humanities': ['Bible Knowledge', 'Geography', 'History', 'Life Skills/SOS'],
                # Languages are Chichewa and English; ranking based on total marks across both
                'languages': ['English', 'Chichewa']
            }
            
            if category not in subject_groups:
                return []
            
            subjects = subject_groups[category]
            placeholders = ','.join(['?' for _ in subjects])
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # For department-based performance we calculate the TOTAL marks across the group's subjects
                # and also provide the department average (total / number of subjects taken) so the frontend
                # can display both a total and an average percentage.
                if school_id:
                    cursor.execute(f"""
                        SELECT s.student_id, s.first_name, s.last_name, 
                               SUM(sm.mark) as department_total,
                               COUNT(DISTINCT sm.subject) as subjects_taken
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ? AND s.school_id = ?
                        AND sm.subject IN ({placeholders})
                        GROUP BY s.student_id
                        HAVING subjects_taken >= 1
                        ORDER BY department_total DESC
                        LIMIT 10
                    """, (form_level, term, academic_year, school_id, *subjects))
                else:
                    cursor.execute(f"""
                        SELECT s.student_id, s.first_name, s.last_name, 
                               SUM(sm.mark) as department_total,
                               COUNT(DISTINCT sm.subject) as subjects_taken
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE s.grade_level = ? AND sm.term = ? AND sm.academic_year = ?
                        AND sm.subject IN ({placeholders})
                        GROUP BY s.student_id
                        HAVING subjects_taken >= 1
                        ORDER BY department_total DESC
                        LIMIT 10
                    """, (form_level, term, academic_year, *subjects))
                
                performers = []
                for row in cursor.fetchall():
                    student_id, first_name, last_name, department_total, subjects_taken = row
                    
                    # Compute department average (percentage) for coloring and display
                    department_avg = (department_total / subjects_taken) if subjects_taken > 0 else 0
                    
                    # Get student's overall average across all subjects
                    if school_id:
                        cursor.execute("""
                            SELECT AVG(mark) FROM student_marks 
                            WHERE student_id = ? AND term = ? AND academic_year = ? AND school_id = ?
                        """, (student_id, term, academic_year, school_id))
                    else:
                        cursor.execute("""
                            SELECT AVG(mark) FROM student_marks 
                            WHERE student_id = ? AND term = ? AND academic_year = ?
                        """, (student_id, term, academic_year))
                    overall_avg_result = cursor.fetchone()
                    overall_average = overall_avg_result[0] if overall_avg_result and overall_avg_result[0] else 0
                    
                    performers.append({
                        'name': f"{first_name} {last_name}",
                        'average': round(overall_average, 1),  # Overall average in %
                        'department_total': int(department_total),
                        'department_average': round(department_avg, 1),
                        'subjects_taken': int(subjects_taken),
                        'excellence_area': f"{category.title()} Department"
                    })
                
                # Sort by department total (highest first)
                performers.sort(key=lambda x: x['department_total'], reverse=True)
                return performers
                
        except Exception as e:
            self.logger.error(f"Error getting top performers: {e}")
            return []
    
    def calculate_aggregate_points_for_student(self, student_id: int, term: str, academic_year: str, form_level: int) -> int:
        """Calculate aggregate points for Forms 3&4 (sum of best 6 subjects converted to MSCE grade points)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mark FROM student_marks 
                    WHERE student_id = ? AND term = ? AND academic_year = ?
                    ORDER BY mark DESC
                    LIMIT 6
                """, (student_id, term, academic_year))
                
                marks = [row[0] for row in cursor.fetchall()]
                if len(marks) < 6:
                    return None  # Not enough subjects
                
                # Convert marks to MSCE grade points and sum them
                aggregate_points = 0
                for mark in marks:
                    grade = self.calculate_grade(mark, form_level)
                    if grade.isdigit():
                        aggregate_points += int(grade)
                    else:
                        aggregate_points += 9  # Default for non-numeric grades
                
                return aggregate_points
                
        except Exception as e:
            self.logger.error(f"Error calculating aggregate points: {e}")
            return None

    def get_subject_teachers(self, form_level: int = None, school_id: int = None) -> Dict[str, str]:
        """Get subject teachers for specific form level and school"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if form_level and school_id:
                    cursor.execute("SELECT subject, teacher_name FROM subject_teachers WHERE form_level = ? AND school_id = ?", (form_level, school_id))
                elif form_level:
                    cursor.execute("SELECT subject, teacher_name FROM subject_teachers WHERE form_level = ?", (form_level,))
                elif school_id:
                    cursor.execute("SELECT subject, teacher_name FROM subject_teachers WHERE school_id = ?", (school_id,))
                else:
                    cursor.execute("SELECT subject, teacher_name FROM subject_teachers")
                return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            self.logger.error(f"Error getting subject teachers: {e}")
            return {}
    
    def update_subject_teacher(self, subject: str, form_level: int, teacher_name: str, school_id: int = None):
        """Update teacher for a subject in specific form and school"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO subject_teachers (subject, form_level, teacher_name, updated_date, school_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (subject, form_level, teacher_name, datetime.now().isoformat(), school_id))
                self.logger.info(f"Updated teacher for {subject} Form {form_level}: {teacher_name}")
        except Exception as e:
            self.logger.error(f"Error updating subject teacher: {e}")
            raise

    def delete_subject_teacher(self, subject: str, form_level: int, school_id: int = None) -> bool:
        """Delete a subject teacher mapping for a form and school. Returns True if a row was deleted."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if school_id is not None:
                    cursor.execute("DELETE FROM subject_teachers WHERE subject = ? AND form_level = ? AND school_id = ?", (subject, form_level, school_id))
                else:
                    cursor.execute("DELETE FROM subject_teachers WHERE subject = ? AND form_level = ?", (subject, form_level))
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error deleting subject teacher: {e}")
            raise
    
    def get_subject_position(self, student_id: int, subject: str, term: str, academic_year: str, form_level: int, school_id: int = None) -> str:
        """Get student position in a specific subject with tied ranking (format: position/total)
        
        Returns:
            str: Position in format "position/total" where total is the number of students who have marks for this subject
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get students who sat for this subject
                if school_id:
                    cursor.execute("""
                        SELECT DISTINCT s.student_id, s.first_name, s.last_name, sm.mark
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE sm.form_level = ? 
                          AND sm.subject = ? 
                          AND sm.term = ? 
                          AND sm.academic_year = ?
                          AND sm.school_id = ?
                        ORDER BY sm.mark DESC, s.first_name, s.last_name
                    """, (form_level, subject, term, academic_year, school_id))
                else:
                    cursor.execute("""
                        SELECT DISTINCT s.student_id, s.first_name, s.last_name, sm.mark
                        FROM students s
                        JOIN student_marks sm ON s.student_id = sm.student_id
                        WHERE sm.form_level = ? 
                          AND sm.subject = ? 
                          AND sm.term = ? 
                          AND sm.academic_year = ?
                        ORDER BY sm.mark DESC, s.first_name, s.last_name
                    """, (form_level, subject, term, academic_year))
                
                results = cursor.fetchall()
                
                if not results:
                    return "0/0"
                
                total_students = len(results)
                
                # Calculate positions with tie handling
                current_rank = 1
                prev_mark = None
                
                for i, (sid, first_name, last_name, mark) in enumerate(results):
                    # If this mark is different from previous, update current_rank
                    if i > 0 and mark != prev_mark:
                        current_rank = i + 1
                    
                    # If this is our target student, return their position
                    if sid == student_id:
                        return f"{current_rank}/{total_students}"
                    
                    prev_mark = mark
                
                # If we get here, the student didn't sit for this subject
                return f"0/{total_students}"
                
        except Exception as e:
            self.logger.error(f"Error getting subject position: {e}")
            return "0/0"
    
    def get_teacher_comment(self, grade: str) -> str:
        """Get teacher comment based on grade for Forms 3&4"""
        grade_comments = {
            '1': 'Distinction',
            '2': 'Distinction', 
            '3': 'Strong Credit',
            '4': 'Credit',
            '5': 'Credit',
            '6': 'Credit',
            '7': 'Pass',
            '8': 'Mere Pass',
            '9': 'Fail',
            'A': 'Excellent',
            'B': 'Very Good',
            'C': 'Good', 
            'D': 'Average',
            'F': 'Fail'
        }
        return grade_comments.get(grade, 'Needs Improvement')
    
    def update_school_settings(self, settings_data: Dict, school_id: int = None):
        """Update school settings in database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract selected term and academic year from the data
                # If terms/academic_years are arrays, use the first element as selected
                selected_term = settings_data.get('selected_term', '')
                if not selected_term and 'terms' in settings_data:
                    terms_list = settings_data.get('terms', [])
                    if isinstance(terms_list, list) and len(terms_list) > 0:
                        selected_term = terms_list[0]
                
                selected_academic_year = settings_data.get('selected_academic_year', '')
                if not selected_academic_year and 'academic_years' in settings_data:
                    years_list = settings_data.get('academic_years', [])
                    if isinstance(years_list, list) and len(years_list) > 0:
                        selected_academic_year = years_list[0]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO school_settings 
                    (school_name, school_address, school_phone, school_email, 
                     pta_fund, sdf_fund, boarding_fee, next_term_begins, boys_uniform, girls_uniform, 
                     selected_term, selected_academic_year, updated_date, school_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings_data.get('school_name'),
                    settings_data.get('school_address'),
                    settings_data.get('school_phone'),
                    settings_data.get('school_email'),
                    settings_data.get('pta_fund'),
                    settings_data.get('sdf_fund'),
                    settings_data.get('boarding_fee'),
                    settings_data.get('next_term_begins'),
                    settings_data.get('boys_uniform'),
                    settings_data.get('girls_uniform'),
                    selected_term,
                    selected_academic_year,
                    datetime.now().isoformat(),
                    school_id
                ))
                
                self.logger.info("School settings updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating school settings: {e}")
            raise
    
    def update_academic_periods(self, academic_years: List[str], terms: List[str], school_id: int = None):
        """Update academic periods without affecting existing grades"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check which columns exist in academic_periods table
                cursor.execute("PRAGMA table_info(academic_periods)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Add created_date column if it doesn't exist
                if 'created_date' not in columns:
                    try:
                        cursor.execute("ALTER TABLE academic_periods ADD COLUMN created_date TEXT DEFAULT CURRENT_TIMESTAMP")
                        self.logger.info("Added created_date column to academic_periods table")
                        columns.append('created_date')  # Update our list
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e):
                            self.logger.error(f"Error adding created_date column: {e}")
                
                # Add school_id column if it doesn't exist
                if 'school_id' not in columns:
                    try:
                        cursor.execute("ALTER TABLE academic_periods ADD COLUMN school_id INTEGER")
                        self.logger.info("Added school_id column to academic_periods table")
                        columns.append('school_id')  # Update our list
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e):
                            self.logger.error(f"Error adding school_id column: {e}")
                
                # Build insert statement based on available columns
                has_school_id = 'school_id' in columns
                has_created_date = 'created_date' in columns
                
                for academic_year in academic_years:
                    for term in terms:
                        if has_school_id and has_created_date:
                            # Both columns exist
                            cursor.execute("""
                                INSERT OR IGNORE INTO academic_periods 
                                (academic_year, period_name, school_id, created_date)
                                VALUES (?, ?, ?, ?)
                            """, (academic_year.strip(), term.strip(), school_id, datetime.now().isoformat()))
                        elif has_school_id:
                            # Only school_id exists
                            cursor.execute("""
                                INSERT OR IGNORE INTO academic_periods 
                                (academic_year, period_name, school_id)
                                VALUES (?, ?, ?)
                            """, (academic_year.strip(), term.strip(), school_id))
                        elif has_created_date:
                            # Only created_date exists
                            cursor.execute("""
                                INSERT OR IGNORE INTO academic_periods 
                                (academic_year, period_name, created_date)
                                VALUES (?, ?, ?)
                            """, (academic_year.strip(), term.strip(), datetime.now().isoformat()))
                        else:
                            # Neither column exists (old schema)
                            cursor.execute("""
                                INSERT OR IGNORE INTO academic_periods 
                                (academic_year, period_name)
                                VALUES (?, ?)
                            """, (academic_year.strip(), term.strip()))
                
                self.logger.info(f"Updated academic periods")
        except Exception as e:
            self.logger.error(f"Error updating academic periods: {e}")
            raise
    
    def get_academic_periods(self, school_id: int = None) -> List[Dict]:
        """Get all academic periods for a specific school - isolated by school_id"""
        try:
            if not school_id:
                # If no school_id provided, return empty list (no periods from other schools)
                return []
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # ONLY get periods for this specific school_id (no OR school_id IS NULL)
                cursor.execute("""
                    SELECT * FROM academic_periods 
                    WHERE school_id = ?
                    ORDER BY academic_year DESC, period_name
                """, (school_id,))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Error retrieving academic periods: {e}")
            return []
    
    def get_available_terms_and_years(self, school_id: int = None) -> Dict:
        """Get available terms and academic years that have actual grade data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get terms and years that actually have grade data - ONLY for this school_id
                if school_id:
                    cursor.execute("""
                        SELECT DISTINCT term, academic_year 
                        FROM student_marks sm
                        JOIN students s ON sm.student_id = s.student_id
                        WHERE s.school_id = ?
                        ORDER BY academic_year DESC, term
                    """, (school_id,))
                else:
                    # If no school_id provided, return empty (no data from other schools)
                    return {
                        'all_terms': [],
                        'all_years': [],
                        'terms_with_data': [],
                        'years_with_data': []
                    }
                
                rows = cursor.fetchall()
                
                # Extract unique terms and years
                terms_with_data = sorted(list(set([row[0] for row in rows])))
                years_with_data = sorted(list(set([row[1] for row in rows])), reverse=True)
                
                # Get all configured periods
                all_periods = self.get_academic_periods(school_id)
                all_terms = sorted(list(set([period['period_name'] for period in all_periods])))
                all_years = sorted(list(set([period['academic_year'] for period in all_periods])), reverse=True)
                
                # Fallback to defaults if no periods configured
                if not all_terms:
                    all_terms = ['Term 1', 'Term 2', 'Term 3']
                if not all_years:
                    all_years = [f'{y}-{y+1}' for y in range(2020, 2031)]
                
                return {
                    'all_terms': all_terms,
                    'all_years': all_years,
                    'terms_with_data': terms_with_data,
                    'years_with_data': years_with_data,
                    'periods_with_data': [{'term': row[0], 'year': row[1]} for row in rows]
                }
        except Exception as e:
            self.logger.error(f"Error getting available terms and years: {e}")
            return {
                'all_terms': ['Term 1', 'Term 2', 'Term 3'],
                'all_years': [f'{y}-{y+1}' for y in range(2020, 2031)],
                'terms_with_data': [],
                'years_with_data': [],
                'periods_with_data': []
            }
    
    def get_school_fees(self) -> Dict:
        """Get school fee information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT pta_fund, sdf_fund, boarding_fee FROM school_fees ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                
                if row:
                    return {
                        'pta_fund': row[0],
                        'sdf_fund': row[1],
                        'boarding_fee': row[2]
                    }
                else:
                    return {
                        'pta_fund': 'MK 50,000',
                        'sdf_fund': 'MK 30,000',
                        'boarding_fee': 'MK 150,000'
                    }
        except Exception as e:
            self.logger.error(f"Error getting school fees: {e}")
            return {
                'pta_fund': 'MK 50,000',
                'sdf_fund': 'MK 30,000',
                'boarding_fee': 'MK 150,000'
            }
    
    def delete_student_marks(self, student_id: int, school_id: int = None):
        """Delete all marks for a student"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if school_id:
                    cursor.execute("DELETE FROM student_marks WHERE student_id = ? AND (school_id = ? OR school_id IS NULL)", (student_id, school_id))
                else:
                    cursor.execute("DELETE FROM student_marks WHERE student_id = ?", (student_id,))
                self.logger.info(f"Deleted all marks for student {student_id}")
        except Exception as e:
            self.logger.error(f"Error deleting student marks: {e}")
            raise
    
    def delete_student(self, student_id: int, school_id: int = None):
        """Delete a student record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if school_id:
                    cursor.execute("DELETE FROM students WHERE student_id = ? AND (school_id = ? OR school_id IS NULL)", (student_id, school_id))
                else:
                    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted student {student_id}")
                    return True
                else:
                    self.logger.warning(f"No student found with ID {student_id} for deletion")
                    return False
        except Exception as e:
            self.logger.error(f"Error deleting student: {e}")
            raise
    
    def update_student_name(self, student_id: int, first_name: str, last_name: str, school_id: int = None):
        """Update a student's name"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if school_id:
                    cursor.execute("""
                        UPDATE students 
                        SET first_name = ?, last_name = ? 
                        WHERE student_id = ? AND (school_id = ? OR school_id IS NULL)
                    """, (first_name, last_name, student_id, school_id))
                else:
                    cursor.execute("""
                        UPDATE students 
                        SET first_name = ?, last_name = ? 
                        WHERE student_id = ?
                    """, (first_name, last_name, student_id))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated student {student_id} name to {first_name} {last_name}")
                    return True
                else:
                    self.logger.warning(f"No student found with ID {student_id} for name update")
                    return False
        except Exception as e:
            self.logger.error(f"Error updating student name: {e}")
            raise
    
    def authenticate_school(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate school login"""
        try:
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT school_id, school_name, username, status, subscription_status, days_remaining, must_change_password
                    FROM schools 
                    WHERE username = ? AND password_hash = ? AND status = 'active'
                """, (username, password_hash))
                
                row = cursor.fetchone()
                if row:
                    # Update last login
                    cursor.execute("""
                        UPDATE schools SET last_login = ? WHERE school_id = ?
                    """, (datetime.now().isoformat(), row[0]))
                    
                    return {
                        'school_id': row[0],
                        'school_name': row[1],
                        'username': row[2],
                        'status': row[3],
                        'subscription_status': row[4],
                        'days_remaining': row[5],
                        'must_change_password': bool(row[6])
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error authenticating school: {e}")
            return None
    
    def add_school(self, school_data: Dict) -> int:
        """Add new school (Developer only)"""
        try:
            import hashlib
            from datetime import datetime, timedelta
            password_hash = hashlib.sha256(school_data['password'].encode()).hexdigest()
            
            # Set trial period (90 days)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=90)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if subscription columns exist, if not add them
                cursor.execute("PRAGMA table_info(schools)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Newly created schools receive a temporary OTP password which they must change on first login
                if 'subscription_status' in columns:
                    cursor.execute("""
                        INSERT INTO schools (school_name, username, password_hash, subscription_status, 
                                           subscription_start_date, subscription_end_date, days_remaining, must_change_password)
                        VALUES (?, ?, ?, 'trial', ?, ?, 90, 1)
                    """, (school_data['school_name'], school_data['username'], password_hash, 
                          start_date.isoformat(), end_date.isoformat()))
                else:
                    cursor.execute("""
                        INSERT INTO schools (school_name, username, password_hash, must_change_password)
                        VALUES (?, ?, ?, 1)
                    """, (school_data['school_name'], school_data['username'], password_hash))
                
                school_id = cursor.lastrowid
                self.logger.info(f"Added school: {school_data['school_name']} (ID: {school_id})")
                return school_id
        except Exception as e:
            self.logger.error(f"Error adding school: {e}")
            raise

    def update_school_password(self, school_id: int, new_password: str):
        """Update school's password and clear must_change_password flag"""
        try:
            import hashlib
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE schools SET password_hash = ?, must_change_password = 0 WHERE school_id = ?
                """, (new_hash, school_id))
                self.logger.info(f"Updated password for school {school_id}")
        except Exception as e:
            self.logger.error(f"Error updating school password: {e}")
            raise

    def reset_school_credentials(self, school_id: int, new_password: str):
        """Reset school's credentials to a temporary password and force change on next login"""
        try:
            import hashlib
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE schools SET password_hash = ?, must_change_password = 1 WHERE school_id = ?
                """, (new_hash, school_id))
                self.logger.info(f"Reset credentials for school {school_id}")
        except Exception as e:
            self.logger.error(f"Error resetting school credentials: {e}")
            raise
    
    def get_all_schools(self) -> List[Dict]:
        """Get all schools (Developer only)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT school_id, school_name, username, status, subscription_status, 
                           subscription_end_date, days_remaining, created_date, last_login
                    FROM schools ORDER BY school_name
                """)
                
                schools = []
                for row in cursor.fetchall():
                    schools.append({
                        'school_id': row[0],
                        'school_name': row[1],
                        'username': row[2],
                        'status': row[3],
                        'subscription_status': row[4],
                        'subscription_end_date': row[5],
                        'days_remaining': row[6],
                        'created_date': row[7],
                        'last_login': row[8]
                    })
                return schools
        except Exception as e:
            self.logger.error(f"Error getting schools: {e}")
            return []
    
    def update_school_status(self, school_id: int, status: str):
        """Update school status (Developer only)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE schools SET status = ? WHERE school_id = ?
                """, (status, school_id))
                self.logger.info(f"Updated school {school_id} status to {status}")
        except Exception as e:
            self.logger.error(f"Error updating school status: {e}")
            raise
    
    def grant_subscription(self, school_id: int, months: int = 12):
        """Grant subscription to school (Developer only)"""
        try:
            from datetime import datetime, timedelta
            start_date = datetime.now()
            end_date = start_date + timedelta(days=months * 30)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE schools 
                    SET subscription_status = 'paid', 
                        subscription_start_date = ?, 
                        subscription_end_date = ?,
                        days_remaining = ?
                    WHERE school_id = ?
                """, (start_date.isoformat(), end_date.isoformat(), months * 30, school_id))
                
                self.logger.info(f"Granted {months} months subscription to school {school_id}")
        except Exception as e:
            self.logger.error(f"Error granting subscription: {e}")
            raise
    
    def send_subscription_reminder(self, school_id: int = None):
        """Send subscription reminder to schools"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if school_id:
                    schools_query = "SELECT school_id, school_name, days_remaining FROM schools WHERE school_id = ?"
                    cursor.execute(schools_query, (school_id,))
                else:
                    schools_query = "SELECT school_id, school_name, days_remaining FROM schools WHERE subscription_status = 'trial' OR days_remaining <= 30"
                    cursor.execute(schools_query)
                
                schools = cursor.fetchall()
                
                for school_id, school_name, days_remaining in schools:
                    message = f"Dear {school_name}, your subscription expires in {days_remaining} days. Please renew to continue using the system."
                    
                    cursor.execute("""
                        INSERT INTO subscription_notifications (school_id, message, notification_type)
                        VALUES (?, ?, 'reminder')
                    """, (school_id, message))
                
                self.logger.info(f"Sent subscription reminders to {len(schools)} schools")
                return len(schools)
        except Exception as e:
            self.logger.error(f"Error sending subscription reminders: {e}")
            return 0
    
    def get_schools_to_lock(self) -> List[Dict]:
        """Get schools that should be locked for non-payment"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT school_id, school_name, username, days_remaining, subscription_end_date
                    FROM schools 
                    WHERE days_remaining <= 0 AND status = 'active'
                    ORDER BY school_name
                """)
                
                schools = []
                for row in cursor.fetchall():
                    schools.append({
                        'school_id': row[0],
                        'school_name': row[1],
                        'username': row[2],
                        'days_remaining': row[3],
                        'subscription_end_date': row[4]
                    })
                return schools
        except Exception as e:
            self.logger.error(f"Error getting schools to lock: {e}")
            return []
    
    def update_days_remaining(self):
        """Update days remaining for all schools"""
        try:
            from datetime import datetime
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT school_id, subscription_end_date FROM schools 
                    WHERE subscription_end_date IS NOT NULL
                """)
                
                schools = cursor.fetchall()
                for school_id, end_date_str in schools:
                    try:
                        end_date = datetime.fromisoformat(end_date_str)
                        days_remaining = (end_date - datetime.now()).days
                        
                        cursor.execute("""
                            UPDATE schools SET days_remaining = ? WHERE school_id = ?
                        """, (max(0, days_remaining), school_id))
                    except:
                        continue
                
                self.logger.info(f"Updated days remaining for {len(schools)} schools")
        except Exception as e:
            self.logger.error(f"Error updating days remaining: {e}")


def main():
    """Main function for testing the database operations"""
    print("School Reporting Database System")
    print("=" * 50)
    print("Features:")
    print("- Official Report Cards (Tests, Exams only)")
    print("- Internal Tracking (Quiz, Homework, Projects, etc.)")
    print("- Comprehensive Teacher Reports")
    print("=" * 50)
    
    # Initialize database
    db = SchoolDatabase()
    
    # Display assessment types
    print("\n📊 REPORT CARD Assessment Types:")
    report_types = db.get_report_card_assessment_types()
    for rt in report_types:
        print(f"  • {rt['type_name']}: {rt['description']}")
    
    print("\n📋 INTERNAL TRACKING Assessment Types:")
    internal_types = db.get_internal_tracking_assessment_types()
    for it in internal_types:
        print(f"  • {it['type_name']}: {it['description']}")
    
    print("\nDatabase system ready for use!")
    print("Use the methods to:")
    print("- generate_official_report_card() for student report cards")
    print("- generate_internal_tracking_report() for teacher tracking")
    print("- generate_comprehensive_teacher_report() for complete view")


if __name__ == "__main__":
    main()
