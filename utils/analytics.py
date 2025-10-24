from models.database import get_db_connection

def get_category_breakdown(user_id, month):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT category, SUM(amount) as total FROM transactions 
        WHERE user_id = ? AND type = 'expense' AND strftime('%Y-%m', date) = ? 
        GROUP BY category ORDER BY total DESC''', (user_id, month))
    categories = cursor.fetchall()
    conn.close()
    return [{'category': row['category'], 'amount': row['total']} for row in categories]

def generate_spending_report(user_id, start_date):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''SELECT 
        SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
        SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense,
        COUNT(*) as transaction_count
        FROM transactions WHERE user_id = ? AND date >= ?''', (user_id, start_date))
    summary = cursor.fetchone()

    cursor.execute('''SELECT category, SUM(amount) as total FROM transactions 
        WHERE user_id = ? AND type = 'expense' AND date >= ? 
        GROUP BY category ORDER BY total DESC''', (user_id, start_date))
    category_breakdown = cursor.fetchall()

    cursor.execute('''SELECT date, SUM(amount) as daily_total FROM transactions 
        WHERE user_id = ? AND type = 'expense' AND date >= ? 
        GROUP BY date ORDER BY date''', (user_id, start_date))
    daily_spending = cursor.fetchall()

    cursor.execute('''SELECT * FROM transactions WHERE user_id = ? 
        AND type = 'expense' AND date >= ? ORDER BY amount DESC LIMIT 5''', (user_id, start_date))
    top_expenses = cursor.fetchall()

    conn.close()

    return {
        'summary': {
            'total_income': summary['total_income'] or 0,
            'total_expense': summary['total_expense'] or 0,
            'net_savings': (summary['total_income'] or 0) - (summary['total_expense'] or 0),
            'transaction_count': summary['transaction_count']
        },
        'category_breakdown': [{'category': r['category'], 'amount': r['total']} for r in category_breakdown],
        'daily_spending': [{'date': r['date'], 'amount': r['daily_total']} for r in daily_spending],
        'top_expenses': [dict(r) for r in top_expenses]
    }
