# Troubleshooting Guide

Common issues and solutions for the ICU Patient Monitoring System.

## Parsing Issues

### Problem: Turkish Numbers Not Converting

**Symptoms:**
- "nokta on beş" appears as text, not 0.15
- Numbers remain in Turkish words

**Solutions:**
1. Check prompt is `prompts/core/01-parse-note.md` (critical parser)
2. Ensure exact Turkish spelling:
   - "nokta" or "virgül" (not "noqta")
   - "beş" not "bes"
3. Review Turkish number conversion section in parser prompt
4. Test with example: "Laktat bir nokta altı" should → 1.6

**Example Fix:**
```bash
# Test parser with simple input
claude-code "Parse this using prompts/core/01-parse-note.md: Laktat nokta on beş mmol/L"
# Should return: "lactate": {"value": 0.15, "unit": "mmol/L"}
```

### Problem: Missing Data in Structured Output

**Symptoms:**
- JSON has null values for parameters mentioned in note
- Data completeness <80%

**Solutions:**
1. **Check note format**: Ensure clinical note has clear parameter statements
   - ✅ Good: "Kreatinin bir nokta sekiz mg/dL"
   - ❌ Bad: "Kreatinin değerleri"

2. **Verify trend syntax**: Use comparison phrases
   - ✅ Good: "önceki değer iki nokta bir idi"
   - ❌ Bad: "öncekine göre düşük"

3. **Use standard terminology**:
   - "noradrenalin" → norepinephrine
   - "laktat" → lactate
   - "kreatinin" → creatinine

### Problem: Trends Not Detected

**Symptoms:**
- trend.direction shows "stable" when values clearly changed
- previous_value is null

**Solutions:**
1. Include explicit comparison in note:
   ```
   ✅ "Laktat bir nokta altı, önceki değer iki nokta bir idi, azaldı"
   ❌ "Laktat bir nokta altı, düzelme var"
   ```

2. Use Turkish trend keywords:
   - azaldı, düştü, geriledi → decreasing
   - arttı, yükseldi → increasing
   - iyileşiyor, düzeliyor → improving

3. Ensure previous day's structured data available for comparison

## Report Generation Issues

### Problem: Recommendations Too Vague

**Symptoms:**
- "Vazopresör ayarlanabilir" instead of specific doses
- No target parameters mentioned

**Solutions:**
1. **Check input data completeness**: Ensure structured JSON has:
   - Current values
   - Previous values (for trends)
   - All relevant parameters

2. **Use correct prompt**: Daily report = `prompts/reports/30-daily-report.md`

3. **Include context in request**:
   ```bash
   # ❌ Vague
   claude-code "Generate report for HT001"

   # ✅ Specific
   claude-code "Using structured data from HT001 for 2025-11-21 AND previous 2 days, generate comprehensive daily assessment using prompts/reports/30-daily-report.md with specific, actionable recommendations"
   ```

### Problem: Report in English Instead of Turkish

**Symptoms:**
- Output in English, not Turkish
- Mixed language output

**Solutions:**
1. Explicitly request Turkish in prompt:
   ```
   "Generate report in TURKISH using prompts/reports/30-daily-report.md"
   ```

2. Check prompt file has Turkish template
3. Verify `config/settings.yaml` has `language: "turkish"`

## Scoring Issues

### Problem: SOFA Score Incorrect

**Symptoms:**
- Component scores don't match criteria
- Total doesn't match components

**Solutions:**
1. **Review input data**: Ensure all 6 components available:
   - Respiratory (P/F ratio)
   - Coagulation (platelet)
   - Hepatic (bilirubin)
   - Cardiovascular (MAP, vasopressor)
   - Neurological (GCS)
   - Renal (creatinine, UO)

2. **Check scoring criteria**: Review `config/scoring-criteria.yaml`

3. **Verify calculations**:
   ```bash
   # Calculate with details
   claude-code "Calculate SOFA score from HT001 structured data using prompts/analysis/13-calculate-scores.md. Include detailed rationale for each component."
   ```

### Problem: Delta SOFA Shows "First Calculation"

**Symptoms:**
- Can't calculate change from previous day
- Delta SOFA unavailable

**Solutions:**
1. **Need previous day score**: Delta requires ≥2 days of data
2. Calculate today's SOFA, save it, then tomorrow will have delta
3. Check previous day's score file exists: `patients/active/ID/scores/YYYY-MM-DD.json`

## File and Directory Issues

### Problem: Permission Denied

**Symptoms:**
- Can't create files
- Can't execute scripts

**Solutions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Make scripts executable
chmod +x utils/*.sh

# Set proper permissions for patient data
chmod 700 patients/
chmod 600 patients/active/*/*.yaml
```

### Problem: Patient Directory Not Found

**Symptoms:**
- "No such file or directory" when processing patient

**Solutions:**
1. **Check patient exists**:
   ```bash
   ls patients/active/
   ```

2. **Create patient** if needed:
   ```bash
   ./utils/new-patient.sh PATIENT_ID
   ```

3. **Check spelling**: Patient IDs are case-sensitive

### Problem: Git Commits Patient Data

**Symptoms:**
- `.git/` shows patient notes or demographics

**Solutions:**
1. **STOP IMMEDIATELY** - Don't push to remote
2. Check `.gitignore`:
   ```bash
   cat .gitignore | grep patients
   # Should exclude: patients/active/*/notes/*.txt
   ```

3. Remove from git:
   ```bash
   git rm --cached patients/active/HT002/notes/*
   git commit -m "Remove patient data"
   ```

4. Add to `.gitignore` if not present
5. **Review** what was committed - may need to purge history if PHI

## Claude Code / API Issues

### Problem: Claude Code Command Not Found

**Symptoms:**
- `claude-code: command not found`

**Solutions:**
1. Check installation:
   ```bash
   which claude-code
   ```

2. Install Claude Code if needed (see docs)

3. Alternative: Use Claude API directly with appropriate wrapper

### Problem: API Rate Limiting

**Symptoms:**
- "Too many requests" error
- Slow responses

**Solutions:**
1. **Batch requests**: Process multiple patients together
2. **Cache results**: Save structured data, don't re-parse
3. **Use appropriate model**: Haiku for simple tasks, Sonnet for complex

### Problem: Prompt Too Long

**Symptoms:**
- Context length exceeded
- Truncated output

**Solutions:**
1. **Reduce input**: Don't include full 7-day history, use 2-3 days
2. **Summarize previous data**: Use trend summary, not full JSON
3. **Split task**: Parse → Score → Report separately

## Data Quality Issues

### Problem: Critical Values Not Flagged

**Symptoms:**
- Life-threatening values not in critical_values array
- No alerts generated

**Solutions:**
1. **Check thresholds**: Review `config/reference-ranges.yaml`
2. **Verify units**: Ensure consistent units (mg/dL, mmol/L)
3. **Re-parse**: Critical detection happens during parsing
   ```bash
   claude-code "Re-parse note with critical value detection enabled"
   ```

### Problem: Inconsistent Data Between Days

**Symptoms:**
- Parameters jump unexpectedly day-to-day
- Trends don't make clinical sense

**Solutions:**
1. **Review source notes**: Check if transcription error
2. **Verify units**: Mixing mg/dL and g/dL?
3. **Check parsing**: Same parameter extracted consistently?

## System Issues

### Problem: Backup Fails

**Symptoms:**
- `./utils/backup.sh` errors
- No backup created

**Solutions:**
1. **Check disk space**:
   ```bash
   df -h
   ```

2. **Create backups directory**:
   ```bash
   mkdir -p backups
   ```

3. **Check permissions**:
   ```bash
   chmod +x utils/backup.sh
   ls -la backups/
   ```

### Problem: Search Returns No Results

**Symptoms:**
- `./utils/search.sh TERM` finds nothing
- Known term not found

**Solutions:**
1. **Check spelling**: Turkish characters (ı, ş, ğ, ü, ö, ç)
2. **Use case-insensitive**: Script uses `-i` flag
3. **Try partial match**: "lakt" finds "laktat", "lactate"
4. **Check path**: Patient exists and has notes?

## Getting Help

### Before Asking for Help

1. **Check example patient HT001**: Does it work?
2. **Review logs**: Check for error messages
3. **Verify installation**: All files present?
4. **Test with simple input**: Isolate the issue

### Information to Provide

When reporting issues:
1. **Error message**: Exact text
2. **Steps to reproduce**: What did you do?
3. **Expected vs actual**: What should happen vs what happened?
4. **System info**: OS, Claude Code version
5. **File structure**: `ls -la` output if relevant

### Where to Get Help

- **Documentation**: Re-read relevant guide
- **GitHub Issues**: https://github.com/yourusername/icu-monitoring-system/issues
- **Example Patient**: Study HT001 workflow
- **Discussions**: Ask community questions

## Common Error Messages

### "Parsing confidence: low"

**Meaning**: Parser wasn't confident about extracted data

**Action**:
- Review source note for clarity
- Check for ambiguous phrasing
- Verify Turkish number formats
- Add more explicit values to note

### "Data completeness: 60%"

**Meaning**: Only 60% of expected data fields populated

**Action**:
- Add missing parameters to clinical note
- More complete notes → better analysis
- At minimum: vitals, key labs, assessment

### "YAML parsing error"

**Meaning**: Invalid YAML syntax in config or patient file

**Action**:
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('file.yaml'))"
```
- Check indentation (2 spaces, not tabs)
- Check quotes and special characters
- Validate lists and nested structures

## Tips for Preventing Issues

### 1. Use Templates
```bash
# Copy template instead of starting from scratch
cp templates/daily-note.txt patients/active/HT002/notes/2025-11-21.txt
```

### 2. Test with HT001 First
Before processing real patients, test workflow with example patient.

### 3. Validate Early
Check structured JSON immediately after parsing, before generating reports.

### 4. Consistent Format
Use same note format daily for consistent parsing.

### 5. Backup Regularly
```bash
# Daily backup
./utils/backup.sh
```

### 6. Version Control
Commit configuration changes (but never patient data!).

## Still Stuck?

1. Start fresh with example patient HT001
2. Compare your workflow to documented examples
3. Check if it's a prompt engineering issue (needs refinement)
4. Open GitHub issue with details

Remember: This is a decision support tool. When in doubt, rely on your clinical judgment, not the system output.
