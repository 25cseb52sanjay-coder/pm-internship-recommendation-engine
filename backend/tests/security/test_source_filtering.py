import asyncio
import urllib.request
import json
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from tests.auth_helper import get_test_base_url

def test_source_filtering_capabilities():
    print("\n======================================================================")
    print("  NCS SOURCE FILTERING TEST SUITE")
    print("======================================================================\n")

    base_url = get_test_base_url()

    # 1. Test All Sources Filter
    print("  [TEST 1] Querying GET /api/v1/internships?source=All...")
    req_all = urllib.request.Request(f"{base_url}/api/v1/internships?source=All")
    resp_all = urllib.request.urlopen(req_all)
    assert resp_all.status == 200
    data_all = json.loads(resp_all.read().decode())
    print(f"    - 'All Sources' Returned {len(data_all)} listings.")
    assert len(data_all) > 0, "All Sources filter must return active listings"

    # 2. Test NCS Filter
    print("\n  [TEST 2] Querying GET /api/v1/internships?source=NCS...")
    req_ncs = urllib.request.Request(f"{base_url}/api/v1/internships?source=NCS")
    resp_ncs = urllib.request.urlopen(req_ncs)
    assert resp_ncs.status == 200
    data_ncs = json.loads(resp_ncs.read().decode())
    print(f"    - 'NCS Source' Returned {len(data_ncs)} listings.")
    for item in data_ncs:
        assert item.get("source") == "NCS" or "NCS" in item.get("source_name", "") or "ncs.gov.in" in (item.get("apply_url") or ""), f"Item {item['id']} is not an NCS listing"
    print("    - All returned items correctly matched NCS source filter criteria.")

    print("\n======================================================================")
    print("  VERIFICATION RESULT: SOURCE FILTERING TESTS PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_source_filtering_capabilities()
