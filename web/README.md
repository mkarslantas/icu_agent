# ICU Agent Web Dashboard

A Flask-based web interface for monitoring ICU patients, viewing reports, analyzing trends, and managing alerts.

## Features

### 🏥 Main Dashboard
- Real-time patient status overview
- System-wide statistics (active patients, immediate alerts, critical values, high SOFA scores)
- Patient table with key metrics (age, gender, SOFA score, critical values, alerts)
- Color-coded status indicators
- Quick navigation to patient details
- Auto-refresh every 30 seconds

### 👤 Patient Detail View
- Comprehensive patient information
- Interactive trend charts:
  - SOFA Score (7-day trend)
  - Lactate levels
  - Creatinine levels
  - Platelet count
- Current alerts with urgency levels
- Latest clinical report display
- Historical data access

### 🔔 Alerts Management
- System-wide alert aggregation
- Three-tier urgency classification:
  - **Immediate (ACİL)**: Life-threatening, requires instant intervention
  - **Urgent (ÖNEMLİ)**: Significant abnormality, needs attention within 1-2 hours
  - **Monitor (TAKİP)**: Concerning trend, requires close monitoring
- Alert filtering by urgency level
- Detailed recommendations in Turkish
- Patient linking from alerts
- Auto-refresh for real-time updates

### 📄 Reports Browser
- Patient selector dropdown
- Date range selector
- Formatted report display
- Download reports as markdown
- Report rendering with proper formatting

## Technology Stack

- **Backend**: Flask 3.0+
- **Frontend**: Bootstrap 5.3
- **Charts**: Chart.js 4.4
- **Icons**: Bootstrap Icons
- **Styling**: Custom CSS with responsive design

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the ICU Agent system has processed some patients (state files exist in `state/` directory)

## Usage

### Start the Web Server

```bash
# From the project root directory
python web/app.py
```

Or:

```bash
# Using the web module directly
python -m web.app
```

The dashboard will be accessible at:
- **URL**: http://localhost:5000
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 5000 (configurable in app.py)

### Development Mode

The application runs in debug mode by default for development:
- Auto-reloads on code changes
- Detailed error pages
- Debug logging enabled

For production deployment, set `debug=False` in `app.py`.

## API Endpoints

### Patient Data

- `GET /api/patients` - List all active patients with summaries
- `GET /api/patient/<patient_id>` - Get detailed patient information
- `GET /api/patient/<patient_id>/trends?days=7` - Get trend timeseries data

### Alerts

- `GET /api/alerts` - Get all active alerts across all patients

### Reports

- `GET /api/report/<patient_id>/<date>` - Get patient report
  - Query param: `format=json` for JSON format (default: markdown)

### System Stats

- `GET /api/stats` - Get system-wide statistics

## Configuration

Edit `web/app.py` to configure:

```python
CONFIG = {
    "patients_dir": Path("patients/active"),  # Active patients directory
    "state_dir": Path("state"),               # State files directory
    "refresh_interval": 30,                   # Auto-refresh interval (seconds)
}
```

Flask app configuration:
```python
app.run(
    host='0.0.0.0',     # Listen on all interfaces
    port=5000,          # Port number
    debug=True          # Debug mode
)
```

## File Structure

```
web/
├── app.py                      # Main Flask application
├── README.md                   # This file
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Main dashboard
│   ├── patient.html           # Patient detail view
│   ├── alerts.html            # Alerts management
│   └── reports.html           # Reports browser
└── static/                     # Static assets
    ├── css/
    │   └── dashboard.css      # Custom styles
    └── js/
        └── dashboard.js       # Common JavaScript functions
```

## Features in Detail

### Real-time Updates

- Auto-refresh every 30 seconds
- Manual refresh button with visual feedback
- Pauses when tab is hidden to save resources
- Live timestamp updates

### Responsive Design

- Mobile-friendly layout
- Collapsible navigation on small screens
- Responsive tables and charts
- Touch-friendly interface

### Data Visualization

- Line charts for parameter trends
- Color-coded badges for severity levels
- Visual status indicators
- Interactive charts with tooltips

### Accessibility

- Semantic HTML structure
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast color schemes

### Security

- Input sanitization
- XSS protection
- CSRF tokens (recommended for production)
- Secure headers (configure in production)

## Production Deployment

For production deployment, consider:

1. **Security**:
   - Set `SECRET_KEY` to a random secure value
   - Enable CSRF protection
   - Use HTTPS (reverse proxy with nginx/Apache)
   - Implement authentication/authorization
   - Set secure headers

2. **Performance**:
   - Use a production WSGI server (gunicorn, uWSGI)
   - Enable caching (Redis, Memcached)
   - Configure database connections pooling
   - Optimize static asset delivery (CDN)

3. **Reliability**:
   - Set up monitoring (Sentry, New Relic)
   - Configure logging (file rotation, centralized logging)
   - Implement health check endpoints
   - Use process manager (systemd, supervisord)

### Example Production Setup with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app

# With systemd service
sudo systemctl enable icu-agent-dashboard
sudo systemctl start icu-agent-dashboard
```

## Troubleshooting

### Dashboard shows "No patients found"

**Cause**: No state files in the configured directory

**Solution**:
1. Verify `state/` directory exists and contains patient data
2. Process at least one patient using the CLI: `icu-agent process-patient -p HT001 -d 2025-11-20`
3. Check `CONFIG["state_dir"]` path in `app.py`

### Charts not displaying

**Cause**: Missing trend data or JavaScript errors

**Solution**:
1. Check browser console for JavaScript errors
2. Verify patient has multiple days of data for trends
3. Ensure Chart.js CDN is accessible

### "Error loading data" messages

**Cause**: API endpoint errors or missing data files

**Solution**:
1. Check Flask console for error messages
2. Verify state file permissions
3. Check that required JSON data is valid
4. Review Flask logs for detailed error traces

### Port already in use

**Cause**: Another service is using port 5000

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change port in app.py
app.run(port=5001)
```

## Development

### Adding New Pages

1. Create HTML template in `templates/`
2. Add route in `app.py`:
```python
@app.route('/newpage')
def newpage():
    return render_template('newpage.html')
```

### Adding New API Endpoints

1. Add route in `app.py`:
```python
@app.route('/api/newdata')
def api_newdata():
    data = get_data()
    return jsonify(data)
```

### Customizing Styles

Edit `static/css/dashboard.css` to customize:
- Colors and themes
- Typography
- Layout and spacing
- Component styles

## Browser Compatibility

Tested and supported on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## License

Part of the ICU Agent Multi-Agent Monitoring System.

## Support

For issues and questions:
- Check troubleshooting section above
- Review Flask logs for errors
- Ensure all dependencies are installed
- Verify state files exist and are valid JSON
