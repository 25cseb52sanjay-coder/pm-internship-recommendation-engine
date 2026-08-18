import asyncio
import urllib.request
import urllib.error
import socket
import json
import sqlite3
import sys
import os
from datetime import datetime

# Set path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def audit_runtime():
    print("=" * 80)
    print("  INGESTION ENGINE REALITY & RUNTIME AUDIT REPORT")
    print("=" * 80 + "\n")

    # 1. DATABASE AUDIT: Where did the 8 current internship records come from?
    print("--- 1. DATABASE ORIGIN AUDIT (Current Internship Records) ---")
    conn = sqlite3.connect("pm_internships.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, company_name, source_id, is_demo, created_at, duplicate_fingerprint, fingerprint_sha256 FROM internships")
    rows = cursor.fetchall()
    print(f"Total Internship Records in DB: {len(rows)}")

    seed_demo_count = 0
    pipeline_count = 0

    for r in rows:
        opp_id, title, company, source_id, is_demo, created_at, fp, fp_sha = r
        is_demo_str = "DEMO / SEED DATA" if (is_demo == 1 or source_id is None) else f"PIPELINE (Source ID {source_id})"
        if is_demo == 1 or source_id is None:
            seed_demo_count += 1
        else:
            pipeline_count += 1
        print(f"  - ID {opp_id}: '{title}' @ '{company}' -> {is_demo_str} [Created: {created_at}]")

    print(f"\nOrigin Breakdown: {seed_demo_count} Seed/Demo records, {pipeline_count} Ingestion Pipeline records.")

    # 2. EXTERNAL URL REACHABILITY & DATA PROOF AUDIT
    print("\n--- 2. EXTERNAL URL REACHABILITY & DATA PROOF AUDIT ---")
    urls_to_test = [
        ("PMIS Feed URL", "https://pminternship.mca.gov.in/api/feed"),
        ("Tata Motors Career Feed URL", "https://careers.tatamotors.com/api/pm-internships"),
        ("LinkedIn API URL", "https://api.linkedin.com/v2/jobs"),
        ("Internshala Feed URL", "https://internshala.com/api/v1/feed"),
        ("Naukri API URL", "https://api.naukri.com/v1/jobs")
    ]

    for label, url in urls_to_test:
        print(f"\nTesting URL: [{label}] -> {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
                content_type = resp.headers.get('Content-Type')
                body_sample = resp.read(200).decode('utf-8', errors='ignore')
                print(f"  HTTP Status: {status}")
                print(f"  Content-Type: {content_type}")
                print(f"  Body Sample: {body_sample[:100]}...")
                print(f"  Result: REAL EXTERNAL ENDPOINT REACHABLE")
        except urllib.error.HTTPError as e:
            print(f"  HTTP Error Status: {e.code} ({e.reason})")
            print(f"  Result: ENDPOINT RESPONSIVE WITH HTTP ERROR (HTTP {e.code})")
        except urllib.error.URLError as e:
            print(f"  URL Error: {e.reason}")
            print(f"  Result: NOT REACHABLE / SIMULATED URL IN CODE")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Result: UNREACHABLE")

    # 3. REDIS & CELERY RUNTIME AUDIT
    print("\n--- 3. REDIS & CELERY WORKER RUNTIME AUDIT ---")
    redis_port_open = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        res = s.connect_ex(('127.0.0.1', 6379))
        if res == 0:
            redis_port_open = True
            print("  Redis Service on 127.0.0.1:6379: PORT OPEN & REACHABLE")
        else:
            print("  Redis Service on 127.0.0.1:6379: PORT CLOSED (Redis not running locally)")
        s.close()
    except Exception as e:
        print(f"  Redis Check Error: {e}")

    # Check Celery via python import
    try:
        import celery
        print(f"  Celery Library Installed: Version {celery.__version__}")
    except ImportError:
        print("  Celery Library: NOT INSTALLED")

    # 4. COMPONENT BY COMPONENT AUDIT & CODE INSPECTION
    print("\n--- 4. CONNECTOR & PIPELINE CODE INSPECTION ---")
    from app.ingestion.source_connectors.pmis import PMISConnector
    from app.ingestion.source_connectors.company_career import CompanyCareerConnector

    pmis = PMISConnector()
    print(f"  PMISConnector implementation type: Returns simulated/hardcoded feed array inside code: {len(asyncio.run(pmis.fetch()))} items")

    tata = CompanyCareerConnector()
    print(f"  CompanyCareerConnector implementation type: Returns simulated/hardcoded feed array inside code: {len(asyncio.run(tata.fetch()))} items")

    conn.close()

if __name__ == "__main__":
    audit_runtime()
