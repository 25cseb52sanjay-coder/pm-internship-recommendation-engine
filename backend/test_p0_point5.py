import asyncio
from app.db.database import AsyncSessionLocal
from app.db.models import User, StudentProfile, UserRole, SchemeRule
from app.services.eligibility import DynamicEligibilityService
from sqlalchemy import delete

def test_pm_scheme_eligibility_rules():
    print("\n======================================================================")
    print("  AUDIT TEST: P0 POINT 5 — COMPLETE PM SCHEME HARD ELIGIBILITY RULES")
    print("======================================================================\n")

    async def run_boundary_tests():
        async with AsyncSessionLocal() as db:
            # Clean up prior test records for idempotency
            await db.execute(delete(StudentProfile).where(StudentProfile.id.in_([10, 11, 12])))
            await db.execute(delete(User).where(User.id.in_([10, 11, 12])))
            await db.commit()

            # Create user 10 (Positive: Age 22)
            u10 = User(id=10, email="cand10@sih.gov.in", password_hash="TEST_HASH", full_name="Candidate 10", role=UserRole.STUDENT)
            db.add(u10)
            await db.flush()
            cand_eligible = StudentProfile(id=10, user_id=10, age=22, qualification="Graduate", degree="B.Tech")
            db.add(cand_eligible)

            # Create user 11 (Negative: Age 20 - Underage)
            u11 = User(id=11, email="cand11@sih.gov.in", password_hash="TEST_HASH", full_name="Candidate 11", role=UserRole.STUDENT)
            db.add(u11)
            await db.flush()
            cand_young = StudentProfile(id=11, user_id=11, age=20, qualification="Graduate", degree="B.Tech")
            db.add(cand_young)

            # Create user 12 (Negative: Age 25 - Overage)
            u12 = User(id=12, email="cand12@sih.gov.in", password_hash="TEST_HASH", full_name="Candidate 12", role=UserRole.STUDENT)
            db.add(u12)
            await db.flush()
            cand_old = StudentProfile(id=12, user_id=12, age=25, qualification="Graduate", degree="B.Tech")
            db.add(cand_old)

            await db.commit()

            # 1. Test Positive Case: Age 22
            res_pass = await DynamicEligibilityService.evaluate_student_eligibility(db, student_id=10)
            print(f"  [1] Positive Case (Age 22, B.Tech): Status = {res_pass['eligibility_status']}, Eligible = {res_pass['is_eligible']}")
            assert res_pass['is_eligible'] == True, "Age 22 candidate should be eligible"

            # 2. Test Negative Case: Age 20 (Underage boundary)
            res_young = await DynamicEligibilityService.evaluate_student_eligibility(db, student_id=11)
            print(f"  [2] Negative Case (Age 20, Underage): Status = {res_young['eligibility_status']}, Reasons = {res_young['reasons']}")
            assert res_young['is_eligible'] == False, "Age 20 candidate must be disqualified"

            # 3. Test Negative Case: Age 25 (Overage boundary)
            res_old = await DynamicEligibilityService.evaluate_student_eligibility(db, student_id=12)
            print(f"  [3] Negative Case (Age 25, Overage): Status = {res_old['eligibility_status']}, Reasons = {res_old['reasons']}")
            assert res_old['is_eligible'] == False, "Age 25 candidate must be disqualified"

    asyncio.run(run_boundary_tests())

    print("\n======================================================================")
    print("  VERIFICATION RESULT: P0 POINT 5 PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_pm_scheme_eligibility_rules()
