import random
from datetime import datetime

def generate_unique_id(country_full_name):
    # Take first two letters, uppercase
    country_code = country_full_name.strip()[:2].upper()
    
    year = datetime.now().year % 100  # last two digits of year, e.g. 2025 -> 25
    random_number = random.randint(1, 99999)  # random number between 1 and 99999
    random_number_str = str(random_number).zfill(5)  # zero-pad to 5 digits

    unique_id = f"{country_code}/{random_number_str}/{year}"
    return unique_id
