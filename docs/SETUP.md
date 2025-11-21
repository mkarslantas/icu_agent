# Setup Guide

## Prerequisites

### Required
- **Claude Code** or Claude API access
- **Terminal/Command line** (bash-compatible)
- **Text editor** (vim, nano, VS Code, etc.)
- **Git** (for version control)

### Optional
- Python 3.x (for future extensions)
- jq (for JSON processing)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/icu-monitoring-system.git
cd icu-monitoring-system
```

### 2. Verify Directory Structure

```bash
ls -la
# Should see: config/, prompts/, patients/, utils/, docs/, etc.
```

### 3. Make Scripts Executable

```bash
chmod +x utils/*.sh
```

### 4. Create Backup Directory

```bash
mkdir -p backups
```

### 5. Test Installation

```bash
# View example patient
cat patients/active/HT001/notes/2025-11-20-day5.txt

# Run stats
./utils/stats.sh
```

## Configuration

### System Settings

Edit `config/settings.yaml` to customize:

```yaml
system:
  locale: "tr_TR"  # Turkish locale
  timezone: "Europe/Istanbul"

clinical:
  default_weight_kg: 70
  alerts:
    critical_values_notification: true

parsing:
  language: "turkish"
  number_conversion: true
```

### Reference Ranges

Adjust `config/reference-ranges.yaml` if your institution uses different thresholds:

```yaml
vitals:
  blood_pressure:
    map:
      target_min: 65  # Adjust per protocol
```

### Scoring Criteria

Review `config/scoring-criteria.yaml` for SOFA/APACHE-II calculation rules.

## Claude Code Setup

### Method 1: Claude Code CLI

If using Claude Code CLI:

```bash
# Already installed if you're using Claude Code
# Verify version
claude-code --version
```

### Method 2: API Access

If using Claude API directly:

1. Set API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

2. Add to `.bashrc` or `.zshrc` for persistence:
```bash
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
```

## Creating Your First Patient

### 1. Create Patient Directory

```bash
./utils/new-patient.sh HT002
```

### 2. Fill Patient Information

Edit demographics:
```bash
vim patients/active/HT002/demographics.yaml
```

Fill in:
- Age, gender
- Comorbidities
- Home medications
- Allergies

Edit admission data:
```bash
vim patients/active/HT002/admission.yaml
```

Fill in:
- Admission date/time
- Primary diagnosis
- Admission vitals
- Initial labs

### 3. Add Clinical Note

Create first note:
```bash
vim patients/active/HT002/notes/$(date +%Y-%m-%d).txt
```

Paste Turkish clinical note from ccNote or type manually.

### 4. Process Note

```bash
claude-code "Parse patients/active/HT002/notes/$(date +%Y-%m-%d).txt using prompts/core/01-parse-note.md. Output structured JSON."
```

Save output to `patients/active/HT002/structured/$(date +%Y-%m-%d).json`

## Backup Setup

### Manual Backup

```bash
./utils/backup.sh
```

### Automated Backup (Cron)

Add to crontab:
```bash
crontab -e

# Add line for daily backup at 2 AM:
0 2 * * * cd /path/to/icu-monitoring-system && ./utils/backup.sh >> logs/backup.log 2>&1
```

## Directory Permissions

Ensure proper permissions:

```bash
# Owner read/write only for patient data
chmod 700 patients/
chmod 700 patients/active/
chmod 600 patients/active/*/*.yaml

# Executable for scripts
chmod +x utils/*.sh
```

## Troubleshooting Setup

### Issue: Scripts Not Executable

```bash
chmod +x utils/*.sh
```

### Issue: YAML Parsing Errors

Validate YAML syntax:
```bash
# If you have Python:
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"
```

### Issue: Claude Code Not Found

Check installation:
```bash
which claude-code
# Or check Claude Code documentation
```

### Issue: Permission Denied

```bash
# Check ownership
ls -la

# Fix ownership
sudo chown -R $USER:$USER .
```

## Next Steps

1. Read [USAGE.md](USAGE.md) for daily workflows
2. Review [CLINICAL_GUIDELINES.md](CLINICAL_GUIDELINES.md)
3. Process example patient HT001 to learn system
4. Create your first real patient (with anonymized data)

## Security Checklist

- [ ] `.gitignore` configured (patient data excluded)
- [ ] Backup directory created
- [ ] Proper file permissions set
- [ ] API keys stored securely (not in repo)
- [ ] Local-only storage verified
- [ ] Compliance with local regulations confirmed

## Getting Help

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Open GitHub issue
- Review example patient HT001

**Setup Complete!** 🎉 Ready to start monitoring patients.
