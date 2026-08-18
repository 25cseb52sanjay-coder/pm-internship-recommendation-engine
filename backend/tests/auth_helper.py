import os
import json
import urllib.request

def get_test_base_url() -> str:
    return os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

def get_student_credentials():
    email = os.getenv("TEST_STUDENT_EMAIL", "student@sih.gov.in")
    password = os.getenv("TEST_STUDENT_PASSWORD", "password123")
    if not email or not password:
        raise ValueError("TEST_STUDENT_EMAIL and TEST_STUDENT_PASSWORD environment variables must be configured.")
    return email, password

def get_admin_credentials():
    email = os.getenv("TEST_ADMIN_EMAIL")
    password = os.getenv("TEST_ADMIN_PASSWORD")
    if not email or not password:
        raise ValueError(
            "Missing Required Test Credentials: TEST_ADMIN_EMAIL and TEST_ADMIN_PASSWORD environment variables are required. "
            "Please configure them in your test environment or .env file before running admin test suites."
        )
    return email, password

def get_student_token() -> str:
    base_url = get_test_base_url()
    email, password = get_student_credentials()
    req = urllib.request.Request(
        f"{base_url}/api/v1/auth/login",
        data=json.dumps({"email": email, "password": password, "requested_role": "STUDENT"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        return data["access_token"]
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate test student '{email}': {e}")

def get_admin_token() -> str:
    base_url = get_test_base_url()
    email, password = get_admin_credentials()
    req = urllib.request.Request(
        f"{base_url}/api/v1/auth/login",
        data=json.dumps({"email": email, "password": password, "requested_role": "ADMIN"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        return data["access_token"]
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate test admin '{email}': {e}")
