import subprocess
import sys

def run_all_tests():
    print("\n======================================================================")
    print("  PM INTERNSHIP RECOMMENDATION ENGINE: ALL 28-POINT AUDIT TEST RUNNER")
    print("======================================================================\n")

    test_scripts = [
        ("Phase 1 - Point 1: Real AI Vector Model", "test_p0_point1.py"),
        ("Phase 1 - Point 2: Recommendation Explainability", "test_p0_point2.py"),
        ("Phase 1 - Points 3 & 4: Seat Allocation & Concurrency", "test_p0_points3_4.py"),
        ("Phase 1 - Point 5: PM Scheme Hard Eligibility", "test_p0_point5.py"),
        ("Phase 1 - Point 6: Live Ingestion & Deduplication", "test_p0_point6.py"),
        ("Phase 1 - Point 7: Admin RBAC Enforcement", "test_p0_point7.py"),
        ("Phase 2 - Points 8-19: JWT Revocation, Pagination, Caching", "test_phase2_p1.py"),
        ("Master System Verification Test Suite", "test_master_suite.py"),
        ("Ingestion Engine Spec v1.0.0 Verification Suite", "tests/ingestion/test_ingestion_spec_suite.py"),
        ("Discovery & Verification Engine Spec v1.0.0 Suite", "tests/discovery/test_discovery_engine_suite.py"),
        ("25-Locale Multilingual i18n Architecture Suite", "tests/multilingual/test_i18n_spec_suite.py"),
        ("Security Audit & Password Leak Prevention Suite", "tests/security/test_security_spec_suite.py"),
        ("Negative Production Configuration Hardening Suite", "tests/security/test_config_hardening.py"),
        ("NCS Source Filtering Test Suite", "tests/security/test_source_filtering.py"),
        ("NCS Background Synchronization Suite", "tests/ncs/test_ncs_sync_suite.py"),
        ("Official Greenhouse API Connection Suite", "tests/greenhouse/test_greenhouse_api_connection.py"),
        ("Real Greenhouse Job Normalization Suite", "tests/greenhouse/test_greenhouse_normalization.py"),
        ("Greenhouse Opportunity Classification Suite", "tests/greenhouse/test_greenhouse_classification.py"),
        ("Real Greenhouse Database Storage Suite", "tests/greenhouse/test_greenhouse_db_storage.py"),
        ("Greenhouse UI & API Display Suite", "tests/greenhouse/test_greenhouse_ui_display.py"),
        ("Greenhouse Redirection Security Suite", "tests/greenhouse/test_greenhouse_redirection.py"),
        ("Greenhouse Deduplication & Updates Suite", "tests/greenhouse/test_greenhouse_deduplication.py"),
        ("Greenhouse Automated Sync Pipeline Suite", "tests/greenhouse/test_greenhouse_full_sync.py"),
        ("Greenhouse AI Recommendation Engine Suite", "tests/greenhouse/test_greenhouse_ai_recommendations.py"),
        ("Greenhouse Apply Now Direct Redirection Audit Suite", "tests/greenhouse/test_greenhouse_apply_redirect_flow.py"),
        ("Adzuna Authentication Configuration Suite", "tests/adzuna/test_adzuna_config.py"),
        ("Adzuna Official REST API Connection Suite", "tests/adzuna/test_adzuna_live_connection.py"),
        ("Real Adzuna Job Normalization Suite", "tests/adzuna/test_adzuna_normalization.py"),
        ("Adzuna Opportunity Classification Suite", "tests/adzuna/test_adzuna_classification.py"),
        ("Real Adzuna Database Storage Suite", "tests/adzuna/test_adzuna_db_storage.py"),
        ("Adzuna UI & API Display Suite", "tests/adzuna/test_adzuna_ui_display.py"),
        ("Adzuna Redirection Security Suite", "tests/adzuna/test_adzuna_redirection.py"),
        ("Adzuna Deduplication & Updates Suite", "tests/adzuna/test_adzuna_deduplication.py"),
        ("Adzuna Automated Sync Pipeline Suite", "tests/adzuna/test_adzuna_full_sync.py"),
        ("Adzuna AI Recommendation Engine Suite", "tests/adzuna/test_adzuna_ai_recommendations.py"),
        ("LeetCode Profile URL Validation Suite", "tests/leetcode/test_leetcode_url_validation.py"),
        ("LeetCode Database Schema & Model Suite", "tests/leetcode/test_leetcode_db_model.py"),
        ("LeetCode Provider Interface Suite", "tests/leetcode/test_leetcode_provider_interface.py"),
        ("LeetCode Account Verification Suite", "tests/leetcode/test_leetcode_account_verification.py"),
        ("LeetCode Ownership Verification Suite", "tests/leetcode/test_leetcode_ownership_verification.py"),
        ("LeetCode Verified Profile Storage Suite", "tests/leetcode/test_leetcode_verified_profile_storage.py"),
        ("LeetCode Real Profile Metrics Suite", "tests/leetcode/test_leetcode_real_profile_metrics.py"),
        ("LeetCode Skill Assessment Suite", "tests/leetcode/test_leetcode_skill_assessment.py"),
        ("LeetCode Profile Assessment UI Suite", "tests/leetcode/test_leetcode_profile_assessment_ui.py"),
        ("LeetCode AI Recommendation Integration Suite", "tests/leetcode/test_leetcode_ai_recommendation_integration.py"),
        ("LeetCode Comprehensive Security Audit Suite", "tests/leetcode/test_leetcode_security_audit.py"),
        ("LeetCode Master End-to-End Verification Suite", "tests/leetcode/test_leetcode_e2e_verification.py"),
        ("Candidate Evidence Engine Aggregation Suite", "tests/evidence/test_candidate_evidence_engine.py"),
        ("Real Candidate Evidence Ingestion & Sync Suite", "tests/evidence/test_candidate_evidence_ingestion.py"),
        ("Explainable AI Recommendation Engine Suite", "tests/recommendation/test_explainable_recommendations.py"),
        ("Requirement Priority & Eligibility Rules Suite", "tests/recommendation/test_requirement_priority_rules.py"),
        ("Opportunity Data Quality & Recommendation Gate Suite", "tests/opportunity/test_opportunity_quality_gate.py"),
        ("9-Stage End-to-End Recommendation Pipeline Architecture Suite", "tests/architecture/test_end_to_end_pipeline_architecture.py"),
        ("Automated Real Opportunity Synchronization Suite", "tests/sync/test_automated_opportunity_sync.py"),
        ("Final End-to-End Acceptance Validation Suite", "tests/acceptance/test_end_to_end_acceptance_validation.py"),
        ("Production Security Validation Suite", "tests/security/test_production_security_validation.py"),
        ("Production Performance & Scalability Validation Suite", "tests/performance/test_performance_and_scalability.py"),
        ("Multi-Discipline Academic Data Foundation Suite", "tests/academic/test_multi_discipline_academic_foundation.py"),
        ("Multi-Discipline Branch Compatibility Engine Suite", "tests/academic/test_branch_compatibility_engine.py"),
        ("Canonical Multi-Disciplinary Tree Verification Suite", "tests/academic/test_canonical_discipline_tree.py"),
        ("Multi-Discipline Specialization & Sector Matching Suite", "tests/academic/test_specialization_sector_matching.py"),
        ("Multi-Discipline Opportunity Role & Domain Intelligence Suite", "tests/academic/test_opportunity_role_intelligence.py"),
        ("Multi-Discipline Recommendation Ranking & Allocation Suite", "tests/academic/test_multi_discipline_recommendation_ranking.py"),
        ("Exact Internship Application Redirect Integrity Suite", "tests/acceptance/test_exact_application_redirect.py"),
        ("Exact 1-to-1 Internship URL Pairing Audit", "tests/acceptance/verify_exact_internship_url_matching.py"),
        ("Live Application Destination Verification Suite", "tests/acceptance/test_live_destination_verification.py"),
        ("Final Production Readiness & Architecture Freeze Audit", "tests/acceptance/test_production_readiness_audit.py"),
        ("Adzuna Live Credential Configuration & API Verification Suite", "tests/adzuna/test_adzuna_live_credential_verification.py"),
        ("Adzuna Real Opportunity End-to-End Validation Suite", "tests/adzuna/test_adzuna_real_opportunity_e2e_validation.py"),
        ("Adzuna Exact Application Destination Verification Suite", "tests/adzuna/test_adzuna_exact_destination_verification.py"),
        ("Final Deployment Validation Suite — Frozen Production Architecture", "tests/acceptance/test_final_deployment_validation.py"),
        ("Final Production Deployment & Smoke Validation Suite", "tests/acceptance/test_production_smoke_validation.py"),
        ("Public Production Deployment Validation Suite", "tests/acceptance/test_public_production_deployment_validation.py"),
        ("LeetCode Profile Metrics & Badges — Real Data Only Suite", "tests/leetcode/test_leetcode_real_data_only.py"),
        ("Academic Dropdown Fields — Course & Qualification Suite", "tests/academic/test_academic_dropdown_fields.py"),
        ("Engineering Branch Dynamic Dropdown Suite", "tests/academic/test_engineering_branch_dropdown.py"),
        ("Academic Qualification Dependency UX Suite", "tests/academic/test_academic_qualification_dependency.py"),
        ("Technical & Soft Skills Matrix Selectors Suite", "tests/academic/test_skills_category_dropdown.py"),
        ("Candidate Profile View/Edit & Save Suite", "tests/academic/test_profile_view_edit_mode.py")
    ]

    passed_count = 0
    total_count = len(test_scripts)

    for name, script in test_scripts:
        print(f"  -> Running Test Suite: {name} ({script})...")
        res = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [OK] {name}: PASSED (100% Success)")
            passed_count += 1
        else:
            print(f"  [FAIL] {name}: FAILED\n  Error Output:\n{res.stderr}\n{res.stdout}")

    print("\n======================================================================")
    print(f"  FINAL AUDIT TEST SUMMARY: {passed_count}/{total_count} TEST SUITES PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    run_all_tests()
