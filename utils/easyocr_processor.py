"""
Enhanced OCR Processor using EasyOCR for improved accuracy
Provides better receipt reading with fallback to Tesseract if needed
"""

import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import re
from datetime import datetime
import os
import logging
from typing import Dict, Optional, Tuple, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global reader instance (lazy loaded)
_reader = None
_reader_lock = None

def get_ocr_reader(languages=['en']):
    """
    Get or initialize EasyOCR reader (singleton pattern for performance)
    
    Args:
        languages: List of language codes to recognize
        
    Returns:
        easyocr.Reader: Initialized OCR reader
    """
    global _reader, _reader_lock
    
    if _reader is None:
        logger.info(f"Initializing EasyOCR reader for languages: {languages}")
        try:
            _reader = easyocr.Reader(languages, gpu=False)
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            raise
    
    return _reader


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess image for better OCR accuracy
    
    Args:
        image_path: Path to the receipt image
        
    Returns:
        np.ndarray: Preprocessed image
    """
    try:
        # Read image with OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Apply adaptive thresholding for better text contrast
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Apply morphological operations to improve text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Upscale if image is small
        height = morph.shape[0]
        if height < 300:
            scale_factor = 2
            morph = cv2.resize(morph, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        
        logger.info(f"Image preprocessed successfully: {morph.shape}")
        return morph
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise


def extract_text_with_confidence(image_path: str, languages=['en']) -> Tuple[str, float]:
    """
    Extract text from image using EasyOCR with confidence scoring
    
    Args:
        image_path: Path to the receipt image
        languages: Languages to recognize
        
    Returns:
        Tuple of (extracted_text, average_confidence)
    """
    try:
        reader = get_ocr_reader(languages)
        
        # Preprocess the image
        processed_img = preprocess_image(image_path)
        
        # Run OCR
        results = reader.readtext(processed_img, detail=1)
        
        if not results:
            logger.warning("No text detected in image")
            return "", 0.0
        
        # Extract text and confidence
        texts = []
        confidences = []
        
        for (bbox, text, confidence) in results:
            if confidence > 0.1:  # Filter out very low confidence results
                texts.append(text)
                confidences.append(confidence)
        
        full_text = '\n'.join(texts)
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        logger.info(f"Extracted {len(texts)} text elements with avg confidence: {avg_confidence:.2%}")
        
        return full_text, avg_confidence
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        raise


def extract_receipt_data(image_path: str) -> Dict:
    """
    Extract structured receipt data from an image
    
    Args:
        image_path: Path to the receipt image
        
    Returns:
        dict: Dictionary containing:
              - amount: Transaction amount (float)
              - date: Transaction date (string)
              - description: Merchant name (string)
              - raw_text: Full OCR text (string)
              - confidence: OCR confidence score (float)
              - ocr_method: 'easyocr' or 'tesseract'
    """
    try:
        # Validate file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {
                'amount': 0.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Error: Receipt file not found',
                'raw_text': '',
                'confidence': 0.0,
                'ocr_method': 'none',
                'error': 'File not found'
            }
        
        logger.info(f"Processing receipt: {image_path}")
        
        # Extract text with confidence
        text, confidence = extract_text_with_confidence(image_path)
        
        if not text or text.strip() == '':
            logger.warning("No text extracted from receipt")
            return {
                'amount': 0.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'No text found in receipt image',
                'raw_text': text,
                'confidence': confidence,
                'ocr_method': 'easyocr',
                'warning': 'No text extracted'
            }
        
        # Extract structured data
        amount = extract_amount(text)
        date = extract_date(text)
        merchant = extract_merchant(text)
        
        logger.info(f"Extracted - Amount: {amount}, Date: {date}, Merchant: {merchant}")
        
        return {
            'amount': amount,
            'date': date,
            'description': merchant or 'Receipt Purchase',
            'raw_text': text,
            'confidence': confidence,
            'ocr_method': 'easyocr'
        }
        
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        return {
            'amount': 0.0,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': f'Error processing receipt: {type(e).__name__}',
            'raw_text': '',
            'confidence': 0.0,
            'ocr_method': 'easyocr',
            'error': str(e)
        }


def extract_amount(text: str) -> float:
    """
    Extract transaction amount from OCR text
    Supports multiple currency formats
    
    Args:
        text: Extracted OCR text
        
    Returns:
        float: Extracted amount or 0.0
    """
    if not text:
        return 0.0
    
    # Enhanced patterns for better accuracy
    patterns = [
        # Pattern 1: TOTAL variations with optional currency symbols
        r'(?:TOTAL\s*AMOUNT|GRAND\s*TOTAL|TOTAL|PAYABLE)[:\s]*\$?₹?([0-9,]+\.?[0-9]*)',
        
        # Pattern 2: Amount label patterns
        r'(?:Amount|AMOUNT|DUE|PAY)[:\s]*\$?₹?([0-9,]+\.?[0-9]*)',
        
        # Pattern 3: Subtotal and tax variations
        r'(?:SUBTOTAL|SUB\s*TOTAL|NET\s*AMOUNT)[:\s]*\$?₹?([0-9,]+\.?[0-9]*)',
        
        # Pattern 4: Currency symbols with amounts
        r'₹\s*([0-9,]+\.?[0-9]*)',  # Indian Rupee
        r'\$\s*([0-9,]+\.[0-9]{2})',  # US Dollar
        r'€\s*([0-9,]+\.?[0-9]*)',  # Euro
        
        # Pattern 5: Common amount formats at line end
        r'([0-9]{1,5}[.,][0-9]{2})(?:\s|$)',
        
        # Pattern 6: Amounts with word boundaries
        r'(?:^|\s)([0-9,]+\.[0-9]{2})(?:\s|$)',
        
        # Pattern 7: Large amounts (no decimal)
        r'(?:^|\s)([0-9,]+)(?:\s*(?:TOTAL|AMOUNT|INR|USD))',
    ]
    
    largest_amount = 0.0
    
    for pattern in patterns:
        try:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                amount_str = match.group(1)
                
                # Parse amount with smart decimal separator detection
                amount = parse_amount(amount_str)
                
                # Validate amount (realistic for receipts)
                if 0 < amount < 1000000 and amount > largest_amount:
                    largest_amount = amount
                    logger.debug(f"Found amount: {amount} from pattern: {pattern}")
                    
        except Exception as e:
            logger.debug(f"Pattern matching error: {str(e)}")
            continue
    
    return largest_amount


def parse_amount(amount_str: str) -> float:
    """
    Parse amount string with intelligent decimal/thousand separator detection
    
    Args:
        amount_str: Amount string to parse
        
    Returns:
        float: Parsed amount
    """
    if not amount_str:
        return 0.0
    
    # Clean whitespace
    amount_str = amount_str.strip()
    
    # Count separators
    comma_count = amount_str.count(',')
    dot_count = amount_str.count('.')
    
    try:
        # Both separators present
        if comma_count > 0 and dot_count > 0:
            # Determine which is decimal by position
            last_comma = amount_str.rfind(',')
            last_dot = amount_str.rfind('.')
            
            if last_dot > last_comma:
                # Dot is last separator (decimal)
                amount_str = amount_str.replace(',', '')
            else:
                # Comma is last separator (decimal)
                amount_str = amount_str.replace('.', '').replace(',', '.')
                
        # Only commas
        elif comma_count > 1:
            # Multiple commas = thousand separators
            amount_str = amount_str.replace(',', '')
        elif comma_count == 1 and dot_count == 0:
            # Single comma, no dot = decimal separator
            amount_str = amount_str.replace(',', '.')
            
        # Only dots
        elif dot_count > 1:
            # Multiple dots - keep last as decimal
            parts = amount_str.split('.')
            amount_str = parts[0].replace('.', '') + '.' + parts[-1]
        
        return float(amount_str)
        
    except ValueError:
        logger.warning(f"Could not parse amount: {amount_str}")
        return 0.0


def extract_date(text: str) -> str:
    """
    Extract transaction date from OCR text
    
    Args:
        text: Extracted OCR text
        
    Returns:
        str: Date in YYYY-MM-DD format
    """
    if not text:
        return datetime.now().strftime('%Y-%m-%d')
    
    date_patterns = [
        # ISO format
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        # DD-MM-YYYY or MM/DD/YYYY
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        # Month name formats
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
        # Date in text format
        r'(\d{4}-\d{2}-\d{2})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                from dateutil import parser
                parsed_date = parser.parse(date_str, fuzzy=False)
                return parsed_date.strftime('%Y-%m-%d')
            except:
                logger.debug(f"Could not parse date: {date_str}")
                continue
    
    logger.info("No date found in receipt, using current date")
    return datetime.now().strftime('%Y-%m-%d')


def extract_merchant(text: str) -> str:
    """
    Extract merchant/store name from receipt text
    
    Args:
        text: Extracted OCR text
        
    Returns:
        str: Merchant name or 'Receipt Purchase'
    """
    if not text or not text.strip():
        return 'Receipt Purchase'
    
    lines = text.strip().split('\n')
    
    # Keywords that indicate non-merchant lines
    skip_keywords = [
        'TOTAL', 'AMOUNT', 'TAX', 'SUBTOTAL', 'PRICE', 'ITEM', 'QTY',
        'THANK', 'WELCOME', 'INVOICE', 'RECEIPT', 'ORDER', 'REF', 'PHONE',
        'ADDRESS', 'PAID', 'CHANGE', 'CASH', 'CARD', 'THANK YOU', 'PLEASE',
        'DATE', 'TIME', 'CASHIER', 'REGISTER', 'BILL'
    ]
    
    candidates: List[Tuple[int, str]] = []
    
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        line = line.strip()
        
        # Skip empty or very short/long lines
        if len(line) < 2 or len(line) > 150:
            continue
        
        # Skip purely numeric lines
        if re.match(r'^\d+$', line):
            continue
        
        # Skip lines with excessive numbers (codes, amounts)
        digit_ratio = len(re.findall(r'\d', line)) / len(line)
        if digit_ratio > 0.7:
            continue
        
        # Skip known receipt labels
        if any(keyword in line.upper() for keyword in skip_keywords):
            continue
        
        # Skip lines with only special characters
        if re.match(r'^[^\w\s]*$', line):
            continue
        
        # Skip lines that are clearly product/item names (too short or common)
        if line.lower() in ['item', 'items', 'product', 'products']:
            continue
        
        # Prioritize earlier lines (merchant usually at top)
        candidates.append((i, line))
    
    if candidates:
        # Return the earliest meaningful line
        return candidates[0][1]
    
    return 'Receipt Purchase'


def clear_reader_cache():
    """Clear the global OCR reader cache (useful for testing)"""
    global _reader
    _reader = None
    logger.info("OCR reader cache cleared")