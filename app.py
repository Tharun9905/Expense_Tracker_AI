from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models.database import init_db, get_db_connection
from utils.easyocr_processor import extract_receipt_data
from utils.ai_categorizer import categorize_expense, predict_category
from utils.alerts import check_budget_alerts, detect_anomalies
from utils.analytics import generate_spending_report, get_category_breakdown
from utils.email_service import get_notification_preferences, send_daily_summary_email
from utils.enhanced_email_service import EmailService
from utils.currency_formatter import format_inr, currency_symbol, currency_name
# Initialize enhanced email service
email_service = EmailService()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

init_db()

# Make currency formatter available to all templates
@app.context_processor
def inject_currency():
    return {
        'format_inr': format_inr,
        'currency_symbol': currency_symbol(),
        'currency_name': currency_name()
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Email already registered!', 'error')
            conn.close()
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 10', (user_id,))
    recent_transactions = cursor.fetchall()

    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''SELECT 
        SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
        SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions WHERE user_id = ? AND strftime('%Y-%m', date) = ?''', (user_id, current_month))
    summary = cursor.fetchone()

    category_data = get_category_breakdown(user_id, current_month)
    alerts = check_budget_alerts(user_id)
    anomalies = detect_anomalies(user_id)

    conn.close()

    return render_template('dashboard.html', transactions=recent_transactions, summary=summary, categories=category_data, alerts=alerts, anomalies=anomalies)

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        user_id = session['user_id']
        transaction_type = request.form.get('type')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        description = request.form.get('description', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))

        if not category or category == 'auto':
            category = predict_category(description, amount)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES (?, ?, ?, ?, ?, ?)', (user_id, transaction_type, amount, category, description, date))
        conn.commit()
        conn.close()

        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_transaction.html')

@app.route('/upload_receipt', methods=['GET', 'POST'])
@login_required
def upload_receipt():
    if request.method == 'POST':
        if 'receipt' not in request.files:
            flash('No file uploaded!', 'error')
            return redirect(request.url)

        file = request.files['receipt']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            extracted_data = extract_receipt_data(filepath)

            if extracted_data:
                category = categorize_expense(extracted_data.get('description', ''))
                user_id = session['user_id']
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO transactions (user_id, type, amount, category, description, date, receipt_path) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, 'expense', extracted_data.get('amount', 0), category, extracted_data.get('description', ''), extracted_data.get('date', datetime.now().strftime('%Y-%m-%d')), filepath))
                conn.commit()
                conn.close()

                flash('Receipt processed successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Could not extract data from receipt.', 'error')

    return render_template('upload_receipt.html')

@app.route('/analytics')
@login_required
def analytics():
    user_id = session['user_id']
    period = request.args.get('period', 'month')

    if period == 'week':
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period == 'year':
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    else:
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')

    report = generate_spending_report(user_id, start_date)
    return render_template('analytics.html', report=report, period=period)

@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    user_id = session['user_id']

    if request.method == 'POST':
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        period = request.form.get('period', 'monthly')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO budgets (user_id, category, amount, period) VALUES (?, ?, ?, ?)', (user_id, category, amount, period))
        conn.commit()
        conn.close()

        flash('Budget set successfully!', 'success')
        return redirect(url_for('budgets'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,))
    user_budgets = cursor.fetchall()
    conn.close()

    return render_template('budgets.html', budgets=user_budgets)

@app.route('/transactions')
@login_required
def transactions():
    user_id = session['user_id']
    transaction_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM transactions WHERE user_id = ?'
    params = [user_id]

    if transaction_type != 'all':
        query += ' AND type = ?'
        params.append(transaction_type)

    if category != 'all':
        query += ' AND category = ?'
        params.append(category)

    query += ' ORDER BY date DESC'

    cursor.execute(query, params)
    all_transactions = cursor.fetchall()

    cursor.execute('SELECT DISTINCT category FROM transactions WHERE user_id = ?', (user_id,))
    categories = [row['category'] for row in cursor.fetchall()]

    conn.close()

    return render_template('transactions.html', transactions=all_transactions, categories=categories, selected_type=transaction_type, selected_category=category)

@app.route('/delete_transaction/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
    conn.commit()
    conn.close()
    flash('Transaction deleted!', 'success')
    return redirect(url_for('transactions'))

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    user_id = session['user_id']
    
    if request.method == 'POST':
        budget_alerts_email = 1 if request.form.get('budget_alerts_email') else 0
        anomaly_alerts_email = 1 if request.form.get('anomaly_alerts_email') else 0
        daily_summary_email = 1 if request.form.get('daily_summary_email') else 0
        weekly_summary_email = 1 if request.form.get('weekly_summary_email') else 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO notification_preferences 
            (user_id, budget_alerts_email, anomaly_alerts_email, daily_summary_email, weekly_summary_email) 
            VALUES (?, ?, ?, ?, ?)''', 
            (user_id, budget_alerts_email, anomaly_alerts_email, daily_summary_email, weekly_summary_email))
        conn.commit()
        conn.close()
        
        flash('Notification preferences updated!', 'success')
        return redirect(url_for('notifications'))
    
    preferences = get_notification_preferences(user_id)
    return render_template('notifications.html', preferences=preferences)

@app.route('/send_test_email')
@login_required
def send_test_email():
    user_id = session['user_id']
    try:
        success = send_daily_summary_email(user_id)
        if success:
            flash('Test email sent successfully!', 'success')
        else:
            flash('Failed to send test email. Please check your email configuration.', 'error')
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/api/email-status')
@login_required
def email_status():
    """API endpoint to check if email is configured"""
    import os
    configured = bool(os.environ.get('SMTP_USERNAME') and os.environ.get('SMTP_PASSWORD'))
    return jsonify({'configured': configured})

@app.route('/send_enhanced_test_email')
@login_required
def send_enhanced_test_email():
    """Send test email using enhanced email service"""
    user_id = session['user_id']
    
    # Get user email
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        flash('User email not found', 'error')
        return redirect(url_for('notifications'))
    
    user_email = result['email']
    
    try:
        # Send test email using enhanced service
        result = email_service.send_template(
            'test',
            [user_email],
            '🧪 Enhanced Email Service Test - Expense Tracker',
            {}
        )
        
        if result['success']:
            flash(f'✅ Enhanced test email sent successfully to {user_email}! Check your inbox.', 'success')
        else:
            flash(f'❌ Failed to send enhanced test email: {result.get("error", "Unknown error")}', 'error')
    
    except Exception as e:
        flash(f'❌ Error sending enhanced test email: {str(e)}', 'error')
    
    return redirect(url_for('notifications'))

@app.route('/test_all_email_templates')
@login_required
def test_all_email_templates():
    """Test all professional email templates"""
    user_id = session['user_id']
    
    # Get user email
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        flash('User email not found', 'error')
        return redirect(url_for('notifications'))
    
    user_email = result['email']
    
    try:
        # Import enhanced email service
        from utils.enhanced_email_service import EmailService
        professional_email_service = EmailService()
        
        templates_to_test = [
            {
                'name': 'Budget Alert',
                'options': {
                    'to': user_email,
                    'subject': '🚨 Professional Budget Alert Test',
                    'html': '''
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                            <h2 style="margin: 0;">🚨 Budget Alert</h2>
                            <p style="margin: 5px 0;">Professional Notification Test</p>
                        </div>
                        <div style="padding: 20px; background-color: #fff5f5; border-left: 4px solid #ff6b6b; margin: 20px 0;">
                            <h3 style="color: #d63031; margin-top: 0;">Food & Dining Category</h3>
                            <p><strong>Budget:</strong> $400.00 | <strong>Spent:</strong> $485.50 | <strong>Over by:</strong> $85.50</p>
                        </div>
                        <p style="text-align: center; color: #666;">Sent from expensetracker@gmail.com</p>
                    </div>
                    '''
                }
            },
            {
                'name': 'Daily Summary',
                'options': {
                    'to': user_email,
                    'subject': '📊 Professional Daily Summary Test',
                    'html': '''
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center;">
                            <h2 style="margin: 0;">📊 Daily Summary</h2>
                            <p style="margin: 5px 0;">Professional Template Test</p>
                        </div>
                        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #2d3436; margin-top: 0;">Today's Expenses</h3>
                            <div style="background: white; padding: 10px; border-radius: 5px;">
                                <p><strong>Total Spent:</strong> <span style="color: #e74c3c;">$127.50</span></p>
                                <p><strong>Top Categories:</strong> Food ($65), Transport ($35), Shopping ($27.50)</p>
                            </div>
                        </div>
                        <p style="text-align: center; color: #666;">Professional Daily Summary from expensetracker@gmail.com</p>
                    </div>
                    '''
                }
            },
            {
                'name': 'Welcome Email',
                'options': {
                    'to': user_email,
                    'subject': '🎉 Professional Welcome Email Test',
                    'html': '''
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                            <h1 style="margin: 0;">🎉 Welcome!</h1>
                            <p style="margin: 10px 0 0;">Professional Email Template Test</p>
                        </div>
                        <div style="padding: 30px 20px;">
                            <h2 style="color: #333;">✨ Professional Features Active:</h2>
                            <ul style="line-height: 1.8;">
                                <li>📧 Professional sender: expensetracker@gmail.com</li>
                                <li>🎨 HTML email templates</li>
                                <li>🚨 Budget alerts with rich formatting</li>
                                <li>📊 Daily summaries with charts</li>
                                <li>🔍 Anomaly detection notifications</li>
                            </ul>
                            <div style="text-align: center; margin: 30px 0;">
                                <div style="display: inline-block; background-color: #4CAF50; color: white; padding: 15px 30px; border-radius: 25px;">
                                    <strong>Professional System: ACTIVE</strong>
                                </div>
                            </div>
                        </div>
                        <p style="color: #7f8c8d; text-align: center; font-size: 14px;">Professional template from expensetracker@gmail.com</p>
                    </div>
                    '''
                }
            }
        ]
        
        results = []
        for template in templates_to_test:
            try:
                result = professional_email_service.send_mail(template['options'])
                results.append({
                    'name': template['name'],
                    'success': result['success'],
                    'message_id': result.get('message_id', ''),
                    'error': result.get('error', '')
                })
            except Exception as e:
                results.append({
                    'name': template['name'],
                    'success': False,
                    'error': str(e)
                })
        
        # Count successes
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        if successful == total:
            flash(f'🎉 All {total} professional email templates sent successfully to {user_email}! Check your inbox for professional-looking notifications.', 'success')
        else:
            flash(f'⚠️ {successful}/{total} email templates sent successfully. Check your professional email configuration.', 'warning')
            
    except Exception as e:
        flash(f'❌ Error testing professional email templates: {str(e)}', 'error')
    
    return redirect(url_for('notifications'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
