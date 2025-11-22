#!/usr/bin/env python
"""
ICU Agent Web Dashboard

A Flask-based web interface for monitoring ICU patients, viewing reports,
analyzing trends, and managing alerts.

Features:
- Real-time patient status dashboard
- Interactive trend charts
- Alert management panel
- Report browser
- SOFA score visualization
- Multi-patient overview

Run with:
    python web/app.py

Access at:
    http://localhost:5000
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, jsonify, request, send_file
from agents.base.state import StateManager
from agents.orchestrator import BatchProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'icu-agent-dashboard-secret-key'
app.config['JSON_SORT_KEYS'] = False

# Global configuration
CONFIG = {
    "patients_dir": Path("patients/active"),
    "state_dir": Path("state"),
    "refresh_interval": 30,  # seconds
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_active_patients() -> List[str]:
    """
    Get list of active patient IDs.

    Returns:
        List of patient ID strings
    """
    patients_dir = CONFIG["patients_dir"]
    if not patients_dir.exists():
        return []

    patient_ids = [
        p.name for p in patients_dir.iterdir()
        if p.is_dir() and not p.name.startswith('.')
    ]

    return sorted(patient_ids)


def get_patient_dates(patient_id: str, days: int = 7) -> List[str]:
    """
    Get available dates for a patient.

    Args:
        patient_id: Patient identifier
        days: Number of days to look back

    Returns:
        List of date strings (YYYY-MM-DD)
    """
    state_patient_dir = CONFIG["state_dir"] / patient_id
    if not state_patient_dir.exists():
        return []

    dates = [
        d.name for d in state_patient_dir.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ]

    # Sort by date descending
    dates = sorted(dates, reverse=True)[:days]

    return dates


def load_state_data(patient_id: str, date: str, phase: str) -> Optional[Dict[str, Any]]:
    """
    Load state data for a patient/date/phase.

    Args:
        patient_id: Patient identifier
        date: Date string
        phase: Phase name

    Returns:
        Parsed JSON data or None
    """
    try:
        sm = StateManager(patient_id, date)
        content = sm.load(phase)

        if not content:
            return None

        # Try to extract JSON
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to parse as plain JSON
        return json.loads(content)

    except Exception as e:
        logger.debug(f"Could not load {phase} for {patient_id}/{date}: {e}")
        return None


def get_patient_summary(patient_id: str) -> Dict[str, Any]:
    """
    Get summary information for a patient.

    Args:
        patient_id: Patient identifier

    Returns:
        Summary dictionary
    """
    dates = get_patient_dates(patient_id, days=1)

    if not dates:
        return {
            "patient_id": patient_id,
            "status": "no_data",
            "last_update": None,
        }

    latest_date = dates[0]

    # Load latest data
    parsed_data = load_state_data(patient_id, latest_date, "parsed")
    scores_data = load_state_data(patient_id, latest_date, "scores")
    critical_data = load_state_data(patient_id, latest_date, "critical")
    alerts_data = load_state_data(patient_id, latest_date, "alerts")

    # Extract key information
    patient_info = parsed_data.get("patient_info", {}) if parsed_data else {}

    sofa_score = -1
    if scores_data:
        sofa = scores_data.get("scores", {}).get("sofa", {})
        sofa_score = sofa.get("total_score", -1)

    critical_count = 0
    if critical_data:
        analysis = critical_data.get("critical_analysis", {})
        summary = analysis.get("summary", {})
        critical_count = summary.get("total_critical_values", 0)

    immediate_alerts = 0
    if alerts_data:
        alerts = alerts_data.get("alerts", [])
        immediate_alerts = sum(1 for a in alerts if a.get("urgency") == "immediate")

    return {
        "patient_id": patient_id,
        "status": "active",
        "last_update": latest_date,
        "age": patient_info.get("age"),
        "gender": patient_info.get("gender"),
        "sofa_score": sofa_score,
        "critical_count": critical_count,
        "immediate_alerts": immediate_alerts,
    }


# ============================================================================
# WEB ROUTES - PAGES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page showing all patients."""
    return render_template('index.html')


@app.route('/patient/<patient_id>')
def patient_detail(patient_id: str):
    """Patient detail page with trends and history."""
    return render_template('patient.html', patient_id=patient_id)


@app.route('/alerts')
def alerts_page():
    """Alerts management page."""
    return render_template('alerts.html')


@app.route('/reports')
def reports_page():
    """Reports browser page."""
    return render_template('reports.html')


# ============================================================================
# API ROUTES - DATA
# ============================================================================

@app.route('/api/patients')
def api_patients():
    """
    Get list of all active patients with summary information.

    Returns:
        JSON array of patient summaries
    """
    patient_ids = get_active_patients()
    patients = [get_patient_summary(pid) for pid in patient_ids]

    return jsonify({
        "patients": patients,
        "count": len(patients),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/patient/<patient_id>')
def api_patient_detail(patient_id: str):
    """
    Get detailed information for a specific patient.

    Args:
        patient_id: Patient identifier

    Returns:
        JSON with patient details
    """
    dates = get_patient_dates(patient_id, days=7)

    if not dates:
        return jsonify({"error": "No data found for patient"}), 404

    latest_date = dates[0]

    # Load all phases for latest date
    parsed_data = load_state_data(patient_id, latest_date, "parsed")
    vitals_data = load_state_data(patient_id, latest_date, "vitals")
    labs_data = load_state_data(patient_id, latest_date, "labs")
    trends_data = load_state_data(patient_id, latest_date, "trends")
    critical_data = load_state_data(patient_id, latest_date, "critical")
    scores_data = load_state_data(patient_id, latest_date, "scores")
    alerts_data = load_state_data(patient_id, latest_date, "alerts")

    return jsonify({
        "patient_id": patient_id,
        "date": latest_date,
        "available_dates": dates,
        "parsed": parsed_data,
        "vitals": vitals_data,
        "labs": labs_data,
        "trends": trends_data,
        "critical": critical_data,
        "scores": scores_data,
        "alerts": alerts_data,
    })


@app.route('/api/patient/<patient_id>/trends')
def api_patient_trends(patient_id: str):
    """
    Get trend data for a patient over multiple days.

    Args:
        patient_id: Patient identifier

    Query params:
        days: Number of days to retrieve (default: 7)

    Returns:
        JSON with trend timeseries
    """
    days = int(request.args.get('days', 7))
    dates = get_patient_dates(patient_id, days=days)

    # Build timeseries data
    sofa_series = []
    lactate_series = []
    creatinine_series = []
    platelets_series = []

    for date in reversed(dates):  # Oldest to newest
        # Load SOFA
        scores_data = load_state_data(patient_id, date, "scores")
        if scores_data:
            sofa = scores_data.get("scores", {}).get("sofa", {})
            total = sofa.get("total_score")
            if total is not None:
                sofa_series.append({"date": date, "value": total})

        # Load labs
        labs_data = load_state_data(patient_id, date, "labs")
        if labs_data:
            lab_values = labs_data.get("lab_values", {})

            # Lactate
            lactate = lab_values.get("chemistry", {}).get("lactate", {}).get("value")
            if lactate is not None:
                lactate_series.append({"date": date, "value": lactate})

            # Creatinine
            creat = lab_values.get("chemistry", {}).get("creatinine", {}).get("value")
            if creat is not None:
                creatinine_series.append({"date": date, "value": creat})

            # Platelets
            plts = lab_values.get("hematology", {}).get("platelets", {}).get("value")
            if plts is not None:
                platelets_series.append({"date": date, "value": plts})

    return jsonify({
        "patient_id": patient_id,
        "sofa": sofa_series,
        "lactate": lactate_series,
        "creatinine": creatinine_series,
        "platelets": platelets_series,
    })


@app.route('/api/alerts')
def api_all_alerts():
    """
    Get all active alerts across all patients.

    Returns:
        JSON array of alerts
    """
    all_alerts = []

    patient_ids = get_active_patients()

    for patient_id in patient_ids:
        dates = get_patient_dates(patient_id, days=1)
        if not dates:
            continue

        latest_date = dates[0]
        alerts_data = load_state_data(patient_id, latest_date, "alerts")

        if alerts_data:
            alerts = alerts_data.get("alerts", [])
            for alert in alerts:
                alert["patient_id"] = patient_id
                alert["date"] = latest_date
                all_alerts.append(alert)

    # Sort by urgency (immediate first)
    urgency_order = {"immediate": 0, "urgent": 1, "monitor": 2}
    all_alerts.sort(key=lambda a: urgency_order.get(a.get("urgency", "monitor"), 3))

    return jsonify({
        "alerts": all_alerts,
        "count": len(all_alerts),
        "immediate_count": sum(1 for a in all_alerts if a.get("urgency") == "immediate"),
        "urgent_count": sum(1 for a in all_alerts if a.get("urgency") == "urgent"),
        "monitor_count": sum(1 for a in all_alerts if a.get("urgency") == "monitor"),
    })


@app.route('/api/report/<patient_id>/<date>')
def api_patient_report(patient_id: str, date: str):
    """
    Get report for a specific patient and date.

    Args:
        patient_id: Patient identifier
        date: Date string (YYYY-MM-DD)

    Returns:
        Report content as markdown or JSON
    """
    sm = StateManager(patient_id, date)
    report_content = sm.load("report")

    if not report_content:
        return jsonify({"error": "Report not found"}), 404

    format_type = request.args.get('format', 'markdown')

    if format_type == 'json':
        return jsonify({
            "patient_id": patient_id,
            "date": date,
            "content": report_content
        })
    else:
        # Return as plain text markdown
        return report_content, 200, {'Content-Type': 'text/markdown; charset=utf-8'}


@app.route('/api/stats')
def api_system_stats():
    """
    Get system-wide statistics.

    Returns:
        JSON with system stats
    """
    patient_ids = get_active_patients()
    total_patients = len(patient_ids)

    active_patients = 0
    total_critical = 0
    total_immediate = 0
    high_sofa_count = 0

    for patient_id in patient_ids:
        dates = get_patient_dates(patient_id, days=1)
        if dates:
            active_patients += 1

            latest_date = dates[0]

            # Count critical values
            critical_data = load_state_data(patient_id, latest_date, "critical")
            if critical_data:
                analysis = critical_data.get("critical_analysis", {})
                summary = analysis.get("summary", {})
                total_critical += summary.get("total_critical_values", 0)

            # Count immediate alerts
            alerts_data = load_state_data(patient_id, latest_date, "alerts")
            if alerts_data:
                alerts = alerts_data.get("alerts", [])
                total_immediate += sum(1 for a in alerts if a.get("urgency") == "immediate")

            # Count high SOFA
            scores_data = load_state_data(patient_id, latest_date, "scores")
            if scores_data:
                sofa = scores_data.get("scores", {}).get("sofa", {})
                total_score = sofa.get("total_score", 0)
                if total_score >= 10:
                    high_sofa_count += 1

    return jsonify({
        "total_patients": total_patients,
        "active_patients": active_patients,
        "total_critical_values": total_critical,
        "total_immediate_alerts": total_immediate,
        "high_sofa_patients": high_sofa_count,
        "timestamp": datetime.now().isoformat()
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting ICU Agent Web Dashboard...")
    logger.info("Access at: http://localhost:5000")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
