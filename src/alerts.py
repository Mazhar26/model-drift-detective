"""
alerts.py — Email alert system for drift notifications.

Sends email alerts when significant drift is detected.
Controlled via environment variables (disabled by default).
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# ── Alert Configuration (from environment) ──
ALERTS_ENABLED = os.getenv("ALERTS_ENABLED", "false").lower() == "true"
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.3"))
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def send_drift_alert(feature_name, drift_score, severity, recommendation="Monitor and investigate"):
    """
    Send an email alert for a drifted feature.

    Args:
        feature_name: Name of the feature with drift.
        drift_score: KS-test drift score.
        severity: Drift severity (high/medium/low).
        recommendation: Suggested action string.

    Returns:
        True if alert was sent successfully, False otherwise.
    """
    # Guard: check if alerts are enabled
    if not ALERTS_ENABLED:
        logger.debug("Alerts disabled — skipping alert for %s", feature_name)
        return False

    # Guard: only alert above threshold
    if drift_score < ALERT_THRESHOLD:
        logger.debug(
            "Drift score %.4f below alert threshold %.4f for %s — skipping",
            drift_score,
            ALERT_THRESHOLD,
            feature_name,
        )
        return False

    # Guard: check email config
    if not ALERT_EMAIL_FROM or not ALERT_EMAIL_TO or not SMTP_PASSWORD:
        logger.warning(
            "Alert email config incomplete — FROM=%s, TO=%s, PASSWORD=%s",
            bool(ALERT_EMAIL_FROM),
            bool(ALERT_EMAIL_TO),
            bool(SMTP_PASSWORD),
        )
        return False

    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 Drift Alert — {severity.upper()} drift detected in {feature_name}"
        msg["From"] = ALERT_EMAIL_FROM
        msg["To"] = ALERT_EMAIL_TO

        # Plain text body
        text_body = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 MODEL DRIFT ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature:        {feature_name}
Drift Score:    {drift_score:.4f}
Severity:       {severity.upper()}
Timestamp:      {timestamp}

Recommended Action:
{recommendation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This alert was sent by Model Drift Detective.
Configure alerts in your .env file.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # HTML body
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #16213e; border-radius: 12px;
              padding: 30px; border: 1px solid #0f3460;">
    <h1 style="color: #e94560; margin-top: 0;">🚨 Model Drift Alert</h1>
    <hr style="border-color: #0f3460;">

    <table style="width: 100%; margin: 20px 0;">
      <tr>
        <td style="color: #a89f91; padding: 8px 0;">Feature</td>
        <td style="font-weight: bold; padding: 8px 0;">{feature_name}</td>
      </tr>
      <tr>
        <td style="color: #a89f91; padding: 8px 0;">Drift Score</td>
        <td style="font-weight: bold; color: #e94560; padding: 8px 0;">{drift_score:.4f}</td>
      </tr>
      <tr>
        <td style="color: #a89f91; padding: 8px 0;">Severity</td>
        <td style="padding: 8px 0;">
          <span style="background: {'#e94560' if severity == 'high'
                                    else '#f0a500' if severity == 'medium'
                                    else '#4ecca3'};
                       color: #fff; padding: 4px 12px; border-radius: 4px; font-weight: bold;">
            {severity.upper()}
          </span>
        </td>
      </tr>
      <tr>
        <td style="color: #a89f91; padding: 8px 0;">Timestamp</td>
        <td style="padding: 8px 0;">{timestamp}</td>
      </tr>
    </table>

    <div style="background: #0f3460; padding: 15px; border-radius: 8px; margin: 20px 0;">
      <strong style="color: #4ecca3;">📋 Recommended Action:</strong>
      <p style="margin: 8px 0 0 0;">{recommendation}</p>
    </div>

    <hr style="border-color: #0f3460;">
    <p style="color: #666; font-size: 12px; margin-bottom: 0;">
      Sent by Model Drift Detective • Configure alerts in .env
    </p>
  </div>
</body>
</html>
"""

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Send via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(ALERT_EMAIL_FROM, SMTP_PASSWORD)
            server.sendmail(ALERT_EMAIL_FROM, ALERT_EMAIL_TO, msg.as_string())

        logger.info(
            "Alert sent for %s (score=%.4f, severity=%s) to %s",
            feature_name,
            drift_score,
            severity,
            ALERT_EMAIL_TO,
        )
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check credentials in .env")
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending alert for %s: %s", feature_name, e)
        return False
    except Exception as e:
        logger.error("Failed to send alert for %s: %s", feature_name, e)
        return False


def check_and_alert(drift_results, recommendations=None):
    """
    Check all drift results and send alerts for features exceeding the threshold.

    Args:
        drift_results: Dict of feature→drift info from detect_drift().
        recommendations: Optional dict of feature→action strings.

    Returns:
        Dict with alert_count and alerts_sent list.
    """
    alerts_sent = []
    alerts_skipped = 0

    for feature, result in drift_results.items():
        if not result.get("drift_detected", False):
            continue

        drift_score = result.get("drift_score", 0)
        severity = result.get("severity", "low")
        rec = (recommendations or {}).get(feature, "Monitor and investigate")

        sent = send_drift_alert(feature, drift_score, severity, rec)

        if sent:
            alerts_sent.append(feature)
        else:
            alerts_skipped += 1

    if alerts_sent:
        logger.info("Alerts sent for %d features: %s", len(alerts_sent), alerts_sent)
    else:
        logger.debug("No alerts sent (sent=%d, skipped=%d)", len(alerts_sent), alerts_skipped)

    return {
        "alerts_enabled": ALERTS_ENABLED,
        "alert_threshold": ALERT_THRESHOLD,
        "alerts_sent": alerts_sent,
        "alerts_skipped": alerts_skipped,
    }
