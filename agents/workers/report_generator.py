"""
Report Generator Agent

This agent generates comprehensive Turkish daily ICU reports from all
collected clinical data, trends, and analysis.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class ReportGeneratorAgent(BaseAgent):
    """
    Generates comprehensive daily ICU reports in Turkish.

    This agent:
    - Loads all previous phase outputs (vitals, labs, critical, scores)
    - Loads historical data (2-3 days) for trend analysis
    - Generates Turkish markdown report with all sections
    - Provides specific, actionable recommendations
    - Formats professional medical report

    Uses prompt: prompts/reports/30-daily-report.md
    Saves to: 07_report.md
    """

    REQUIRED_SECTIONS = [
        "GENEL DURUM",
        "SİSTEM BAZLI DEĞERLENDİRME",
        "ÖNCELİKLİ SORUNLAR",
        "TEDAVİ ÖNERİLERİ"
    ]

    def __init__(self, state_manager, config=None):
        """
        Initialize the Report Generator Agent.

        Args:
            state_manager: StateManager instance
            config: Optional configuration dict
        """
        super().__init__(
            name="ReportGenerator",
            prompt_path="prompts/reports/30-daily-report.md",
            state_manager=state_manager,
            config=config,
        )

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare comprehensive input for report generation.

        Args:
            context: Dictionary containing all clinical data

        Returns:
            Formatted input string with all data and historical trends
        """
        # Load all phase outputs
        vitals_data = context.get("vitals_data") or self._load_state_json("vitals")
        labs_data = context.get("labs_data") or self._load_state_json("labs")
        parsed_data = context.get("parsed_data") or self._load_state_json("parsed")
        critical_data = context.get("critical_data") or self._load_state_json("critical")
        scores_data = context.get("scores_data") or self._load_state_json("scores")

        if not parsed_data:
            raise ValueError("No parsed clinical data found for report generation")

        # Load historical data
        history = self.state_manager.get_history(days=3)
        historical_summary = self._generate_historical_summary(history)

        # Extract patient demographics
        patient_info = parsed_data.get("patient_info", {})
        admission_info = parsed_data.get("admission_info", {})

        # Format comprehensive input
        input_text = f"""## HASTA BİLGİLERİ

**Hasta ID:** {self.state_manager.patient_id}
**Tarih:** {self.state_manager.date}
**Yaş:** {patient_info.get('age', 'N/A')} yaş
**Cinsiyet:** {patient_info.get('gender', 'N/A')}
**Tanı:** {admission_info.get('diagnosis', 'N/A')}
**Yatış Günü:** {admission_info.get('icu_day', 'N/A')}

---

## BUGÜNKÜ KLİNİK VERİLER

### Parsed Data
```json
{json.dumps(parsed_data, indent=2, ensure_ascii=False)}
```

### Vital Signs
```json
{json.dumps(vitals_data.get('vitals', {}) if vitals_data else {}, indent=2, ensure_ascii=False)}
```

### Laboratory Values
```json
{json.dumps(labs_data.get('labs', {}) if labs_data else {}, indent=2, ensure_ascii=False)}
```

### Critical Values
```json
{json.dumps(critical_data.get('critical_analysis', {}) if critical_data else {}, indent=2, ensure_ascii=False)}
```

### SOFA Score
```json
{json.dumps(scores_data.get('scores', {}) if scores_data else {}, indent=2, ensure_ascii=False)}
```

---

## TARİHSEL VERİLER (Trend Analizi)

{historical_summary}

---

## RAPOR OLUŞTURMA TALİMATLARI

Yukarıdaki tüm verileri kullanarak kapsamlı bir Türkçe günlük değerlendirme raporu oluştur.

**Önemli Kurallar:**
1. **SPESİFİK ÖNERİLER:** Genel öneriler değil, spesifik dozlar ve hedeflerle öneriler ver
   - YANLIŞ: "Vazopresör dozu ayarlanabilir"
   - DOĞRU: "Noradrenalin 0.15 → 0.10 mcg/kg/dk azaltma denenebilir, MAP ≥65 mmHg hedeflenerek"

2. **TREND ANALİZİ:** Her parametre için önceki değerlerle karşılaştırma yap
   - Laktat: [önceki] → [şimdi] ([↓ İyileşiyor / ↑ Kötüleşiyor])

3. **ACİL DURUMLAR:** Kritik değerler varsa önceliklendir ve vurgula

4. **TÜRKÇE:** Tüm rapor Türkçe olmalı, medikal terimler orijinal dilde kalabilir

5. **FORMAT:** Markdown formatında, emoji kullanarak okunabilir hale getir

Tüm bölümleri eksiksiz doldur ve SADECE markdown raporu döndür.
"""

        logger.info("Prepared comprehensive input for report generation")
        return input_text

    def validate_output(self, output: str) -> bool:
        """
        Validate that the output is a complete Turkish report.

        Args:
            output: Raw output from Claude

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check that output is non-empty markdown
            if not output or len(output.strip()) < 500:
                logger.warning("Report output too short")
                return False

            # Check for required sections
            for section in self.REQUIRED_SECTIONS:
                if section not in output:
                    logger.warning(f"Missing required section: {section}")
                    return False

            # Check for Turkish content (contains Turkish characters)
            turkish_chars = ['ş', 'ğ', 'ü', 'ö', 'ç', 'ı', 'İ', 'Ş', 'Ğ', 'Ü', 'Ö', 'Ç']
            has_turkish = any(char in output for char in turkish_chars)

            if not has_turkish:
                logger.warning("Report does not appear to be in Turkish")
                return False

            # Check that recommendations are specific (not generic)
            generic_phrases = [
                "ayarlanabilir",
                "değerlendirilebilir",
                "düşünülebilir"
            ]

            # Count generic vs specific recommendations
            generic_count = sum(output.lower().count(phrase) for phrase in generic_phrases)
            if generic_count > 10:
                logger.warning(f"Too many generic recommendations ({generic_count})")
                # Don't fail, just warn
                # return False

            logger.info("Report validation passed")
            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated report output.

        Args:
            output: Validated report markdown

        Returns:
            Dictionary containing the report and metadata
        """
        # Extract sections
        sections = self._extract_sections(output)

        # Count recommendations
        recommendations = self._count_recommendations(output)

        # Log summary
        logger.info(
            f"Generated report: "
            f"length={len(output)} chars, "
            f"sections={len(sections)}, "
            f"recommendations={recommendations}"
        )

        return {
            "report": output,
            "sections": sections,
            "recommendation_count": recommendations,
            "length": len(output),
            "generated_at": self.state_manager.workflow_status.get("started_at")
        }

    def _load_state_json(self, phase: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from a state phase."""
        state = self.state_manager.load(phase)
        if not state:
            return None

        try:
            # Try to extract JSON from markdown
            json_str = self._extract_json(state)
            return json.loads(json_str)
        except Exception as e:
            logger.debug(f"Could not load JSON from {phase}: {e}")
            return None

    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks if present."""
        text = text.strip()

        json_block_pattern = r"```json\s*(.*?)\s*```"
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        code_block_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        return text

    def _generate_historical_summary(self, history: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of historical data for trend analysis.

        Args:
            history: List of historical workflow statuses

        Returns:
            Formatted string with historical summary
        """
        if not history:
            return "**Geçmiş veri yok** (İlk gün değerlendirmesi)"

        summary_lines = []

        for i, day in enumerate(history[:3], 1):  # Last 3 days
            date = day.get("date", "N/A")
            patient_id = day.get("patient_id", "N/A")

            summary_lines.append(f"### Gün {i} ({date})")

            try:
                # Try to load scores for this day
                from agents.base.state import StateManager
                temp_sm = StateManager(patient_id, date)

                # Load SOFA score
                scores_state = temp_sm.load("scores")
                if scores_state:
                    scores_json = self._extract_json(scores_state)
                    scores_data = json.loads(scores_json)
                    sofa = scores_data.get("scores", {}).get("sofa", {})
                    total = sofa.get("total_score", "N/A")
                    summary_lines.append(f"- **SOFA:** {total}/24")

                # Load critical values
                critical_state = temp_sm.load("critical")
                if critical_state:
                    critical_json = self._extract_json(critical_state)
                    critical_data = json.loads(critical_json)
                    analysis = critical_data.get("critical_analysis", {})
                    summary_text = analysis.get("summary", {})
                    total_critical = summary_text.get("total_critical_values", 0)
                    summary_lines.append(f"- **Kritik Değerler:** {total_critical}")

            except Exception as e:
                logger.debug(f"Could not load history for {date}: {e}")
                summary_lines.append("- (Veri yüklenemedi)")

            summary_lines.append("")

        return "\n".join(summary_lines)

    def _extract_sections(self, report: str) -> Dict[str, str]:
        """
        Extract sections from the report.

        Args:
            report: Full report markdown

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}

        # Split by ## headers
        parts = re.split(r'\n## ', report)

        for part in parts[1:]:  # Skip first empty part
            lines = part.split('\n', 1)
            if len(lines) == 2:
                section_name = lines[0].strip()
                section_content = lines[1].strip()
                sections[section_name] = section_content

        return sections

    def _count_recommendations(self, report: str) -> int:
        """
        Count specific recommendations in the report.

        Args:
            report: Full report markdown

        Returns:
            Number of recommendations found
        """
        # Look for recommendation bullet points in "Öneriler" sections
        recommendation_pattern = r'^\s*[-*]\s+.+$'
        matches = re.findall(recommendation_pattern, report, re.MULTILINE)

        # Filter for lines that appear in recommendation sections
        in_recommendations_section = False
        count = 0

        for line in report.split('\n'):
            if 'Öneri' in line or 'PLAN' in line:
                in_recommendations_section = True
            elif line.startswith('##'):
                in_recommendations_section = False

            if in_recommendations_section and re.match(recommendation_pattern, line):
                count += 1

        return count

    def get_report_text(self, report_data: Dict[str, Any]) -> str:
        """
        Get the report markdown text.

        Args:
            report_data: Report data dictionary

        Returns:
            Report markdown string
        """
        return report_data.get("report", "")

    def get_sections(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Get report sections.

        Args:
            report_data: Report data dictionary

        Returns:
            Dictionary of sections
        """
        return report_data.get("sections", {})
