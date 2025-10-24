from models.database import get_db_connection
from datetime import datetime, timedelta
from .email_service import send_budget_alert_email, send_anomaly_alert_email

def check_budget_alerts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    alerts = []
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
            alerts.append({'type': 'danger', 'category': budget['category'], 
                         'message': f"Budget exceeded for {budget['category']}! Spent: ${spent:.2f} / ${budget['amount']:.2f}"})
        elif percentage >= 80:
            alerts.append({'type': 'warning', 'category': budget['category'],
                         'message': f"Approaching budget limit for {budget['category']}. Spent: ${spent:.2f} / ${budget['amount']:.2f}"})
    
    # Send email if there are alerts
    if alerts:
        try:
            send_budget_alert_email(user_id, alerts)
        except Exception as e:
            print(f"Failed to send budget alert email: {e}")
    
    conn.close()
    return alerts

def detect_anomalies(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    anomalies = []
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
            anomalies.append({'type': 'info',
                'message': f"Unusual {category} expense: ${transaction['amount']:.2f} on {transaction['date']}"})
    
    # Send email if there are anomalies
    if anomalies:
        try:
            send_anomaly_alert_email(user_id, anomalies)
        except Exception as e:
            print(f"Failed to send anomaly alert email: {e}")
    
    conn.close()
    return anomalies
