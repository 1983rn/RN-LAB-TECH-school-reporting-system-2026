#!/usr/bin/env python3
"""
Multi-User Management System for Schools
Allows multiple users from same school to work concurrently
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

class SchoolUserManager:
    """Manages multiple users for the same school"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def create_school_users_table(self):
        """Create users table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS school_users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        school_id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        email TEXT,
                        role TEXT DEFAULT 'teacher',
                        assigned_forms TEXT DEFAULT '[]',
                        is_active BOOLEAN DEFAULT 1,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        last_login TEXT,
                        session_token TEXT,
                        session_expires TEXT,
                        FOREIGN KEY (school_id) REFERENCES schools (school_id),
                        UNIQUE(username, school_id)
                    )
                """)
                
                # Create user activity log table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_activity_log (
                        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        activity_type TEXT NOT NULL,
                        form_level INTEGER,
                        details TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES school_users (user_id)
                    )
                """)
                
                conn.commit()
                self.logger.info("School users tables created successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating users tables: {e}")
            return False
    
    def create_school_user(self, school_id: int, username: str, password: str, 
                         full_name: str, email: str = None, role: str = 'teacher',
                         assigned_forms: List[int] = None) -> bool:
        """Create a new user for a school"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if username already exists for this school
                cursor.execute("""
                    SELECT COUNT(*) FROM school_users 
                    WHERE username = ? AND school_id = ?
                """, (username, school_id))
                
                if cursor.fetchone()[0] > 0:
                    return False  # Username already exists
                
                # Hash password
                password_hash = self._hash_password(password)
                
                # Convert assigned forms to JSON string
                forms_json = str(assigned_forms) if assigned_forms else '[]'
                
                cursor.execute("""
                    INSERT INTO school_users 
                    (school_id, username, password_hash, full_name, email, role, assigned_forms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (school_id, username, password_hash, full_name, email, role, forms_json))
                
                conn.commit()
                self.logger.info(f"Created user {username} for school {school_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return False
    
    def authenticate_school_user(self, username: str, password: str, school_id: int) -> Optional[Dict]:
        """Authenticate a school user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, school_id, username, password_hash, full_name, 
                           email, role, assigned_forms, is_active
                    FROM school_users 
                    WHERE username = ? AND school_id = ? AND is_active = 1
                """, (username, school_id))
                
                user_data = cursor.fetchone()
                
                if not user_data:
                    return None
                
                # Verify password
                if not self._verify_password(password, user_data[3]):
                    return None
                
                # Update last login
                cursor.execute("""
                    UPDATE school_users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                """, (user_data[0],))
                
                conn.commit()
                
                return {
                    'user_id': user_data[0],
                    'school_id': user_data[1],
                    'username': user_data[2],
                    'full_name': user_data[4],
                    'email': user_data[5],
                    'role': user_data[6],
                    'assigned_forms': eval(user_data[7]),  # Convert JSON string back to list
                    'is_active': user_data[8]
                }
                
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_school_users(self, school_id: int) -> List[Dict]:
        """Get all users for a school"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, username, full_name, email, role, 
                           assigned_forms, is_active, created_date, last_login
                    FROM school_users 
                    WHERE school_id = ?
                    ORDER BY created_date DESC
                """, (school_id,))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'full_name': row[2],
                        'email': row[3],
                        'role': row[4],
                        'assigned_forms': eval(row[5]),  # Convert JSON string back to list
                        'is_active': row[6],
                        'created_date': row[7],
                        'last_login': row[8]
                    })
                
                return users
                
        except Exception as e:
            self.logger.error(f"Error getting users: {e}")
            return []
    
    def update_user_assignment(self, user_id: int, assigned_forms: List[int]) -> bool:
        """Update user's form assignments"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                forms_json = str(assigned_forms)
                cursor.execute("""
                    UPDATE school_users 
                    SET assigned_forms = ?
                    WHERE user_id = ?
                """, (forms_json, user_id))
                
                conn.commit()
                self.logger.info(f"Updated form assignments for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating user assignment: {e}")
            return False
    
    def log_user_activity(self, user_id: int, activity_type: str, 
                       form_level: int = None, details: str = None) -> bool:
        """Log user activity for tracking and conflict prevention"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO user_activity_log 
                    (user_id, activity_type, form_level, details)
                    VALUES (?, ?, ?, ?)
                """, (user_id, activity_type, form_level, details))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error logging activity: {e}")
            return False
    
    def get_active_users_on_form(self, form_level: int, minutes: int = 5) -> List[Dict]:
        """Get users currently active on a specific form"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent activity for this form
                cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
                
                cursor.execute("""
                    SELECT DISTINCT u.user_id, u.username, u.full_name, u.assigned_forms
                    FROM school_users u
                    JOIN user_activity_log a ON u.user_id = a.user_id
                    WHERE a.form_level = ? 
                    AND a.timestamp > ?
                    AND a.activity_type IN ('login', 'data_entry', 'form_access')
                    ORDER BY a.timestamp DESC
                """, (form_level, cutoff_time))
                
                active_users = []
                for row in cursor.fetchall():
                    active_users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'full_name': row[2],
                        'assigned_forms': eval(row[3])
                    })
                
                return active_users
                
        except Exception as e:
            self.logger.error(f"Error getting active users: {e}")
            return []
    
    def check_form_access_conflict(self, user_id: int, form_level: int) -> Dict:
        """Check if user can access form without conflicts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user's assigned forms
                cursor.execute("""
                    SELECT assigned_forms FROM school_users WHERE user_id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {'can_access': False, 'reason': 'User not found'}
                
                assigned_forms = eval(result[0])
                
                # Check if user is assigned to this form
                if form_level not in assigned_forms:
                    return {
                        'can_access': False, 
                        'reason': f'User not assigned to Form {form_level}',
                        'assigned_forms': assigned_forms
                    }
                
                # Check for active conflicts
                active_users = self.get_active_users_on_form(form_level, minutes=2)
                
                # Filter out current user
                other_active_users = [u for u in active_users if u['user_id'] != user_id]
                
                if other_active_users:
                    return {
                        'can_access': False,
                        'reason': 'Form currently being edited by another user',
                        'active_users': other_active_users
                    }
                
                return {'can_access': True, 'assigned_forms': assigned_forms}
                
        except Exception as e:
            self.logger.error(f"Error checking form access: {e}")
            return {'can_access': False, 'reason': 'Error checking access'}
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def create_default_users(self, school_id: int, school_name: str) -> bool:
        """Create default users for a new school"""
        try:
            # Create 4 default users for Forms 1, 2, 3, 4
            default_users = [
                {
                    'username': f'{school_name.lower().replace(" ", "_")}_form1',
                    'password': 'Form1Teacher2024',
                    'full_name': f'{school_name} - Form 1 Teacher',
                    'role': 'teacher',
                    'assigned_forms': [1]
                },
                {
                    'username': f'{school_name.lower().replace(" ", "_")}_form2',
                    'password': 'Form2Teacher2024',
                    'full_name': f'{school_name} - Form 2 Teacher',
                    'role': 'teacher',
                    'assigned_forms': [2]
                },
                {
                    'username': f'{school_name.lower().replace(" ", "_")}_form3',
                    'password': 'Form3Teacher2024',
                    'full_name': f'{school_name} - Form 3 Teacher',
                    'role': 'teacher',
                    'assigned_forms': [3]
                },
                {
                    'username': f'{school_name.lower().replace(" ", "_")}_form4',
                    'password': 'Form4Teacher2024',
                    'full_name': f'{school_name} - Form 4 Teacher',
                    'role': 'teacher',
                    'assigned_forms': [4]
                }
            ]
            
            success_count = 0
            for user_data in default_users:
                if self.create_school_user(
                    school_id=school_id,
                    username=user_data['username'],
                    password=user_data['password'],
                    full_name=user_data['full_name'],
                    role=user_data['role'],
                    assigned_forms=user_data['assigned_forms']
                ):
                    success_count += 1
            
            self.logger.info(f"Created {success_count} default users for school {school_id}")
            return success_count == 4
            
        except Exception as e:
            self.logger.error(f"Error creating default users: {e}")
            return False
