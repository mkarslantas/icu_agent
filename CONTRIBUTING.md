# Contributing to ICU Patient Monitoring System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 Code of Conduct

- Be respectful and professional
- Focus on improving patient care
- Protect patient privacy at all times
- Follow evidence-based medicine principles
- Collaborate constructively

## 🎯 Ways to Contribute

### 1. Prompt Engineering
- Improve existing prompts for accuracy
- Add new clinical prompts
- Enhance Turkish language handling
- Fix parsing edge cases

### 2. Clinical Content
- Add new clinical protocols
- Update guidelines to latest evidence
- Contribute drug database entries
- Add scoring systems

### 3. Documentation
- Improve setup instructions
- Add usage examples
- Translate documentation
- Fix typos and clarity

### 4. Code & Scripts
- Enhance utility scripts
- Add new features
- Fix bugs
- Improve performance

### 5. Testing & Validation
- Test with real scenarios (anonymized data only)
- Report bugs
- Suggest improvements
- Clinical validation

## 📝 Contribution Guidelines

### General Principles

1. **Evidence-Based**: All clinical content must be based on current evidence and guidelines
2. **Privacy First**: Never commit patient data (real or identifiable)
3. **Documentation**: Document all changes thoroughly
4. **Testing**: Test changes with example patient data
5. **Review**: Be open to peer review and feedback

### Before You Start

1. Check existing issues to avoid duplication
2. Open an issue to discuss major changes
3. Fork the repository
4. Create a feature branch

### Prompt Development Guidelines

When creating or modifying prompts:

```markdown
# Prompt Title

## Purpose
Clear statement of what this prompt does

## Input
Describe expected input format

## Output
Describe output format (JSON schema, markdown template, etc.)

## Instructions
Step-by-step instructions for the AI

## Examples
At least one example input/output pair

## Edge Cases
Document how to handle edge cases

## Clinical Context
Evidence base or guidelines referenced
```

#### Turkish Language Prompts

- Use professional medical Turkish
- Translate terminology consistently
- Provide both Turkish and English for drug names
- Use Turkish number words examples
- Explain cultural considerations

#### Prompt Testing

Before submitting:
- Test with example patient (HT001)
- Test with edge cases
- Verify output format
- Check for hallucinations
- Validate clinical accuracy

### Clinical Content Guidelines

#### Adding Protocols

1. **Source**: Cite evidence-based guidelines
2. **Date**: Include publication year
3. **Applicability**: Note if specific to population
4. **Format**: Use consistent markdown structure

#### Drug Database Entries

Required fields:
- Generic name
- Class
- Mechanism of action
- Dosing (including ICU-specific)
- Monitoring parameters
- Adverse effects
- Drug interactions
- Evidence/references

#### Scoring Systems

Include:
- Full scoring criteria
- Calculation method
- Interpretation
- Mortality/outcome prediction
- Limitations
- Evidence base

### Code Guidelines

#### Bash Scripts

```bash
#!/bin/bash
# Script description

# Check parameters
if [ -z "$1" ]; then
    echo "Error message"
    echo "Usage: script.sh PARAM"
    exit 1
fi

# Clear variable names
PATIENT_ID="$1"

# Comment complex logic
# Explanation of what this does

# Error handling
if [ ! -d "$DIR" ]; then
    echo "Error: Directory not found"
    exit 1
fi
```

#### YAML Files

- Use consistent indentation (2 spaces)
- Add comments for complex fields
- Validate YAML syntax
- Use meaningful key names

### Documentation Standards

- Use clear, concise language
- Provide examples
- Keep beginner-friendly
- Update table of contents
- Check for broken links

### Git Commit Messages

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructure
- `test`: Testing
- `chore`: Maintenance

Examples:
```
feat(prompts): add septic shock assessment prompt

- Adds prompt for early septic shock recognition
- Includes lactate trending analysis
- Based on SSC 2021 guidelines

Closes #123
```

```
fix(parser): handle Turkish fraction expressions

- Fixes parsing of "bir buçuk" (1.5)
- Adds test cases for fractions
- Updates documentation

Fixes #456
```

## 🔄 Pull Request Process

### Before Submitting

1. **Test thoroughly**
   - Run with example patient
   - Test edge cases
   - Verify no patient data committed

2. **Update documentation**
   - Update README if needed
   - Update CHANGELOG.md
   - Add docstrings/comments

3. **Check .gitignore**
   - Ensure no sensitive files
   - No patient data
   - No credentials

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Clinical content update
- [ ] Breaking change

## Testing
How was this tested?

## Clinical Validation
Was this clinically reviewed? By whom?

## Evidence Base
What guidelines or evidence supports this?

## Checklist
- [ ] Code tested with example patient
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No patient data committed
- [ ] Follows contribution guidelines
- [ ] Ready for review
```

### Review Process

1. Maintainer reviews for:
   - Code quality
   - Clinical accuracy
   - Documentation completeness
   - Privacy compliance

2. Clinical expert review (for clinical content)
3. Testing with example data
4. Approval by 2 maintainers
5. Merge to main branch

## 🏥 Clinical Review

For clinical content contributions:

1. **Expertise Required**
   - Intensivist/ICU physician
   - Emergency medicine
   - Infectious disease (for antibiotic guidelines)
   - Respiratory therapist (for ventilation)

2. **Review Checklist**
   - Evidence-based and current
   - Appropriate for ICU setting
   - Clear contraindications noted
   - Adverse effects documented
   - Dosing appropriate and safe

3. **Liability Disclaimer**
   - All clinical content is advisory only
   - Not a substitute for clinical judgment
   - Local protocols may differ

## 🔐 Privacy & Security

### Absolute Rules

1. **NEVER commit real patient data**
2. **NEVER commit patient identifiers** (names, MRNs, dates of birth, etc.)
3. **NEVER commit credentials or API keys**

### If Accidental Commit

1. **Stop immediately**
2. Contact maintainers
3. Remove from history (git filter-branch or BFG)
4. Rotate any exposed credentials
5. Report as security incident

### Example Data Guidelines

- Use fictional patients only
- Use clearly fake IDs (HT001, TEST001, EXAMPLE001)
- Randomize all values
- Note clearly as "EXAMPLE DATA"
- No combination of real patient data points

## 📚 Resources for Contributors

### Clinical Guidelines
- Surviving Sepsis Campaign 2021
- IDSA Guidelines Portal
- ARDS Network Protocols
- SCCM (Society of Critical Care Medicine)

### Technical Resources
- Markdown Guide: https://www.markdownguide.org/
- YAML Syntax: https://yaml.org/
- Conventional Commits: https://www.conventionalcommits.org/

### Turkish Medical Resources
- Turkish Society of Intensive Care
- Turkish medical terminology standards

## ❓ Questions?

- Open an issue for technical questions
- Discussion forum for clinical questions
- Email maintainers for sensitive issues

## 🙏 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Acknowledged in release notes
- Added to contributors list (if desired)

Thank you for helping improve ICU patient care! 🏥
