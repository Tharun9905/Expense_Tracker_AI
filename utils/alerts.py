from models.database import get_db_connection
from datetime import datetime, timedelta
from .email_service import send_budget_alert_email, send_anomaly_alert_email

def has_alert_been_sent_today(user_id, alert_type, category):
    """Check if an alert has already been sent for this category today"""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''SELECT id FROM email_alert_history 
        WHERE user_id = ? AND alert_type = ? AND category = ? AND sent_date = ?''',
        (user_id, alert_type, category, today))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

def record_alert_sent(user_id, alert_type, category):
    """Record that an alert email has been sent for this category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        cursor.execute('''INSERT OR IGNORE INTO email_alert_history 
            (user_id, alert_type, category, sent_date)
            VALUES (?, ?, ?, ?)''',
            (user_id, alert_type, category, today))
        conn.commit()
    except Exception as e:
        print(f"Error recording alert: {e}")
    finally:
        conn.close()

def check_budget_alerts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    alerts = []
    alerts_to_send = []
    current_month = datetime.now().strftime('%Y-%m')

    cursor.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,))
    budgets = cursor.fetchall()

    for budget in budgets:
        cursor.execute('''SELECT SUM(amount) as total FROM transactions 
            WHERE user_id = ? AND category = ? AND type = 'expense' 
            AND strftime('%Y-%m', date) = ?''', 
            (user_id, budget['category'], current_month))
        result = cursor.fetchone()
        spent = result['total'] or 0
        percentage = (spent / budget['amount']) * 100 if budget['amount'] > 0 else 0

        if percentage >= 100:
            alert_msg = {'type': 'danger', 'category': budget['category'], 
                         'message': f"Budget exceeded for {budget['category']}! Spent: ${spent:.2f} / ${budget['amount']:.2f}"}
            alerts.append(alert_msg)
            
            # Only send email if not already sent today
            if not has_alert_been_sent_today(user_id, 'budget_danger', budget['category']):
                alerts_to_send.append(alert_msg)
                record_alert_sent(user_id, 'budget_danger', budget['category'])
                
        elif percentage >= 80:
            alert_msg = {'type': 'warning', 'category': budget['category'],
                         'message': f"Approaching budget limit for {budget['category']}. Spent: ${spent:.2f} / ${budget['amount']:.2f}"}
            alerts.append(alert_msg)
            
            # Only send email if not already sent today
            if not has_alert_been_sent_today(user_id, 'budget_warning', budget['category']):
                alerts_to_send.append(alert_msg)
                record_alert_sent(user_id, 'budget_warning', budget['category'])
    
    # Send email only for new alerts
    if alerts_to_send:
        try:
            send_budget_alert_email(user_id, alerts_to_send)
            print(f"Budget alert email sent for {len(alerts_to_send)} category/categories")
        except Exception as e:
            print(f"Failed to send budget alert email: {e}")
    else:
        print("Budget alert already sent today for all triggered categories")
    
    conn.close()
    return alerts

def detect_anomalies(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    anomalies = []
    anomalies_to_send = []
    last_30_days = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    cursor.execute('''SELECT AVG(amount) as avg_amount, category FROM transactions 
        WHERE user_id = ? AND type = 'expense' AND date >= ? GROUP BY category''', 
        (user_id, last_30_days))
    averages = cursor.fetchall()

    last_7_days = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    for avg_row in averages:
        category = avg_row['category']
        avg_amount = avg_row['avg_amount']
        cursor.execute('''SELECT * FROM transactions WHERE user_id = ? AND category = ? 
            AND type = 'expense' AND date >= ? AND amount > ?''', 
            (user_id, category, last_7_days, avg_amount * 2))
        unusual = cursor.fetchall()

        for transaction in unusual:
            anomaly_msg = {'type': 'info',
                'message': f"Unusual {category} expense: ${transaction['amount']:.2f} on {transaction['date']}"}
            anomalies.append(anomaly_msg)
            
            # Only send email if not already sent today for this category
            if not has_alert_been_sent_today(user_id, 'anomaly', category):
                anomalies_to_send.append(anomaly_msg)
                record_alert_sent(user_id, 'anomaly', category)
    
    # Send email only for new anomalies
    if anomalies_to_send:
        try:
            send_anomaly_alert_email(user_id, anomalies_to_send)
            print(f"Anomaly alert email sent for {len(anomalies_to_send)} anomaly/anomalies")
        except Exception as e:
            print(f"Failed to send anomaly alert email: {e}")
    else:
        if anomalies:
            print("Anomaly alert already sent today for this category")
    
    conn.close()
    return anomalies
