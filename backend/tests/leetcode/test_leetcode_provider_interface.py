import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.leetcode.data_provider import (
    LeetCodeDataProvider,
    UnconfiguredLeetCodeProvider,
    LeetCodeProviderRegistry,
    ProviderResultStatus,
    ProviderResult
)

def test_leetcode_provider_interface_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 5: PROVIDER INTERFACE AUDIT TEST SUITE")
    print("======================================================================\n")

    # 1. Verify Abstract Class Contract Enforcement
    print("  [STEP 1] Verifying LeetCodeDataProvider abstract interface contract...")
    try:
        instance = LeetCodeDataProvider() # Should raise TypeError
        assert False, "Instantiating raw abstract LeetCodeDataProvider must fail!"
    except TypeError as err:
        print(f"    - Abstract Instantiation Prevention Verified: {err}")

    # 2. Verify Enum Values
    print("\n  [STEP 2] Verifying ProviderResultStatus allowed enum statuses...")
    expected_statuses = {"SUCCESS", "NOT_FOUND", "UNAVAILABLE", "NOT_PERMITTED", "ERROR"}
    enum_members = {s.value for s in ProviderResultStatus}
    print(f"    - Enum Statuses Found: {enum_members}")
    assert enum_members == expected_statuses

    async def _run():
        # 3. Verify Default Unconfigured Provider Safety
        print("\n  [STEP 3] Verifying UnconfiguredLeetCodeProvider safety & zero mock data fabrication...")
        provider = UnconfiguredLeetCodeProvider()

        status_res = await provider.get_provider_status()
        print(f"    - Provider Status Response: {status_res}")
        assert status_res["is_configured"] is False
        assert status_res["status"] == "UNAVAILABLE"

        res_exist = await provider.check_profile_exists("candidate_dev")
        print(f"    - Check Profile Exists Result: status={res_exist.status}, data={res_exist.data}")
        assert res_exist.status == ProviderResultStatus.UNAVAILABLE
        assert res_exist.data is None, "Must NOT fabricate profile existence data!"

        res_data = await provider.get_profile_data("candidate_dev")
        assert res_data.status == ProviderResultStatus.UNAVAILABLE
        assert res_data.data is None, "Must NOT fabricate profile metadata!"

        res_stats = await provider.get_profile_statistics("candidate_dev")
        assert res_stats.status == ProviderResultStatus.UNAVAILABLE
        assert res_stats.data is None, "Must NOT fabricate problem statistics!"

        # 4. Verify Provider Registry Dependency Injection / Pluggability
        print("\n  [STEP 4] Verifying LeetCodeProviderRegistry pluggability & DI...")
        active_p = LeetCodeProviderRegistry.get_provider()
        assert isinstance(active_p, UnconfiguredLeetCodeProvider)

        class CustomDummyProvider(LeetCodeDataProvider):
            async def check_profile_exists(self, username: str) -> ProviderResult:
                return ProviderResult(status=ProviderResultStatus.NOT_FOUND, message="Not found", timestamp="2026-08-14T00:00:00Z")
            async def get_profile_data(self, username: str) -> ProviderResult:
                return ProviderResult(status=ProviderResultStatus.NOT_FOUND, message="Not found", timestamp="2026-08-14T00:00:00Z")
            async def get_profile_statistics(self, username: str) -> ProviderResult:
                return ProviderResult(status=ProviderResultStatus.NOT_FOUND, message="Not found", timestamp="2026-08-14T00:00:00Z")
            async def get_provider_status(self) -> dict:
                return {"is_configured": True, "provider_name": "CustomDummyProvider"}

        LeetCodeProviderRegistry.set_provider(CustomDummyProvider())
        new_p = LeetCodeProviderRegistry.get_provider()
        assert isinstance(new_p, CustomDummyProvider)

        LeetCodeProviderRegistry.reset()
        reset_p = LeetCodeProviderRegistry.get_provider()
        assert isinstance(reset_p, UnconfiguredLeetCodeProvider)
        print("    - Registry replacement and reset functionality verified 100%.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 5 LEETCODE PROVIDER INTERFACE VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_provider_interface_suite()
