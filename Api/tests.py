from datetime import datetime
from django.test import TestCase
from Api.utils import generate_unique_id  # Adjust to your actual app name
from django.contrib.auth.models import User
from Api.models import Profile

class UtilsTestCase(TestCase):
    def test_generate_unique_id_format(self):
        country = "Kenya"
        unique_id = generate_unique_id(country)
        
        # Check if it starts with first two letters uppercase
        self.assertTrue(unique_id.startswith("KE/"), f"Unique ID prefix incorrect: {unique_id}")
        
        # Check length pattern: KE/00062/25
        parts = unique_id.split('/')
        self.assertEqual(len(parts), 3, f"Unique ID should have 3 parts separated by '/': {unique_id}")
        
        country_code, random_number, year = parts
        
        # Country code check
        self.assertEqual(country_code, "KE", f"Country code incorrect: {country_code}")
        
        # Random number should be 5 digits, numeric
        self.assertTrue(len(random_number) == 5 and random_number.isdigit(), f"Random number invalid: {random_number}")
        
        # Year should be last two digits of current year
        expected_year = str(datetime.now().year % 100).zfill(2)
        self.assertEqual(year, expected_year, f"Year part incorrect: {year}, expected: {expected_year}")

        print("generate_unique_id test passed!")




class ProfileUniqueIdTestCase(TestCase):
    def test_profile_unique_id_assignment(self):
        # Create a new user
        user = User.objects.create_user(username='testuser', password='password123')
        
        # Create a Profile linked to this user with a country name
        profile = Profile.objects.create(user=user, country="Kenya")
        
        # Refresh profile from DB to get updates done by signals
        profile.refresh_from_db()
        
        # Assert unique_id is assigned and has correct prefix
        self.assertIsNotNone(profile.unique_id, "unique_id should be assigned on profile creation")
        self.assertTrue(profile.unique_id.startswith("KE/"), f"unique_id format incorrect: {profile.unique_id}")

        print("Profile unique_id assignment test passed!")
