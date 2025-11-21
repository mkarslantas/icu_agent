#!/bin/bash
# Backup ICU patient data

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/${TIMESTAMP}"

echo "🔄 Creating backup..."
echo "Timestamp: ${TIMESTAMP}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup active patients
echo "📦 Backing up active patients..."
if [ -d "patients/active" ] && [ "$(ls -A patients/active)" ]; then
    cp -r patients/active "${BACKUP_DIR}/"
    echo "   ✓ Active patients backed up"
else
    echo "   ℹ No active patients to backup"
fi

# Backup configuration
echo "📦 Backing up configuration..."
cp -r config "${BACKUP_DIR}/"
echo "   ✓ Configuration backed up"

# Backup prompts
echo "📦 Backing up prompts..."
cp -r prompts "${BACKUP_DIR}/"
echo "   ✓ Prompts backed up"

# Create backup manifest
cat > "${BACKUP_DIR}/manifest.txt" << EOF
ICU Monitoring System Backup
============================
Backup Date: $(date +"%Y-%m-%d %H:%M:%S")
Backup ID: ${TIMESTAMP}

Contents:
- Active patients data
- Configuration files
- Prompt templates

Restore Instructions:
1. Extract backup to temporary location
2. Review contents
3. Copy desired files back to main directory
4. Verify integrity

EOF

# Create compressed archive
echo "🗜️  Compressing backup..."
cd backups
tar -czf "${TIMESTAMP}.tar.gz" "${TIMESTAMP}"
rm -rf "${TIMESTAMP}"
cd ..

BACKUP_SIZE=$(du -h "backups/${TIMESTAMP}.tar.gz" | cut -f1)

echo ""
echo "✅ Backup completed successfully!"
echo "📂 Location: backups/${TIMESTAMP}.tar.gz"
echo "📊 Size: ${BACKUP_SIZE}"
echo ""
echo "To restore:"
echo "   tar -xzf backups/${TIMESTAMP}.tar.gz -C backups/"
echo ""
