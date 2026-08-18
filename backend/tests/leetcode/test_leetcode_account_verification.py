import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.leetcode.verification import LeetCodeVerificationService
from app.leetcode.data_provider import (
    LeetCodeDataProvider,
    LeetCodeProviderRegistry,
    ProviderResultStatus,
    ProviderResult
)

def test_leetcode_account_verification_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 6: REAL ACCOUNT VERIFICATION AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        # 1. Test Default Unconfigured Provider Behavior (Limitation Reporting)
        print("  [STEP 1] Testing account verification with default Unconfigured Provider...")
        LeetCodeProviderRegistry.reset()
        
        res_default = await LeetCodeVerificationService.verify_account_existence("https://leetcode.com/u/valid_handle")
        print(f"    - Handle:               'valid_handle'")
        print(f"    - Account Exists:       {res_default['account_exists']}")
        print(f"    - System Status:        '{res_default['status']}'")
        print(f"    - Provider Status:      '{res_default['provider_status']}'")
        print(f"    - Message:              '{res_default['message']}'")

        assert res_default["account_exists"] is False, "URL syntax alone MUST NOT mark profile as ACCOUNT_FOUND!"
        assert res_default["status"] == "DATA_UNAVAILABLE", "Unconfigured provider must report DATA_UNAVAILABLE limitation"
        assert "limitation" in res_default["message"].lower()

        # 2. Test Result Mapping with Permitted Provider
        print("\n  [STEP 2] Testing strict result mapping with registered LeetCodeDataProvider...")

        class MockAuthorizedProvider(LeetCodeDataProvider):
            async def check_profile_exists(self, username: str) -> ProviderResult:
                if username == "found_user":
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="Profile found", timestamp="2026-08-14T00:00:00Z")
                elif username == "missing_user":
                    return ProviderResult(status=ProviderResultStatus.NOT_FOUND, message="Profile not found", timestamp="2026-08-14T00:00:00Z")
                elif username == "forbidden_user":
                    return ProviderResult(status=ProviderResultStatus.NOT_PERMITTED, message="Access not permitted", timestamp="2026-08-14T00:00:00Z")
                else:
                    return ProviderResult(status=ProviderResultStatus.ERROR, message="API error", timestamp="2026-08-14T00:00:00Z")

            async def get_profile_data(self, username: str) -> ProviderResult:
                return ProviderResult(status=ProviderResultStatus.UNAVAILABLE, message="N/A", timestamp="2026-08-14T00:00:00Z")
            async def get_profile_statistics(self, username: str) -> ProviderResult:
                return ProviderResult(status=ProviderResultStatus.UNAVAILABLE, message="N/A", timestamp="2026-08-14T00:00:00Z")
            async def get_provider_status(self) -> dict:
                return {"is_configured": True}

        LeetCodeProviderRegistry.set_provider(MockAuthorizedProvider())

        # SUCCESS -> ACCOUNT_FOUND
        res_found = await LeetCodeVerificationService.verify_account_existence("found_user")
        print(f"    - 'found_user':   status={res_found['status']} | account_exists={res_found['account_exists']}")
        assert res_found["status"] == "ACCOUNT_FOUND"
        assert res_found["account_exists"] is True

        # NOT_FOUND -> ACCOUNT_NOT_FOUND
        res_notfound = await LeetCodeVerificationService.verify_account_existence("missing_user")
        print(f"    - 'missing_user': status={res_notfound['status']} | account_exists={res_notfound['account_exists']}")
        assert res_notfound["status"] == "ACCOUNT_NOT_FOUND"
        assert res_notfound["account_exists"] is False

        # NOT_PERMITTED -> DATA_UNAVAILABLE
        res_noperm = await LeetCodeVerificationService.verify_account_existence("forbidden_user")
        print(f"    - 'forbidden_user': status={res_noperm['status']}")
        assert res_noperm["status"] == "DATA_UNAVAILABLE"
        assert res_noperm["account_exists"] is False

        # ERROR -> VERIFICATION_FAILED
        res_err = await LeetCodeVerificationService.verify_account_existence("error_user")
        print(f"    - 'error_user':    status={res_err['status']}")
        assert res_err["status"] == "VERIFICATION_FAILED"
        assert res_err["account_exists"] is False

        # Reset registry to default
        LeetCodeProviderRegistry.reset()

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 6 LEETCODE ACCOUNT VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_account_verification_suite()
