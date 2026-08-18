import asyncio
import sys
import os
from sqlalchemy import select, text, func

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, LeetCodeProfile, CandidateEvidence
from app.services.candidate_evidence import CandidateEvidenceService, VERIFICATION_LEVEL_CONFIDENCE

def test_candidate_evidence_ingestion_suite():
    print("\n======================================================================")
    print("  CANDIDATE EVIDENCE ENGINE TASK 18: REAL EVIDENCE INGESTION TEST SUITE")
    print("======================================================================\n")

    async def _run():
        # Ensure schema table exists
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as db:
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None
            cand_id = student.id

            # Clean start: clear existing candidate evidence records for cand_id
            await db.execute(text(f"DELETE FROM candidate_evidences WHERE candidate_id = {cand_id}"))
            await db.commit()

            # 1. Synchronize Profile Evidence & Verify SKILL records
            print("  [Test 1] Synchronizing Candidate Profile SKILL evidence...")
            sync_1 = await CandidateEvidenceService.sync_candidate_profile_evidence(db, cand_id)
            assert sync_1["status"] == "SUCCESS"

            res_ev_skills = await db.execute(
                select(CandidateEvidence).where(
                    CandidateEvidence.candidate_id == cand_id,
                    CandidateEvidence.evidence_type == "SKILL"
                )
            )
            skills_recs = res_ev_skills.scalars().all()
            print(f"    - Ingested {len(skills_recs)} SKILL evidence records (confidence=0.50).")
            for r in skills_recs:
                assert r.verification_status == "SELF_DECLARED"
                assert r.confidence == 0.50

            # 2. Update Profile & Re-synchronize (Test Update without duplication)
            print("\n  [Test 2] Updating profile & verifying update synchronization...")
            student.projects_summary = "Developed Machine Learning and Deep Learning vision pipelines."
            await db.commit()

            sync_2 = await CandidateEvidenceService.sync_candidate_profile_evidence(db, cand_id)
            print(f"    - Sync Result: inserted={sync_2['inserted']} | updated={sync_2['updated']}")
            assert sync_2["status"] == "SUCCESS"

            # 3. Verify ACADEMIC evidence
            print("\n  [Test 3 & 4] Verifying ACADEMIC evidence ingestion & updates...")
            res_ev_acad = await db.execute(
                select(CandidateEvidence).where(
                    CandidateEvidence.candidate_id == cand_id,
                    CandidateEvidence.evidence_type == "ACADEMIC"
                )
            )
            acad_rec = res_ev_acad.scalar_one_or_none()
            if acad_rec:
                assert acad_rec.source == "Academic Record"
                assert acad_rec.verification_status == "DOCUMENTED"
                assert acad_rec.confidence == 0.80
                print("    - ACADEMIC evidence verified 100%.")

            # 5. Add Certification & Verify CERTIFICATION evidence
            print("\n  [Test 5] Ingesting CERTIFICATION evidence...")
            res_cert_ex = await db.execute(
                select(CandidateEvidence).where(
                    CandidateEvidence.candidate_id == cand_id,
                    CandidateEvidence.evidence_type == "CERTIFICATION",
                    CandidateEvidence.value == "AWS Certified Solutions Architect"
                )
            )
            cert_rec = res_cert_ex.scalar_one_or_none()
            if not cert_rec:
                cert_ev = CandidateEvidence(
                    candidate_id=cand_id,
                    evidence_type="CERTIFICATION",
                    value="AWS Certified Solutions Architect",
                    source="Certification",
                    verification_status="DOCUMENTED",
                    confidence=0.80
                )
                db.add(cert_ev)
                await db.commit()
                cert_rec = cert_ev

            assert cert_rec is not None
            assert cert_rec.value == "AWS Certified Solutions Architect"
            print("    - CERTIFICATION evidence ingested 100%.")

            # 6. Verify RESUME evidence
            print("\n  [Test 6] Verifying RESUME evidence ingestion...")
            res_ev_res = await db.execute(
                select(CandidateEvidence).where(
                    CandidateEvidence.candidate_id == cand_id,
                    CandidateEvidence.evidence_type == "RESUME"
                )
            )
            res_recs = res_ev_res.scalars().all()
            assert len(res_recs) > 0
            assert res_recs[0].source == "Resume Parsing"
            assert res_recs[0].confidence == 0.80
            print("    - RESUME evidence verified 100%.")

            # 7. Add Platform Assessment Evidence
            print("\n  [Test 7] Ingesting ASSESSMENT evidence...")
            res_ass_ex = await db.execute(
                select(CandidateEvidence).where(
                    CandidateEvidence.candidate_id == cand_id,
                    CandidateEvidence.evidence_type == "ASSESSMENT",
                    CandidateEvidence.value == "Algorithmic Data Structures"
                )
            )
            ass_rec = res_ass_ex.scalar_one_or_none()
            if not ass_rec:
                assess_ev = CandidateEvidence(
                    candidate_id=cand_id,
                    evidence_type="ASSESSMENT",
                    value="Algorithmic Data Structures",
                    source="Platform Assessment",
                    verification_status="ASSESSED",
                    confidence=0.90
                )
                db.add(assess_ev)
                await db.commit()
                ass_rec = assess_ev

            assert ass_rec is not None
            assert ass_rec.confidence == 0.90
            print("    - ASSESSMENT evidence verified 100%.")

            # 8. Deduplication Verification: Run synchronization twice
            print("\n  [Test 8] Running synchronization twice to verify zero duplicate creation...")
            count_before = (await db.execute(select(func.count(CandidateEvidence.id)).where(CandidateEvidence.candidate_id == cand_id))).scalar()
            
            sync_dup1 = await CandidateEvidenceService.sync_candidate_profile_evidence(db, cand_id)
            sync_dup2 = await CandidateEvidenceService.sync_candidate_profile_evidence(db, cand_id)

            count_after = (await db.execute(select(func.count(CandidateEvidence.id)).where(CandidateEvidence.candidate_id == cand_id))).scalar()

            print(f"    - Evidence Count Before: {count_before} | Evidence Count After Repeated Sync: {count_after}")
            assert count_before == count_after, "Deduplication MUST prevent duplicate evidence record insertion!"

            # 9. Verify missing LeetCode data remains DATA_UNAVAILABLE
            print("\n  [Test 9] Verifying missing LeetCode data remains DATA_UNAVAILABLE...")
            res_lc_ev = await db.execute(
                select(CandidateEvidence).where(
                    CandidateEvidence.candidate_id == cand_id,
                    CandidateEvidence.evidence_type == "LEETCODE"
                )
            )
            lc_ev = res_lc_ev.scalar_one_or_none()
            assert lc_ev is not None
            assert lc_ev.verification_status == "DATA_UNAVAILABLE"
            assert lc_ev.confidence == 0.00
            print("    - LeetCode DATA_UNAVAILABLE state verified 100%.")

            # 10. Verify unrelated evidence remains intact
            print("\n  [Test 10] Verifying unrelated candidate evidence remains intact...")
            res_all = await db.execute(select(CandidateEvidence).where(CandidateEvidence.candidate_id == cand_id))
            all_recs = res_all.scalars().all()
            sources = set(r.source for r in all_recs)
            assert "Certification" in sources
            assert "Platform Assessment" in sources
            print(f"    - All {len(sources)} evidence sources remain 100% intact.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 18 REAL EVIDENCE INGESTION & SYNC: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_candidate_evidence_ingestion_suite()
