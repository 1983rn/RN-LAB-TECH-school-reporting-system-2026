#!/usr/bin/env python3
"""
Subscription Update Script
Automatically updates days remaining for all schools
Run this script daily via cron job or task scheduler

Created by: RN_LAB_TECH
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from school_database import SchoolDatabase

def update_all_subscriptions():
    """Update subscription days for all schools"""
    try:
        db = SchoolDatabase()
        
        print(f"[{datetime.now()}] Starting subscription update...")
        
        # Update days remaining for all schools
        db.update_days_remaining()
        
        # Get schools that need attention
        schools_to_lock = db.get_schools_to_lock()
        
        if schools_to_lock:
            print(f"WARNING: {len(schools_to_lock)} schools have expired subscriptions:")
            for school in schools_to_lock:
                print(f"  - {school['school_name']} ({school['username']}) - {abs(school['days_remaining'])} days overdue")
        
        # Send reminders to schools with expiring subscriptions
        reminder_count = db.send_subscription_reminder()
        
        print(f"Subscription update completed successfully")
        print(f"Reminders sent to {reminder_count} schools")
        print(f"Schools requiring lock: {len(schools_to_lock)}")
        
        return True
        
    except Exception as e:
        print(f"Error updating subscriptions: {e}")
        return False

if __name__ == "__main__":
    success = update_all_subscriptions()
    sys.exit(0 if success else 1)