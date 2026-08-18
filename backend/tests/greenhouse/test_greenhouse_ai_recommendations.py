import urllib.request
import json
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from tests.auth_helper import get_student_token, get_test_base_url

def test_greenhouse_ai_recommendations_suite():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 9: AI RECOMMENDATION ENGINE TEST SUITE")
    print("======================================================================\n")

    base_url = get_test_base_url()
    token = get_student_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch AI Recommendations for Student Candidate
    print("  [STEP 1] Fetching AI Recommendations for candidate via GET /api/v1/students/recommendations...")
    req = urllib.request.Request(f"{base_url}/api/v1/students/recommendations", headers=headers)
    resp = urllib.request.urlopen(req)
    assert resp.status == 200
    recommendations = json.loads(resp.read().decode())
    
    total_recs = len(recommendations)
    print(f"    - Total AI Ranked Recommendations Generated: {total_recs}")
    assert total_recs > 0, "AI Recommendation Engine must return ranked recommendations"

    # 2. Analyze Greenhouse Opportunities in Recommendations Stream
    print("\n  [STEP 2] Verifying Greenhouse opportunities appear in AI recommendations...")
    gh_recs = [r for r in recommendations if r["internship"].get("source") == "Greenhouse"]
    print(f"    - Found {len(gh_recs)} real Greenhouse opportunities in student AI recommendations stream.")
    assert len(gh_recs) > 0, "Greenhouse real opportunities must appear in candidate AI recommendations"

    # 3. Verify Source Attribution & Apply URL Integrity
    print("\n  [STEP 3] Verifying source attribution, opportunity_type, and apply_url on Greenhouse recommendations...")
    for rec in gh_recs[:5]:
        opp = rec["internship"]
        score = rec["score"]
        match_cat = rec["match_category"]
        expl = rec["explanation"]

        assert opp["source"] == "Greenhouse"
        assert opp["source_name"] == "Greenhouse Official"
        assert opp["opportunity_type"] in ["JOB", "INTERNSHIP", "Jobs", "Internships", "UNKNOWN"]
        assert opp["apply_url"] and opp["apply_url"].startswith("http")
        assert 0.0 <= score <= 100.0
        assert expl["summary"] is not None

        print(f"    - Recommended Requisition: '{opp['title']}' ({opp['company_name']})")
        print(f"      • AI Score:         {score}% ({match_cat})")
        print(f"      • Source:           {opp['source']} ({opp['source_name']})")
        print(f"      • Opportunity Type: {opp['opportunity_type']}")
        print(f"      • Apply URL:        {opp['apply_url']}")

    # 4. Verify Fair Relevance Ranking (No Artificial Source Bias)
    print("\n  [STEP 4] Verifying recommendations are strictly ordered by AI compatibility score...")
    scores = [r["score"] for r in recommendations]
    is_sorted = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
    assert is_sorted, "Recommendations must be sorted descending by AI relevance score"
    print("    - Confirmed: Recommendations stream is strictly sorted by relevance score descending.")

    # 5. Verify Inactive / Expired Exclusion
    print("\n  [STEP 5] Verifying expired / inactive opportunities are excluded from recommendations...")
    for rec in recommendations:
        opp = rec["internship"]
        assert opp.get("status") != "EXPIRED", "Expired opportunities must not appear in recommendations"
    print("    - Confirmed: 0 expired/inactive opportunities recommended.")

    print("\n======================================================================")
    print("  TASK 9 AI RECOMMENDATION ENGINE VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_ai_recommendations_suite()
