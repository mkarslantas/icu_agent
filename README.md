# 🏥 ICU Patient Monitoring System

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

> AI-powered clinical decision support system for intensive care unit patient monitoring with Turkish language support

## 📋 Overview

The ICU Patient Monitoring System is a comprehensive AI-powered clinical decision support tool designed specifically for intensive care units. It parses Turkish clinical notes from voice transcription systems (ccNote), performs sophisticated clinical analysis, calculates severity scores (SOFA, APACHE-II), and generates evidence-based recommendations.

### Key Features

- ✅ **Turkish Clinical Note Parser** - Converts unstructured Turkish medical notes to structured JSON
- ✅ **Turkish Number Conversion** - Handles Turkish number words ("nokta on beş" → 0.15)
- ✅ **Automatic Critical Value Detection** - Flags life-threatening parameters instantly
- ✅ **SOFA & APACHE-II Scoring** - Automated severity score calculation
- ✅ **Evidence-Based Recommendations** - Vasopressor, ventilator, antibiotic management
- ✅ **Daily Assessment Reports** - Comprehensive Turkish clinical summaries
- ✅ **7-Day Trend Analysis** - Multi-day parameter tracking and visualization
- ✅ **Complete Documentation** - Detailed guides for non-technical users

## 🚀 Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/code) or API access
- Terminal/Command line
- Text editor

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/icu-monitoring-system.git
cd icu-monitoring-system

# Create a new patient
./utils/new-patient.sh HT002

# Add a clinical note
vim patients/active/HT002/notes/2025-11-21.txt
# [Paste your Turkish clinical note]

# Process the note (example with Claude Code)
claude-code "Parse the Turkish clinical note in patients/active/HT002/notes/2025-11-21.txt using the prompt in prompts/core/01-parse-note.md. Save the structured output to patients/active/HT002/structured/2025-11-21.json"

# Generate daily assessment
claude-code "Using the structured data in patients/active/HT002/structured/2025-11-21.json and the prompt in prompts/reports/30-daily-report.md, generate a comprehensive Turkish daily assessment report. Save to patients/active/HT002/reports/daily/2025-11-21_assessment.md"

# View the report
cat patients/active/HT002/reports/daily/2025-11-21_assessment.md
```

## 📁 Project Structure

```
icu-monitoring-system/
├── config/                    # System configuration
│   ├── settings.yaml         # Global settings
│   ├── reference-ranges.yaml # Normal lab values
│   ├── scoring-criteria.yaml # SOFA, APACHE-II
│   ├── weaning-protocols.yaml
│   └── antibiotic-guidelines.yaml
│
├── prompts/                   # AI prompts
│   ├── core/                 # Parsing prompts
│   │   └── 01-parse-note.md # 🔥 CRITICAL: Turkish note parser
│   ├── analysis/             # Analysis prompts
│   │   ├── 13-calculate-scores.md
│   │   └── 11-trend-analysis.md
│   ├── recommendations/      # Clinical recommendations
│   │   ├── 20-vasopressor-mgmt.md
│   │   ├── 21-ventilator-weaning.md
│   │   └── 22-antibiotic-steward.md
│   └── reports/             # Report generation
│       ├── 30-daily-report.md
│       └── 31-weekly-summary.md
│
├── patients/                 # Patient data
│   ├── active/HT001/        # Example patient
│   │   ├── demographics.yaml
│   │   ├── admission.yaml
│   │   ├── notes/           # Clinical notes (Turkish)
│   │   ├── structured/      # Parsed JSON data
│   │   ├── scores/          # SOFA, APACHE scores
│   │   ├── trends/          # Trend analysis
│   │   └── reports/         # Generated reports
│   ├── discharged/
│   └── deceased/
│
├── knowledge-base/           # Clinical protocols
│   ├── protocols/           # Sepsis, ARDS, AKI
│   ├── guidelines/          # Surviving Sepsis, etc.
│   ├── evidence/            # Key trial summaries
│   └── drug-database/       # Vasopressors, antibiotics
│
├── templates/                # File templates
├── utils/                    # Utility scripts
│   ├── new-patient.sh       # Create new patient
│   ├── backup.sh            # Backup data
│   ├── search.sh            # Search notes
│   └── stats.sh             # System statistics
│
└── docs/                     # Documentation
    ├── SETUP.md
    ├── USAGE.md
    ├── CLINICAL_GUIDELINES.md
    └── TROUBLESHOOTING.md
```

## 💡 Usage Examples

### Example 1: Parse Turkish Clinical Note

**Input** (`patients/active/HT001/notes/2025-11-20-day5.txt`):
```
68 yaşında erkek hasta, ürosepsis nedeniyle beşinci gün takipte.
Hemodinamisi noradrenalin nokta on beş mikrogram kilogram dakika ile stabil.
Laktat bir nokta altı, önceki değer iki nokta bir idi, perfüzyon iyileşiyor.
```

**Processing**:
```bash
claude-code "Parse using prompts/core/01-parse-note.md"
```

**Output**: Structured JSON with:
- Numbers converted: "nokta on beş" → 0.15, "bir nokta altı" → 1.6
- Trends detected: lactate 2.1 → 1.6 (decreasing, improving)
- Critical values flagged
- All clinical parameters structured

### Example 2: Daily Assessment Report

From structured data, generates comprehensive Turkish report with:
- System-by-system evaluation (cardiovascular, respiratory, renal, etc.)
- 3-day trend analysis
- Specific, actionable recommendations
- SOFA score tracking
- Priority alerts

### Example 3: Calculate SOFA Score

```bash
claude-code "Calculate SOFA score from today's structured data using prompts/analysis/13-calculate-scores.md"
```

Outputs detailed score breakdown, mortality risk, and delta SOFA interpretation.

## 🎯 Core Capabilities

### 1. Turkish Clinical Note Parsing

The system's **most critical component** is the Turkish note parser (`prompts/core/01-parse-note.md`). It handles:

- **Turkish Number Conversion**
  - "nokta" / "virgül" → decimal point
  - "nokta on beş" → 0.15
  - "iki buçuk" → 2.5
  - "yüz yirmi beş" → 125
  - "yüzde doksan altı" → 96

- **Trend Detection**
  - "azaldı", "düştü" → decreasing
  - "iyileşiyor" → improving
  - "temizleniyor" (lactate) → clearing

- **Medical Terminology**
  - Turkish ↔ English standardization
  - "noradrenalin" → "norepinephrine"
  - "laktat" → "lactate"
  - Drug name normalization

### 2. Clinical Scoring

- **SOFA Score**: Daily organ failure assessment (0-24)
- **APACHE-II**: Admission severity (0-71)
- **TURK-SOFA**: Turkish population adaptation
- **Delta SOFA**: Trend from baseline

### 3. Evidence-Based Recommendations

All recommendations based on:
- Surviving Sepsis Campaign 2021
- ARDS Network protocols
- IDSA antibiotic guidelines
- Evidence-based weaning protocols

### 4. Comprehensive Reporting

Reports in professional Turkish with:
- System-by-system evaluation
- Trend analysis tables
- Specific, actionable recommendations (not vague)
- Critical value alerts
- 24-hour plan

## 📊 Clinical Decision Support

### Vasopressor Management
- Evidence-based titration recommendations
- Weaning readiness assessment
- Multi-agent strategies

### Ventilator Weaning
- Daily SBT readiness screening
- Weaning protocol guidance
- Extubation criteria evaluation

### Antibiotic Stewardship
- De-escalation opportunities
- Duration recommendations
- Spectrum narrowing guidance

## 🔒 Privacy & Security

**IMPORTANT**: This system handles sensitive medical data.

- ✅ No patient data committed to git (see `.gitignore`)
- ✅ Example patient (HT001) uses anonymized data only
- ✅ Local storage only - no cloud transmission
- ✅ Audit logging available
- ⚠️ Ensure compliance with local healthcare data regulations (HIPAA, GDPR, etc.)

## 📈 Scoring Systems

### SOFA Score Interpretation
- 0-6: <10% mortality (low risk)
- 7-9: 15-20% mortality (moderate risk)
- 10-12: 40-50% mortality (high risk)
- 13-14: 50-60% mortality (very high risk)
- 15-24: >80% mortality (critical)

### Critical Thresholds
- MAP < 65 mmHg → Life-threatening
- Lactate > 4 mmol/L → Critical
- GCS < 8 → Life-threatening
- SpO2 < 90% → Critical
- K+ < 2.5 or > 6.5 → Life-threatening
- pH < 7.2 or > 7.6 → Life-threatening

## 🛠️ Utility Scripts

```bash
# Create new patient
./utils/new-patient.sh PATIENT_ID

# Backup all data
./utils/backup.sh

# Search across patients
./utils/search.sh "laktat" HT001

# System statistics
./utils/stats.sh
```

## 📚 Documentation

- **[SETUP.md](docs/SETUP.md)** - Installation and configuration
- **[USAGE.md](docs/USAGE.md)** - Daily workflows and common tasks
- **[CLINICAL_GUIDELINES.md](docs/CLINICAL_GUIDELINES.md)** - Clinical protocols
- **[SCORING_SYSTEMS.md](docs/SCORING_SYSTEMS.md)** - SOFA, APACHE-II details
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## ⚠️ Disclaimer

**IMPORTANT**: This system provides **clinical decision support only**.

- ❌ NOT intended for diagnostic purposes
- ❌ NOT FDA approved or CE marked
- ❌ NOT a substitute for clinical judgment
- ✅ All recommendations must be reviewed by qualified healthcare professionals
- ✅ Final clinical decisions remain with the responsible physician
- ✅ Use as an adjunct to clinical expertise, not a replacement

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas for contribution:
- Additional prompt templates
- New clinical protocols
- Language support (beyond Turkish)
- Bug fixes and improvements
- Documentation enhancements

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Surviving Sepsis Campaign** - Evidence-based sepsis guidelines
- **ARDS Network** - Mechanical ventilation protocols
- **IDSA** - Infectious disease guidelines
- **Turkish ICU community** - Clinical validation and feedback
- **Anthropic** - Claude AI technology

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/icu-monitoring-system/issues)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/icu-monitoring-system/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/icu-monitoring-system/discussions)

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Multi-patient dashboard
- [ ] PDF report export
- [ ] Interactive trend visualizations
- [ ] Additional scoring systems (qSOFA, CURB-65)

### Version 2.0 (Future)
- [ ] EHR integration capabilities
- [ ] Real-time monitoring support
- [ ] Machine learning predictions
- [ ] Mobile interface

---

**Made with ❤️ for improving ICU patient care**

**Version**: 1.0.0
**Last Updated**: 2025-11-21
**Status**: Production Ready
