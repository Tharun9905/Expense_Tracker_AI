import pytesseract
from PIL import Image
import re
from datetime import datetime
import os

# Try to configure tesseract path for Windows
def configure_tesseract():
    # Common Tesseract paths on Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
        r'C:\ProgramData\chocolatey\bin\tesseract.exe'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True
    return False

def extract_receipt_data(image_path):
    try:
        # Try to configure tesseract path
        tesseract_configured = configure_tesseract()
        
        if not tesseract_configured:
            print("Warning: Tesseract OCR not found. OCR functionality will be limited.")
            # Return mock data for now so the app doesn't crash
            return {
                'amount': 0.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Manual Entry Required (OCR not available)',
                'raw_text': ''
            }
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)

        amount = extract_amount(text)
        date = extract_date(text)
        merchant = extract_merchant(text)

        return {
            'amount': amount,
            'date': date,
            'description': merchant or 'Receipt Purchase',
            'raw_text': text
        }
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        # Return fallback data instead of None to prevent app crashes
        return {
            'amount': 0.0,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': f'Error processing receipt: {str(e)}',
            'raw_text': ''
        }

def extract_amount(text):
    patterns = [
        r'TOTAL[:\\s]*\\$?([0-9,]+\\.?[0-9]*)',
        r'Amount[:\\s]*\\$?([0-9,]+\\.?[0-9]*)',
        r'\\$([0-9,]+\\.[0-9]{2})',
        r'([0-9,]+\\.[0-9]{2})'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except:
                continue
    return 0.0

def extract_date(text):
    date_patterns = [
        r'(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})',
        r'(\\d{4}[/-]\\d{1,2}[/-]\\d{1,2})',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return datetime.now().strftime('%Y-%m-%d')

def extract_merchant(text):
    lines = text.strip().split('\\n')
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 3 and not re.search(r'\\d{4}', line):
            return line
    return None
