import os
import sys

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.adzuna.config import AdzunaConfig, get_adzuna_credentials, is_adzuna_configured

def test_adzuna_auth_config_suite():
    print("\n======================================================================")
    print("  ADZUNA INTEGRATION TASK 1: AUTHENTICATION CONFIGURATION TEST SUITE")
    print("======================================================================\n")

    # Save original env vars
    orig_app_id = os.environ.get("ADZUNA_APP_ID")
    orig_app_key = os.environ.get("ADZUNA_APP_KEY")

    try:
        # 1. Test Unconfigured Environment
        print("  [STEP 1] Testing unconfigured environment state...")
        if "ADZUNA_APP_ID" in os.environ:
            del os.environ["ADZUNA_APP_ID"]
        if "ADZUNA_APP_KEY" in os.environ:
            del os.environ["ADZUNA_APP_KEY"]

        app_id, app_key = AdzunaConfig.get_credentials()
        print(f"    - Unconfigured APP_ID:  {app_id}")
        print(f"    - Unconfigured APP_KEY: {app_key}")
        print(f"    - is_configured():      {AdzunaConfig.is_configured()}")
        assert not AdzunaConfig.is_configured()

        status_unconf = AdzunaConfig.get_auth_status()
        print(f"    - Auth Status Masked APP_ID: {status_unconf['app_id_masked']}")
        assert status_unconf["is_configured"] == False
        assert status_unconf["app_id_masked"] == "NOT_CONFIGURED"

        # 2. Test Environment Configuration Injection
        print("\n  [STEP 2] Injecting test environment credentials...")
        test_id = "test_adzuna_app_1234"
        test_key = "test_adzuna_key_567890abcdef"
        os.environ["ADZUNA_APP_ID"] = test_id
        os.environ["ADZUNA_APP_KEY"] = test_key

        read_id, read_key = get_adzuna_credentials()
        print(f"    - Securely Read APP_ID:  '{read_id}'")
        print(f"    - Securely Read APP_KEY: '{read_key}'")
        print(f"    - is_adzuna_configured(): {is_adzuna_configured()}")

        assert read_id == test_id
        assert read_key == test_key
        assert is_adzuna_configured() == True

        # 3. Test Security Masking (No Raw Credentials Exposure in Auth Status)
        print("\n  [STEP 3] Verifying security masking in auth status payload...")
        status_conf = AdzunaConfig.get_auth_status()
        print(f"    - Source Name:        {status_conf['source_name']}")
        print(f"    - Auth Type:          {status_conf['auth_type']}")
        print(f"    - Masked APP_ID:      {status_conf['app_id_masked']}")
        print(f"    - Raw Key Exposed?    {'ADZUNA_APP_KEY' in str(status_conf)}")

        assert status_conf["is_configured"] == True
        assert status_conf["app_id_masked"] == "test***"
        assert test_key not in str(status_conf), "Raw API key must never be exposed in status payload"

        print("\n======================================================================")
        print("  TASK 1 ADZUNA AUTH CONFIGURATION VERIFICATION: PASSED (100% SUCCESS)")
        print("======================================================================\n")

    finally:
        # Restore environment
        if orig_app_id:
            os.environ["ADZUNA_APP_ID"] = orig_app_id
        elif "ADZUNA_APP_ID" in os.environ:
            del os.environ["ADZUNA_APP_ID"]

        if orig_app_key:
            os.environ["ADZUNA_APP_KEY"] = orig_app_key
        elif "ADZUNA_APP_KEY" in os.environ:
            del os.environ["ADZUNA_APP_KEY"]

if __name__ == "__main__":
    test_adzuna_auth_config_suite()
