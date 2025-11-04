"""
Notification API clients for PreFlight AI
Integrates Twilio (SMS), SendGrid (Email), and Slack
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
import requests
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException


class NotificationError(Exception):
    """Custom exception for notification errors"""

    pass


# ============================================================================
# Twilio SMS Client
# ============================================================================


class SMSNotificationService:
    """
    SMS notification service using Twilio.
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_PHONE_NUMBER")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio credentials not fully configured")

        self.client = TwilioClient(self.account_sid, self.auth_token)

    def send_crew_alert(
        self, flight_id: str, delay_minutes: int, crew_phone: str, additional_info: str = ""
    ) -> Dict:
        """
        Send SMS alert to crew about predicted delay.

        Args:
            flight_id: Flight identifier
            delay_minutes: Predicted delay in minutes
            crew_phone: Crew member phone number (E.164 format, e.g., +14155552671)
            additional_info: Additional context

        Returns:
            dict: Message delivery status
        """
        message_body = f"""
🚨 PREFLIGHT AI ALERT

Flight: {flight_id}
Predicted Delay: {delay_minutes} min
Risk Level: {"HIGH" if delay_minutes > 30 else "MODERATE"}

{additional_info}

Recommend early crew check-in.
View details: https://preflight.ai/flights/{flight_id}
        """.strip()

        try:
            message = self.client.messages.create(
                body=message_body, from_=self.from_number, to=crew_phone
            )

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": crew_phone,
                "sent_at": datetime.now().isoformat(),
            }

        except TwilioRestException as e:
            raise NotificationError(f"Twilio SMS error: {e.msg}")

    def send_passenger_alert(
        self, flight_id: str, delay_minutes: int, passenger_phone: str
    ) -> Dict:
        """
        Send SMS alert to passenger about delay.
        """
        message_body = f"""
Dear Passenger,

Your flight {flight_id} is experiencing a predicted delay of {delay_minutes} minutes.

We recommend arriving at the gate 15 minutes earlier than usual.

For real-time updates, check your airline app.

- PreFlight AI
        """.strip()

        try:
            message = self.client.messages.create(
                body=message_body, from_=self.from_number, to=passenger_phone
            )

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": passenger_phone,
                "sent_at": datetime.now().isoformat(),
            }

        except TwilioRestException as e:
            raise NotificationError(f"Twilio SMS error: {e.msg}")

    def send_bulk_sms(self, recipients: List[Dict]) -> List[Dict]:
        """
        Send SMS to multiple recipients.

        Args:
            recipients: List of dicts with 'phone' and 'message' keys

        Returns:
            list: Delivery status for each message
        """
        results = []
        for recipient in recipients:
            try:
                message = self.client.messages.create(
                    body=recipient["message"],
                    from_=self.from_number,
                    to=recipient["phone"],
                )
                results.append(
                    {
                        "phone": recipient["phone"],
                        "success": True,
                        "message_sid": message.sid,
                    }
                )
            except TwilioRestException as e:
                results.append(
                    {"phone": recipient["phone"], "success": False, "error": str(e)}
                )

        return results


# ============================================================================
# SendGrid Email Client
# ============================================================================


class EmailNotificationService:
    """
    Email notification service using SendGrid.
    """

    BASE_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", "alerts@preflight.ai")

        if not self.api_key:
            raise ValueError("SendGrid API key not configured")

        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        )

    def send_operations_alert(
        self,
        flight_id: str,
        delay_prob: float,
        predicted_delay: int,
        shap_values: Dict,
        explanation: str,
        to_emails: List[str],
    ) -> Dict:
        """
        Send detailed alert email to operations team.

        Args:
            flight_id: Flight identifier
            delay_prob: Delay probability (0-1)
            predicted_delay: Predicted delay in minutes
            shap_values: SHAP explanation values
            explanation: Natural language explanation
            to_emails: List of recipient email addresses

        Returns:
            dict: Email delivery status
        """
        html_content = self._generate_alert_html(
            flight_id, delay_prob, predicted_delay, shap_values, explanation
        )

        payload = {
            "personalizations": [{"to": [{"email": email} for email in to_emails]}],
            "from": {"email": self.from_email, "name": "PreFlight AI"},
            "subject": f"🚨 High Risk Alert: Flight {flight_id} - {int(delay_prob * 100)}% Delay Probability",
            "content": [
                {"type": "text/plain", "value": explanation},
                {"type": "text/html", "value": html_content},
            ],
        }

        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=10)
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "recipients": to_emails,
                "sent_at": datetime.now().isoformat(),
            }

        except requests.exceptions.RequestException as e:
            raise NotificationError(f"SendGrid email error: {str(e)}")

    def send_daily_report(self, report_data: Dict, to_emails: List[str]) -> Dict:
        """
        Send daily operations report.
        """
        html_content = self._generate_daily_report_html(report_data)

        payload = {
            "personalizations": [{"to": [{"email": email} for email in to_emails]}],
            "from": {"email": self.from_email, "name": "PreFlight AI"},
            "subject": f"📊 Daily Operations Report - {report_data.get('date', 'Today')}",
            "content": [{"type": "text/html", "value": html_content}],
        }

        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=10)
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "recipients": to_emails,
                "sent_at": datetime.now().isoformat(),
            }

        except requests.exceptions.RequestException as e:
            raise NotificationError(f"SendGrid email error: {str(e)}")

    def _generate_alert_html(
        self, flight_id, delay_prob, predicted_delay, shap_values, explanation
    ) -> str:
        """Generate HTML email for flight alert."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f0f0f; color: #fff; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #1a1a1a; border: 1px solid #B6FF2B; border-radius: 8px; padding: 30px; }}
        .header {{ text-align: center; color: #B6FF2B; margin-bottom: 20px; }}
        .alert-box {{ background: rgba(182, 255, 43, 0.1); border-left: 4px solid #B6FF2B; padding: 15px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-label {{ color: #888; font-size: 12px; text-transform: uppercase; }}
        .metric-value {{ color: #B6FF2B; font-size: 24px; font-weight: bold; }}
        .factors {{ margin: 20px 0; }}
        .factor {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #222; border-radius: 4px; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 PreFlight AI Alert</h1>
            <h2>High Risk Flight Detected</h2>
        </div>
        
        <div class="alert-box">
            <h3>Flight: {flight_id}</h3>
            <div class="metric">
                <div class="metric-label">Delay Probability</div>
                <div class="metric-value">{int(delay_prob * 100)}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Predicted Delay</div>
                <div class="metric-value">{predicted_delay} min</div>
            </div>
        </div>
        
        <h3>AI Explanation</h3>
        <p>{explanation}</p>
        
        <h3>Contributing Factors</h3>
        <div class="factors">
            {"".join([f'<div class="factor"><span>{k}</span><span style="color: #B6FF2B;">{v}</span></div>' for k, v in shap_values.items()])}
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://preflight.ai/flights/{flight_id}" 
               style="background: #B6FF2B; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                View Full Details
            </a>
        </div>
        
        <div class="footer">
            PreFlight AI - Intelligent Flight Operations<br>
            Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        </div>
    </div>
</body>
</html>
        """

    def _generate_daily_report_html(self, report_data: Dict) -> str:
        """Generate HTML for daily report."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ color: #333; border-bottom: 3px solid #B6FF2B; padding-bottom: 15px; margin-bottom: 25px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f9f9f9; padding: 20px; border-radius: 6px; border-left: 4px solid #B6FF2B; }}
        .stat-label {{ color: #666; font-size: 14px; margin-bottom: 8px; }}
        .stat-value {{ color: #B6FF2B; font-size: 32px; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Operations Report</h1>
            <p>{report_data.get('date', 'Today')}</p>
        </div>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Total Flights</div>
                <div class="stat-value">{report_data.get('total_flights', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Predictions Made</div>
                <div class="stat-value">{report_data.get('predictions', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Alerts Triggered</div>
                <div class="stat-value">{report_data.get('alerts', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Delay</div>
                <div class="stat-value">{report_data.get('avg_delay', 0)} min</div>
            </div>
        </div>
        
        <div class="footer">
            PreFlight AI - Your Intelligent Aviation Partner<br>
            © 2025 PreFlight AI. All rights reserved.
        </div>
    </div>
</body>
</html>
        """


# ============================================================================
# Slack Webhook Client
# ============================================================================


class SlackNotificationService:
    """
    Slack notification service using webhooks.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

        if not self.webhook_url:
            raise ValueError("Slack webhook URL not configured")

        self.session = requests.Session()

    def post_alert(
        self, flight_id: str, delay_prob: float, predicted_delay: int, key_factors: Dict
    ) -> Dict:
        """
        Post alert to Slack channel.

        Args:
            flight_id: Flight identifier
            delay_prob: Delay probability (0-1)
            predicted_delay: Predicted delay in minutes
            key_factors: Top contributing factors

        Returns:
            dict: Post status
        """
        # Format factors for display
        factors_text = "\n".join(
            [f"• *{k}*: {v}" for k, v in list(key_factors.items())[:3]]
        )

        payload = {
            "text": f"🚨 High Risk Flight Detected: {flight_id}",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🚨 High Risk: {flight_id}"},
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Delay Probability:*\n{int(delay_prob * 100)}%",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Predicted Delay:*\n{predicted_delay} min",
                        },
                    ],
                },
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top Factors:*\n{factors_text}"}},
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Dashboard"},
                            "url": f"https://preflight.ai/flights/{flight_id}",
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Acknowledge"},
                            "value": flight_id,
                        },
                    ],
                },
            ],
        }

        try:
            response = self.session.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "sent_at": datetime.now().isoformat(),
            }

        except requests.exceptions.RequestException as e:
            raise NotificationError(f"Slack webhook error: {str(e)}")

    def post_daily_summary(self, summary_data: Dict) -> Dict:
        """
        Post daily summary to Slack.
        """
        payload = {
            "text": "📊 Daily Operations Summary",
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": "📊 Daily Operations Summary"}},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Total Flights:*\n{summary_data.get('total_flights', 0)}"},
                        {"type": "mrkdwn", "text": f"*Alerts:*\n{summary_data.get('alerts', 0)}"},
                        {"type": "mrkdwn", "text": f"*Avg Delay:*\n{summary_data.get('avg_delay', 0)} min"},
                        {"type": "mrkdwn", "text": f"*Accuracy:*\n{summary_data.get('accuracy', 0)}%"},
                    ],
                },
            ],
        }

        try:
            response = self.session.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            return {"success": True, "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            raise NotificationError(f"Slack webhook error: {str(e)}")


# ============================================================================
# Unified Notification Service
# ============================================================================


class NotificationService:
    """
    Unified notification service managing all channels.
    """

    def __init__(self):
        try:
            self.sms = SMSNotificationService()
        except ValueError:
            self.sms = None
            print("Warning: SMS notifications not configured")

        try:
            self.email = EmailNotificationService()
        except ValueError:
            self.email = None
            print("Warning: Email notifications not configured")

        try:
            self.slack = SlackNotificationService()
        except ValueError:
            self.slack = None
            print("Warning: Slack notifications not configured")

    def send_high_risk_alert(
        self, flight_data: Dict, crew_phone: Optional[str] = None, ops_emails: Optional[List[str]] = None
    ) -> Dict:
        """
        Send high-risk alert across all configured channels.

        Args:
            flight_data: Flight and prediction data
            crew_phone: Optional crew phone for SMS
            ops_emails: Optional operations team emails

        Returns:
            dict: Status of each notification channel
        """
        results = {"sms": None, "email": None, "slack": None}

        # Send SMS to crew
        if self.sms and crew_phone:
            try:
                results["sms"] = self.sms.send_crew_alert(
                    flight_data["flight_id"],
                    flight_data["predicted_delay"],
                    crew_phone,
                    additional_info=f"Primary factor: {flight_data.get('primary_factor', 'Unknown')}",
                )
            except NotificationError as e:
                results["sms"] = {"success": False, "error": str(e)}

        # Send email to ops team
        if self.email and ops_emails:
            try:
                results["email"] = self.email.send_operations_alert(
                    flight_data["flight_id"],
                    flight_data["delay_prob"],
                    flight_data["predicted_delay"],
                    flight_data.get("shap_values", {}),
                    flight_data.get("explanation", ""),
                    ops_emails,
                )
            except NotificationError as e:
                results["email"] = {"success": False, "error": str(e)}

        # Post to Slack
        if self.slack:
            try:
                results["slack"] = self.slack.post_alert(
                    flight_data["flight_id"],
                    flight_data["delay_prob"],
                    flight_data["predicted_delay"],
                    flight_data.get("key_factors", {}),
                )
            except NotificationError as e:
                results["slack"] = {"success": False, "error": str(e)}

        return results


def get_notification_service() -> NotificationService:
    """Get singleton notification service instance."""
    return NotificationService()


__all__ = [
    "NotificationError",
    "SMSNotificationService",
    "EmailNotificationService",
    "SlackNotificationService",
    "NotificationService",
    "get_notification_service",
]
