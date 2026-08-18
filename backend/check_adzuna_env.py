import os
import sys

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")
country = os.getenv("ADZUNA_COUNTRY", "in")

print(f"ADZUNA_APP_ID Present: {bool(app_id)}")
print(f"ADZUNA_APP_KEY Present: {bool(app_key)}")
print(f"ADZUNA_COUNTRY: {country}")
