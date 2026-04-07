# Render Deployment Guide - Persistent Data Storage

This guide ensures your School Reporting System data remains intact across deployments on Render.

## 🎯 Problem Solved

**Issue**: On platforms like Render, databases can get wiped between deployments, causing data loss.

**Solution**: Implemented comprehensive persistent data storage with automatic backups and data protection.

## 📁 Files Added

### Core Components
- `persistent_data_manager.py` - Manages persistent storage across deployments
- `deploy_render.py` - Deployment setup and verification
- `start_render.sh` - Application startup with data protection
- `render_config.yaml` - Render service configuration
- `.env.render` - Environment variables for Render

### Key Features Implemented

#### 1. **Persistent Storage**
- Database stored in `/opt/render/project/src/data/` (persistent disk)
- Automatic directory creation and permissions
- Cross-platform compatibility (Render + local development)

#### 2. **Automatic Backups**
- Pre-deployment backups
- Scheduled automatic backups
- Backup retention management
- Multiple backup formats

#### 3. **Data Protection**
- Integrity verification on startup
- Protection checkpoints
- Wipe detection and prevention
- Size monitoring and alerts

#### 4. **Environment Detection**
- Automatic Render vs local detection
- Appropriate storage paths
- Environment-specific configurations

## 🚀 Deployment Steps

### Option 1: Automatic Deployment (Recommended)
1. Push code to your repository
2. Connect repository to Render
3. Use `render_config.yaml` configuration
4. Render automatically handles deployment

### Option 2: Manual Deployment
1. Copy files to Render instance
2. Run deployment script:
   ```bash
   python deploy_render.py
   ```
3. Start application:
   ```bash
   bash start_render.sh
   ```

## 🔧 Configuration

### Environment Variables
- `RENDER=true` - Enables Render-specific features
- `DATABASE_PATH` - Persistent database location
- `BACKUP_DIR` - Backup storage location
- `AUTO_BACKUP_ENABLED=true` - Enable automatic backups
- `DATA_PROTECTION_ENABLED=true` - Enable data protection

### Render Service Settings
- **Persistent Disk**: 10GB storage
- **Auto-deploy**: Enabled
- **Health checks**: Enabled
- **Free tier**: Suitable for small to medium schools

## 🛡️ Data Protection Features

### What's Protected
- Student records and marks
- School settings and configurations
- Academic periods and terms
- Teacher assignments

### Protection Mechanisms
1. **Startup Verification**: Checks database integrity before starting
2. **Checkpoint System**: Creates protection snapshots
3. **Size Monitoring**: Detects potential data wipes
4. **Backup System**: Multiple backup layers
5. **Access Control**: Blocks suspicious operations

## 📊 Backup Strategy

### Automatic Backups
- **Pre-deployment**: Before each deployment
- **Scheduled**: Daily automatic backups
- **Retention**: 30 days retention policy
- **Location**: Separate persistent storage

### Manual Backup
```python
from persistent_data_manager import PersistentDataManager

manager = PersistentDataManager()
backup_path = manager.create_backup('/path/to/database.db')
print(f"Backup created: {backup_path}")
```

## 🔍 Monitoring and Maintenance

### Health Checks
- Database integrity verification
- Storage space monitoring
- Backup verification
- Performance metrics

### Logs Location
- **Render**: `/opt/render/project/src/logs/`
- **Local**: `./logs/`
- **Database**: `school_database.log`

## 🚨 Recovery Procedures

### If Data Loss Occurs
1. Check backup directory: `/opt/render/project/src/backups/`
2. Restore from latest backup:
   ```python
   from persistent_data_manager import PersistentDataManager
   
   manager = PersistentDataManager()
   success = manager.restore_from_backup('backup_file.db', '/path/to/database.db')
   ```
3. Verify data integrity after restoration

## 📱 Development vs Production

### Local Development
- Uses `./data/` for storage
- Automatic backup creation
- Full logging enabled

### Render Production
- Uses persistent disk storage
- Enhanced security features
- Optimized for multi-instance

## ⚡ Performance Optimizations

### Database Settings
- WAL journal mode for better concurrency
- Connection pooling
- Timeout management
- Retry mechanisms

### Storage Optimization
- Compressed backups
- Log rotation
- Cleanup automation

## 🔐 Security Features

### Data Protection
- Wipe detection algorithms
- Access logging
- Checkpoint validation
- Size threshold monitoring

### Access Control
- Environment-based permissions
- Secure file handling
- Protected directory structure

## 📞 Support and Troubleshooting

### Common Issues
1. **Database not found**: Check storage paths and permissions
2. **Backup failures**: Verify disk space and permissions
3. **Performance issues**: Check database size and optimize

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

### Health Check Endpoint
Access: `https://your-app.onrender.com/health`

## 🎉 Benefits Achieved

✅ **Data Persistence**: Data survives deployments and restarts
✅ **Automatic Backups**: Multiple backup layers with retention
✅ **Data Protection**: Prevents accidental data wipes
✅ **Easy Recovery**: Simple restoration procedures
✅ **Cross-Platform**: Works on Render and local development
✅ **Zero Downtime**: Seamless deployment with data preservation

## 📝 Maintenance Tasks

### Weekly
- Review backup logs
- Check storage usage
- Verify data integrity
- Clean old backups (retention policy)

### Monthly
- Test recovery procedures
- Update configurations
- Performance optimization
- Security audit

---

**Your data is now protected and will persist across all deployments on Render!**
