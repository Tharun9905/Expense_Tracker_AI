"""
Enhanced Email Service with Node Mailer-like features
Improved Python SMTP integration with better error handling and features
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Enhanced Email Service with Node Mailer-like functionality"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_username)
        self.sender_name = os.environ.get('SMTP_SENDER_NAME', 'Expense Tracker Notifications')
        
        # Provider-specific settings
        self.provider = self._detect_provider()
        
        # Validate configuration
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
    
    def _detect_provider(self) -> str:
        """Detect email provider based on SMTP server"""
        if 'gmail' in self.smtp_server.lower():
            return 'gmail'
        elif 'outlook' in self.smtp_server.lower() or 'office365' in self.smtp_server.lower():
            return 'outlook'
        elif 'sendgrid' in self.smtp_server.lower():
            return 'sendgrid'
        elif 'smtp.com' in self.smtp_server.lower():
            return 'smtp_com'
        elif 'brevo' in self.smtp_server.lower() or 'sendinblue' in self.smtp_server.lower():
            return 'brevo'
        else:
            return 'generic'
    
    def send_mail(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email with Node Mailer-like interface
        
        Args:
            options: Dictionary with email options
                - to: recipient email(s) (string or list)
                - subject: email subject
                - text: plain text content (optional)
                - html: HTML content (optional)
                - attachments: list of file paths (optional)
                - cc: CC recipients (optional)
                - bcc: BCC recipients (optional)
        
        Returns:
            Dictionary with success status and message info
        """
        try:
            # Validate required fields
            if not options.get('to'):
                return {'success': False, 'error': 'Recipient email is required'}
            
            if not options.get('subject'):
                return {'success': False, 'error': 'Subject is required'}
            
            if not options.get('text') and not options.get('html'):
                return {'success': False, 'error': 'Either text or html content is required'}
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = options['subject']
            
            # Professional sender with name
            sender_email = options.get('from', self.from_email)
            sender_name = options.get('from_name', self.sender_name)
            msg['From'] = f"{sender_name} <{sender_email}>"
            
            # Handle recipients
            recipients = self._normalize_recipients(options['to'])
            msg['To'] = ', '.join(recipients)
            
            # Handle CC
            cc_recipients = []
            if options.get('cc'):
                cc_recipients = self._normalize_recipients(options['cc'])
                msg['Cc'] = ', '.join(cc_recipients)
            
            # Handle BCC
            bcc_recipients = []
            if options.get('bcc'):
                bcc_recipients = self._normalize_recipients(options['bcc'])
            
            # All recipients for sending
            all_recipients = recipients + cc_recipients + bcc_recipients
            
            # Add text content
            if options.get('text'):
                text_part = MIMEText(options['text'], 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            if options.get('html'):
                html_part = MIMEText(options['html'], 'html')
                msg.attach(html_part)
            
            # Add attachments
            if options.get('attachments'):
                self._add_attachments(msg, options['attachments'])
            
            # Send email
            return self._send_message(msg, all_recipients)
            
        except Exception as e:
            logger.error(f"Error in send_mail: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _normalize_recipients(self, recipients) -> List[str]:
        """Convert recipients to list format"""
        if isinstance(recipients, str):
            return [recipients]
        elif isinstance(recipients, list):
            return recipients
        else:
            raise ValueError("Recipients must be string or list")
    
    def _add_attachments(self, msg: MIMEMultipart, attachments: List[str]):
        """Add file attachments to message"""
        for file_path in attachments:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                filename = os.path.basename(file_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}',
                )
                msg.attach(part)
            else:
                logger.warning(f"Attachment file not found: {file_path}")
    
    def _send_message(self, msg: MIMEMultipart, recipients: List[str]) -> Dict[str, Any]:
        """Send the email message"""
        try:
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, recipients, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {', '.join(recipients)}")
            
            return {
                'success': True,
                'messageId': f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'recipients': recipients,
                'timestamp': datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Authentication failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def send_template(self, template_name: str, recipients: List[str], 
                     subject: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email using predefined templates"""
        
        templates = {
            'budget_alert': self._get_budget_alert_template,
            'anomaly_alert': self._get_anomaly_alert_template,
            'daily_summary': self._get_daily_summary_template,
            'welcome': self._get_welcome_template,
            'test': self._get_test_template
        }
        
        if template_name not in templates:
            return {'success': False, 'error': f'Template "{template_name}" not found'}
        
        template_func = templates[template_name]
        html_content, text_content = template_func(template_data)
        
        return self.send_mail({
            'to': recipients,
            'subject': subject,
            'html': html_content,
            'text': text_content
        })
    
    def _get_budget_alert_template(self, data: Dict[str, Any]) -> tuple:
        """Budget alert email template"""
        alerts = data.get('alerts', [])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background-color: #dc3545; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .alert {{ padding: 10px; margin: 10px 0; border-left: 4px solid #dc3545; background-color: #f8d7da; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 Budget Alert</h2>
                </div>
                <p>Hello,</p>
                <p>You have budget alerts that require your attention:</p>
                
                {"".join([f'<div class="alert">{alert.get("message", "")}</div>' for alert in alerts])}
                
                <p>Please review your spending and consider adjusting your budget or expenses accordingly.</p>
                <p>Best regards,<br>Your Expense Tracker</p>
                
                <div class="footer">
                    <p>This is an automated message from your Expense Tracker application.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Budget Alert - Expense Tracker
        
        Hello,
        
        You have budget alerts that require your attention:
        
        {"".join([f"- {alert.get('message', '')}\n" for alert in alerts])}
        
        Please review your spending and consider adjusting your budget or expenses accordingly.
        
        Best regards,
        Your Expense Tracker
        """
        
        return html_content, text_content
    
    def _get_daily_summary_template(self, data: Dict[str, Any]) -> tuple:
        """Daily summary email template"""
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        summary = data.get('summary', {})
        transactions = data.get('transactions', [])
        
        transactions_html = ""
        if transactions:
            transactions_html = "<h3>Today's Transactions:</h3><ul>"
            for t in transactions:
                sign = "+" if t.get('type') == 'income' else "-"
                color = "green" if t.get('type') == 'income' else "red"
                transactions_html += f'<li style="color: {color};">{t.get("category", "")}: {sign}${t.get("amount", 0):.2f} - {t.get("description", "")}</li>'
            transactions_html += "</ul>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background-color: #28a745; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .summary-item {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; flex: 1; margin: 0 5px; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📊 Daily Summary - {date}</h2>
                </div>
                <p>Hello,</p>
                
                <div class="summary">
                    <div class="summary-item">
                        <h4>Income</h4>
                        <h3 style="color: green;">${summary.get('total_income', 0):.2f}</h3>
                    </div>
                    <div class="summary-item">
                        <h4>Expenses</h4>
                        <h3 style="color: red;">${summary.get('total_expense', 0):.2f}</h3>
                    </div>
                    <div class="summary-item">
                        <h4>Net</h4>
                        <h3>${summary.get('total_income', 0) - summary.get('total_expense', 0):.2f}</h3>
                    </div>
                </div>
                
                {transactions_html}
                
                <p>Best regards,<br>Your Expense Tracker</p>
                
                <div class="footer">
                    <p>This is an automated message from your Expense Tracker application.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content, ""
    
    def _get_test_template(self, data: Dict[str, Any]) -> tuple:
        """Test email template"""
        html_content = """
        <h2>✅ Email Service Test</h2>
        <p>Congratulations! Your enhanced email service is working correctly.</p>
        <p>Features available:</p>
        <ul>
            <li>📧 Rich HTML emails</li>
            <li>📎 File attachments</li>
            <li>👥 Multiple recipients (TO, CC, BCC)</li>
            <li>📋 Email templates</li>
            <li>🔍 Detailed error handling</li>
            <li>📊 Delivery tracking</li>
        </ul>
        <p>Best regards,<br>Your Enhanced Email Service</p>
        """
        
        text_content = """
        Email Service Test
        
        Congratulations! Your enhanced email service is working correctly.
        
        Features available:
        - Rich HTML emails
        - File attachments
        - Multiple recipients (TO, CC, BCC)
        - Email templates
        - Detailed error handling
        - Delivery tracking
        
        Best regards,
        Your Enhanced Email Service
        """
        
        return html_content, text_content
    
    def _get_welcome_template(self, data: Dict[str, Any]) -> tuple:
        """Welcome email template"""
        username = data.get('username', 'User')
        
        html_content = f"""
        <h2>🎉 Welcome to Expense Tracker!</h2>
        <p>Hello {username},</p>
        <p>Welcome to your personal expense tracking application!</p>
        <p>You can now:</p>
        <ul>
            <li>📊 Track your expenses and income</li>
            <li>📈 View detailed analytics</li>
            <li>💰 Set and monitor budgets</li>
            <li>🔍 Get smart spending insights</li>
            <li>📧 Receive email notifications</li>
        </ul>
        <p>Get started by adding your first transaction!</p>
        <p>Best regards,<br>The Expense Tracker Team</p>
        """
        
        text_content = f"""
        Welcome to Expense Tracker!
        
        Hello {username},
        
        Welcome to your personal expense tracking application!
        
        You can now:
        - Track your expenses and income
        - View detailed analytics
        - Set and monitor budgets
        - Get smart spending insights
        - Receive email notifications
        
        Get started by adding your first transaction!
        
        Best regards,
        The Expense Tracker Team
        """
        
        return html_content, text_content
    
    def _get_anomaly_alert_template(self, data: Dict[str, Any]) -> tuple:
        """Anomaly alert email template"""
        anomalies = data.get('anomalies', [])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background-color: #fd7e14; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .anomaly {{ padding: 10px; margin: 10px 0; border-left: 4px solid #fd7e14; background-color: #fff3cd; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔍 Unusual Spending Detected</h2>
                </div>
                <p>Hello,</p>
                <p>We've detected some unusual spending patterns in your account:</p>
                
                {"".join([f'<div class="anomaly">{anomaly.get("message", "")}</div>' for anomaly in anomalies])}
                
                <p>Please review these transactions and ensure they are accurate.</p>
                <p>Best regards,<br>Your Expense Tracker</p>
                
                <div class="footer">
                    <p>This is an automated message from your Expense Tracker application.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Unusual Spending Detected - Expense Tracker
        
        Hello,
        
        We've detected some unusual spending patterns in your account:
        
        {"".join([f"- {anomaly.get('message', '')}\n" for anomaly in anomalies])}
        
        Please review these transactions and ensure they are accurate.
        
        Best regards,
        Your Expense Tracker
        """
        
        return html_content, text_content

# Global instance
email_service = EmailService()

# Convenience functions for backward compatibility
def send_email(to_email, subject, html_content, text_content=None):
    """Send email using the enhanced service"""
    options = {
        'to': to_email,
        'subject': subject,
        'html': html_content
    }
    if text_content:
        options['text'] = text_content
    
    result = email_service.send_mail(options)
    return result['success']

def send_budget_alert_email(user_id, alerts):
    """Send budget alert email using templates"""
    from models.database import get_db_connection
    
    # Get user email
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False
    
    user_email = result['email']
    
    result = email_service.send_template(
        'budget_alert',
        [user_email],
        "⚠️ Budget Alert - Expense Tracker",
        {'alerts': alerts}
    )
    
    return result['success']

def send_daily_summary_email(user_id):
    """Send daily summary email using templates"""
    from models.database import get_db_connection
    from datetime import datetime
    
    # Get user email
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False
    
    user_email = result['email']
    
    # Get today's data
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''SELECT 
        SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
        SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense,
        COUNT(*) as total_transactions
        FROM transactions WHERE user_id = ? AND date = ?''', (user_id, today))
    summary = cursor.fetchone()
    
    cursor.execute('SELECT * FROM transactions WHERE user_id = ? AND date = ? ORDER BY created_at DESC', (user_id, today))
    transactions = cursor.fetchall()
    conn.close()
    
    result = email_service.send_template(
        'daily_summary',
        [user_email],
        f"📊 Daily Summary - {today}",
        {
            'date': today,
            'summary': dict(summary) if summary else {},
            'transactions': [dict(t) for t in transactions]
        }
    )
    
    return result['success']