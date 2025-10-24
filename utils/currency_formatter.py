#!/usr/bin/env python3
"""
Currency Formatter Utility
Handles INR (Indian Rupees) formatting throughout the application
"""

def format_inr(amount: float, include_symbol: bool = True) -> str:
    """
    Format amount as Indian Rupees with proper comma separation
    
    Args:
        amount: The numeric amount to format
        include_symbol: Whether to include ₹ symbol
    
    Returns:
        Formatted string (e.g., "₹1,23,456.78" or "1,23,456.78")
    """
    try:
        # Convert to float if it's not already
        amount = float(amount)
        
        # Format with 2 decimal places
        formatted = f"{amount:,.2f}"
        
        # Convert to Indian numbering system (lakhs/crores)
        # For amounts >= 100,000 (1 lakh), use Indian comma format
        if amount >= 100000:
            # Remove commas and reformat with Indian system
            amount_str = f"{amount:.2f}"
            integer_part, decimal_part = amount_str.split('.')
            
            # Reverse the string for easier processing
            integer_part = integer_part[::-1]
            
            # Add commas according to Indian system (3,2,2,2...)
            formatted_parts = []
            for i, digit in enumerate(integer_part):
                if i == 3:  # First comma after 3 digits (thousands)
                    formatted_parts.append(',')
                elif i > 3 and (i - 3) % 2 == 0:  # Subsequent commas every 2 digits
                    formatted_parts.append(',')
                formatted_parts.append(digit)
            
            # Reverse back and add decimal part
            formatted = ''.join(formatted_parts[::-1]) + '.' + decimal_part
        
        # Add rupee symbol if requested
        if include_symbol:
            return f"₹{formatted}"
        else:
            return formatted
            
    except (ValueError, TypeError):
        # Fallback for invalid input
        return "₹0.00" if include_symbol else "0.00"


def format_inr_short(amount: float, include_symbol: bool = True) -> str:
    """
    Format amount with abbreviated notation (K, L, Cr)
    
    Args:
        amount: The numeric amount to format
        include_symbol: Whether to include ₹ symbol
    
    Returns:
        Abbreviated formatted string (e.g., "₹1.2L", "₹5.6Cr")
    """
    try:
        amount = float(amount)
        symbol = "₹" if include_symbol else ""
        
        if amount >= 10000000:  # 1 crore or more
            return f"{symbol}{amount/10000000:.1f}Cr"
        elif amount >= 100000:  # 1 lakh or more
            return f"{symbol}{amount/100000:.1f}L"
        elif amount >= 1000:  # 1 thousand or more
            return f"{symbol}{amount/1000:.1f}K"
        else:
            return f"{symbol}{amount:.2f}"
            
    except (ValueError, TypeError):
        return "₹0.00" if include_symbol else "0.00"


def currency_name() -> str:
    """Return the currency name"""
    return "Indian Rupees"


def currency_symbol() -> str:
    """Return the currency symbol"""
    return "₹"


def currency_code() -> str:
    """Return the currency code"""
    return "INR"


# Example usage and tests
if __name__ == "__main__":
    # Test cases
    test_amounts = [
        25.50,
        1250.75,
        12500.00,
        125000.50,
        1250000.75,
        12500000.00
    ]
    
    print("Currency Formatter Test Results:")
    print("-" * 50)
    
    for amount in test_amounts:
        regular = format_inr(amount)
        short = format_inr_short(amount)
        print(f"Amount: {amount:>12} → {regular:>15} ({short:>8})")
    
    print(f"\nCurrency: {currency_name()} ({currency_code()})")
    print(f"Symbol: {currency_symbol()}")