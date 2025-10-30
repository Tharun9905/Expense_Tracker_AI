from models.database import get_db_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, html_content, text_content=None):
    """Send email using SMTP"""
    try:
        # Email configuration (these should be set as environment variables)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        from_email = os.environ.get('FROM_EMAIL', smtp_username)
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured. Email not sent.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Create the plain-text and HTML version of your message
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def get_user_email(user_id):
    """Get user email from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['email'] if result else None

def get_notification_preferences(user_id):
    """Get user notification preferences"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notification_preferences WHERE user_id = ?', (user_id,))
    prefs = cursor.fetchone()
    
    # If no preferences exist, create default ones
    if not prefs:
        cursor.execute('''INSERT INTO notification_preferences 
            (user_id, budget_alerts_email, anomaly_alerts_email, daily_summary_email, weekly_summary_email) 
            VALUES (?, 1, 1, 0, 0)''', (user_id,))
        conn.commit()
        cursor.execute('SELECT * FROM notification_preferences WHERE user_id = ?', (user_id,))
        prefs = cursor.fetchone()
    
    conn.close()
    return prefs

def send_budget_alert_email(user_id, alerts):
    """Send budget alert email"""
    prefs = get_notification_preferences(user_id)
    if not prefs['budget_alerts_email']:
        return False
        
    user_email = get_user_email(user_id)
    if not user_email:
        return False
    
    subject = "⚠️ Budget Alert - Expense Tracker"
    
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
            
            {"".join([f'<div class="alert">{alert["message"]}</div>' for alert in alerts])}
            
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
    
    {"".join([f"- {alert['message']}" + chr(10) for alert in alerts])}
    
    Please review your spending and consider adjusting your budget or expenses accordingly.
    
    Best regards,
    Your Expense Tracker
    """
    
    return send_email(user_email, subject, html_content, text_content)

def send_anomaly_alert_email(user_id, anomalies):
    """Send anomaly detection alert email"""
    prefs = get_notification_preferences(user_id)
    if not prefs['anomaly_alerts_email']:
        return False
        
    user_email = get_user_email(user_id)
    if not user_email:
        return False
    
    subject = "🔍 Unusual Spending Detected - Expense Tracker"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header {{ background-color: #17a2b8; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .anomaly {{ padding: 10px; margin: 10px 0; border-left: 4px solid #17a2b8; background-color: #d1ecf1; }}
            .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔍 Unusual Spending Detected</h2>
            </div>
            <p>Hello,</p>
            <p>Our system has detected some unusual spending patterns in your account:</p>
            
            {"".join([f'<div class="anomaly">{anomaly["message"]}</div>' for anomaly in anomalies])}
            
            <p>Please review these transactions to ensure they are accurate and expected.</p>
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
    
    Our system has detected some unusual spending patterns in your account:
    
    {"".join([f"- {anomaly['message']}" + chr(10) for anomaly in anomalies])}
    
    Please review these transactions to ensure they are accurate and expected.
    
    Best regards,
    Your Expense Tracker
    """
    
    return send_email(user_email, subject, html_content, text_content)

def send_daily_summary_email(user_id):
    """Send daily spending summary email"""
    prefs = get_notification_preferences(user_id)
    if not prefs['daily_summary_email']:
        return False
        
    user_email = get_user_email(user_id)
    if not user_email:
        return False
    
    # Get today's transactions
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT 
        SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
        SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense,
        COUNT(*) as total_transactions
        FROM transactions WHERE user_id = ? AND date = ?''', (user_id, today))
    summary = cursor.fetchone()
    
    cursor.execute('SELECT * FROM transactions WHERE user_id = ? AND date = ? ORDER BY created_at DESC', (user_id, today))
    transactions = cursor.fetchall()
    conn.close()
    
    subject = f"📊 Daily Summary - {today}"
    
    transactions_html = ""
    if transactions:
        transactions_html = "<h3>Today's Transactions:</h3><ul>"
        for t in transactions:
            sign = "+" if t['type'] == 'income' else "-"
            color = "green" if t['type'] == 'income' else "red"
            transactions_html += f'<li style="color: {color};">{t["category"]}: {sign}${t["amount"]:.2f} - {t["description"]}</li>'
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
            .summary-item {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📊 Daily Summary - {today}</h2>
            </div>
            <p>Hello,</p>
            
            <div class="summary">
                <div class="summary-item">
                    <h4>Income</h4>
                    <h3 style="color: green;">${summary['total_income'] or 0:.2f}</h3>
                </div>
                <div class="summary-item">
                    <h4>Expenses</h4>
                    <h3 style="color: red;">${summary['total_expense'] or 0:.2f}</h3>
                </div>
                <div class="summary-item">
                    <h4>Net</h4>
                    <h3>${(summary['total_income'] or 0) - (summary['total_expense'] or 0):.2f}</h3>
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
    
    return send_email(user_email, subject, html_content)