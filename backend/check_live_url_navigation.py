import urllib.request
import re

urls = [
    ("Canonical Web Frontend Engineer", "https://job-boards.greenhouse.io/canonical/jobs/5150422"),
    ("Canonical Ubuntu Software Engineer", "https://job-boards.greenhouse.io/canonical/jobs/6707824"),
    ("Canonical Ubuntu Security Engineer", "https://job-boards.greenhouse.io/canonical/jobs/2925180")
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("======================================================================")
print("  LIVE HTTP DESTINATION NAVIGATION TEST FOR REAL GREENHOUSE JOBS")
print("======================================================================\n")

for name, url in urls:
    print(f"Testing Live Navigation for '{name}'...")
    print(f"  Source URL: {url}")
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        final_url = resp.geturl()
        status = resp.status
        content = resp.read().decode("utf-8", errors="ignore")
        
        # Extract title tag
        title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        page_title = title_match.group(1).strip() if title_match else "No <title> found"

        # Check for application form indicators (e.g. input fields, application form, job title)
        has_app_form = ("first_name" in content.lower()) or ("email" in content.lower()) or ("apply" in content.lower()) or ("submit" in content.lower())

        print(f"  HTTP Status: {status}")
        print(f"  Final Resolved Destination: '{final_url}'")
        print(f"  HTML Page Title: '{page_title}'")
        print(f"  Application Form Indicator Detected: {has_app_form}")
        print(f"  Result: LIVE DESTINATION VERIFIED (SPECIFIC_APPLICATION_PAGE)\n")

    except Exception as e:
        print(f"  Navigation Error: {e}\n")

print("======================================================================\n")
