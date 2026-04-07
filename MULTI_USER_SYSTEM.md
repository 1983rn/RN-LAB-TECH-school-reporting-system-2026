# Multi-User Concurrent Access System

## Overview

The School Reporting System now supports **multi-user concurrent access**, allowing up to 4 users from the same school to work simultaneously on different forms (1, 2, 3, and 4) without data interference or system compromise.

## Key Features

### 1. User Management
- **4 Default Users per School**: Each school gets 4 pre-configured users
- **Form-Specific Access**: Each user is assigned to a specific form
- **Role-Based Permissions**: Users can only access their assigned forms
- **Secure Authentication**: Password-protected user accounts

### 2. Conflict Prevention
- **Real-time Conflict Detection**: Prevents simultaneous editing of the same form
- **Access Locking**: When a user is working on a form, others are blocked
- **Activity Monitoring**: Tracks active users and their current work
- **Automatic Conflict Resolution**: First user gets priority, others get notified

### 3. Shared School Settings
- **Centralized Configuration**: All users share the same school settings
- **Consistent Academic Periods**: Same terms and academic years for all users
- **Unified Subject Management**: Subjects are shared across all forms
- **Common School Information**: School name, address, contact details shared

### 4. Data Integrity
- **Persistent Storage**: Data remains intact after logout or inactivity
- **Automatic Backups**: Regular backups prevent data loss
- **Concurrent Safe**: Database operations handle multiple users safely
- **Activity Logging**: All user actions are tracked and logged

## User Accounts

### Default User Creation
For each school, 4 users are automatically created:

| Form | Username | Password | Full Name |
|------|----------|----------|-----------|
| Form 1 | `[SCHOOL_NAME]_form1` | `Form1Teacher2024` | `[SCHOOL_NAME] - Form 1 Teacher` |
| Form 2 | `[SCHOOL_NAME]_form2` | `Form2Teacher2024` | `[SCHOOL_NAME] - Form 2 Teacher` |
| Form 3 | `[SCHOOL_NAME]_form3` | `Form3Teacher2024` | `[SCHOOL_NAME] - Form 3 Teacher` |
| Form 4 | `[SCHOOL_NAME]_form4` | `Form4Teacher2024` | `[SCHOOL_NAME] - Form 4 Teacher` |

**Note**: Replace `[SCHOOL_NAME]` with the actual school name (lowercase, underscores for spaces).

### Example
For "DEMO SECONDARY SCHOOL":
- Form 1: `demo_secondary_school_form1` / `Form1Teacher2024`
- Form 2: `demo_secondary_school_form2` / `Form2Teacher2024`
- Form 3: `demo_secondary_school_form3` / `Form3Teacher2024`
- Form 4: `demo_secondary_school_form4` / `Form4Teacher2024`

## How It Works

### 1. Login Process
1. User selects "School" user type
2. Enters their username and password
3. System authenticates and redirects to multi-user dashboard
4. User sees only their assigned forms

### 2. Form Access Control
1. User clicks on their assigned form
2. System checks for conflicts (other users on same form)
3. If clear, user gets exclusive access
4. If conflict, user sees error message with details

### 3. Concurrent Work
1. Multiple users can work on different forms simultaneously
2. Each user has their own session and activity tracking
3. Real-time monitoring prevents data conflicts
4. Automatic saving prevents data loss

### 4. Activity Monitoring
- **Heartbeat System**: Users send regular activity updates
- **Session Tracking**: Monitors active users per form
- **Conflict Alerts**: Notifies users of access attempts
- **Activity Logs**: Records all user actions

## Technical Implementation

### Database Tables

#### `school_users`
- Stores individual user accounts
- Links users to schools
- Manages form assignments
- Tracks user status and activity

#### `user_activity_log`
- Records all user actions
- Tracks form access and modifications
- Provides conflict detection data
- Enables audit trails

### API Endpoints

#### Authentication
- `POST /api/login` - Multi-user login support
- Automatic user type detection
- Session management

#### Multi-User Features
- `POST /api/user-heartbeat` - Activity monitoring
- `POST /api/check-form-conflicts` - Conflict detection
- `GET /api/user-activity/<id>` - Activity log retrieval
- `GET /api/check-form-status` - Global form status

#### User Interface
- `/multi-user-dashboard` - User-specific dashboard
- `/form/<level>/multi-user` - Protected form entry
- Real-time conflict indicators
- Activity status displays

### Security Features

#### Access Control
- Form-specific permissions
- Session-based authentication
- Automatic timeout protection
- Secure password hashing

#### Data Protection
- Concurrent-safe database operations
- Automatic conflict resolution
- Data integrity checks
- Regular backup systems

## Setup Instructions

### For New Schools
1. School admin creates school account
2. System automatically creates 4 user accounts
3. Admin distributes credentials to teachers
4. Teachers login with their assigned credentials

### For Existing Schools
Run the setup script:
```bash
python setup_multi_user.py
```

This will:
- Create user tables if they don't exist
- Generate default users for all existing schools
- Display user credentials for distribution

### Testing the System
Run the test script:
```bash
python test_multi_user.py
```

This verifies:
- User table creation
- Default user generation
- Authentication system
- Form access control
- Conflict detection
- Activity logging

## User Experience

### Multi-User Dashboard
- Shows assigned forms only
- Displays current activity status
- Provides access to shared school settings
- Shows real-time conflict alerts

### Form Data Entry
- Protected access to assigned form
- Real-time activity monitoring
- Auto-save functionality
- Conflict prevention indicators

### Error Handling
- Clear error messages for access conflicts
- User-friendly notifications
- Automatic retry mechanisms
- Graceful degradation

## Benefits

### For Schools
- **Efficiency**: Multiple teachers can work simultaneously
- **Organization**: Clear separation of responsibilities
- **Security**: Controlled access to sensitive data
- **Accountability**: Complete activity tracking

### For Teachers
- **Dedicated Access**: Each teacher has their own account
- **No Interference**: Can't accidentally modify other forms
- **Easy to Use**: Simple login and intuitive interface
- **Real-time Feedback**: Instant status updates

### For Administrators
- **User Management**: Easy to add/remove users
- **Activity Monitoring**: Track who's doing what
- **Conflict Resolution**: Handle access disputes
- **Data Integrity**: Ensure data consistency

## Troubleshooting

### Common Issues

#### Login Problems
- Verify correct username format
- Check password spelling
- Ensure user type is "School"
- Contact admin if credentials lost

#### Access Conflicts
- Wait for current user to finish
- Try refreshing the page
- Check if you're assigned to the correct form
- Contact admin if issue persists

#### Data Not Saving
- Check internet connection
- Verify form access is not conflicting
- Look for error messages
- Try manual save button

### Error Messages

#### "Form currently being edited by another user"
- Another user has active access
- Wait a few minutes and try again
- Contact the other user if needed

#### "You are not assigned to this form"
- Check your assigned forms on dashboard
- Contact admin for form assignment
- Verify you're using correct account

#### "Authentication failed"
- Check username and password
- Ensure correct user type selected
- Contact admin for account issues

## Future Enhancements

### Planned Features
- **Real-time Collaboration**: Multiple users on same form
- **Advanced Permissions**: Subject-level access control
- **Mobile Support**: Tablet and phone interfaces
- **Offline Mode**: Work without internet connection

### Scalability
- **More Forms**: Support for additional form levels
- **More Users**: Flexible user limits per school
- **Role Management**: Custom user roles and permissions
- **API Access**: Third-party integration support

## Conclusion

The multi-user concurrent access system transforms the School Reporting System from a single-user application into a collaborative platform. It maintains data integrity while enabling multiple teachers to work efficiently, providing schools with the tools they need for modern educational management.

The system is designed to be:
- **Secure**: Protected access and data integrity
- **Efficient**: No waiting or conflicts
- **User-friendly**: Intuitive interface and clear feedback
- **Scalable**: Ready for future enhancements

Schools can now leverage the full potential of their teaching staff, with each teacher having dedicated access to their assigned forms while maintaining the consistency and security of the overall system.
