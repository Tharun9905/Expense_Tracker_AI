CATEGORY_KEYWORDS = {
    'Food & Dining': ['restaurant', 'cafe', 'food', 'dining', 'pizza', 'burger', 'coffee', 'lunch', 'dinner', 'breakfast', 'grocery', 'supermarket'],
    'Transportation': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking', 'metro', 'bus', 'train', 'flight', 'airline'],
    'Shopping': ['amazon', 'walmart', 'target', 'mall', 'store', 'shop', 'clothing', 'shoes', 'electronics'],
    'Entertainment': ['movie', 'theater', 'cinema', 'concert', 'game', 'spotify', 'netflix', 'subscription'],
    'Healthcare': ['hospital', 'doctor', 'pharmacy', 'medicine', 'clinic', 'medical', 'health', 'dental'],
    'Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'cable', 'utility'],
    'Education': ['school', 'college', 'university', 'course', 'tuition', 'books', 'education'],
    'Housing': ['rent', 'mortgage', 'maintenance', 'repair', 'furniture', 'home'],
    'Other': []
}

def categorize_expense(description, amount=0):
    if not description:
        return 'Other'
    description_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return 'Other'

def predict_category(description, amount=0, return_all=False):
    if not description:
        return 'Other'
    description_lower = description.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in description_lower)
        if score > 0:
            scores[category] = score
    if not scores:
        return 'Other'
    return max(scores, key=scores.get)
