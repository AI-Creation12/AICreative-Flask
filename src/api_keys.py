from datetime import datetime
from .config import REQUESTS_PLAN, API_KEY, API_KEY_2

API_KEYS = [
    {"key": API_KEY, "usage": [0]*24},
    {"key": API_KEY_2, "usage": [0]*24}
]

def get_current_hour():
    return datetime.utcnow().hour

def get_max_requests_this_hour():
    hour = get_current_hour()
    return REQUESTS_PLAN.get(hour, 10)

def get_available_key():
    hour = get_current_hour()
    max_requests = get_max_requests_this_hour()
    # DEBUG
    # print(hour,max_requests)
    
    for key in API_KEYS:
        if key["usage"][hour] < max_requests:
            key["usage"][hour] += 1
            return key["key"]
    return None

def get_remaining_time_in_hour():
    now = datetime.utcnow()
    return 60 * (60 - now.minute) - now.second