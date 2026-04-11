from datetime import datetime, timedelta

def get_next_thursday():
    """Get the next Thursday date"""
    today = datetime.now().date()
    days_until_thursday = (3 - today.weekday()) % 7
    if days_until_thursday == 0:
        days_until_thursday = 7
    return today + timedelta(days=days_until_thursday)

def get_next_monday():
    """Get the next Monday date"""
    today = datetime.now().date()
    days_until_monday = (0 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    return today + timedelta(days=days_until_monday)

def calculate_hire_cost(price_per_day, pickup_date, return_date):
    """Calculate cost based on hire period"""
    days = (return_date - pickup_date).days
    # Minimum 4 days for Thursday-Monday hire
    if days < 4:
        days = 4
    return price_per_day * days
