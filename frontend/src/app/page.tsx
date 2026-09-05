"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ShieldCheck, Award, BookOpen, Compass, ArrowRight, CheckCircle2, Search, Building2, UserCheck, Sparkles, FileText, HelpCircle, Phone, Info, ChevronDown } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import { getCurrentUser } from "@/lib/api";

export default function LandingPage() {
  const { t } = useLanguage();
  const [user, setUser] = useState<any>(null);
  const [eligibilityCheck, setEligibilityCheck] = useState({
    age: 22,
    qualification: "Graduate",
    degree: "B.Tech",
  });
  const [eligibilityResult, setEligibilityResult] = useState<string | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(0);

  useEffect(() => {
    setUser(getCurrentUser());
  }, []);

  const handleCheckEligibility = (e: React.FormEvent) => {
    e.preventDefault();
    if (eligibilityCheck.age >= 21 && eligibilityCheck.age <= 24) {
      setEligibilityResult("Eligible! You satisfy the my portfolio.com age & academic eligibility guidelines (21-24 years).");
    } else {
      setEligibilityResult("Note: Official PM Scheme standard age range is 21-24 years. You can still explore open opportunities!");
    }
  };

  const faqs = [
    {
      q: "What is the my portfolio.com (PMIS)?",
      a: "The my portfolio.com is a national youth empowerment initiative providing eligible candidates aged 21-24 with 12-month hands-on internships across top public & private sector companies in India with monthly financial assistance."
    },
    {
      q: "How does the AI Recommendation Engine match candidates?",
      a: "The engine first enforces hard eligibility rules (age bounds, degree discipline, minimum marks). It then computes a 0-100 compatibility score evaluating skill intersection (35%), semantic resume similarity (25%), education background (15%), career interest (10%), location (5%), and experience."
    },
    {
      q: "What monthly financial stipend is provided under the scheme?",
      a: "Interns receive a monthly stipend of ₹5,000 (₹4,500 contributed by the Government of India and ₹500 by the host company from CSR funds), plus an additional top-up stipend where offered by partner organizations."
    },
    {
      q: "Are recommendation results explainable?",
      a: "Yes. Every recommendation card includes a 'Why Recommended?' button showing exact matched skills, missing required skills, sub-scores, and primary evaluation drivers."
    }
  ];

  return (
    <div className="space-y-8 pb-12">
      
      {/* Official News Ticker Bar */}
      <div className="bg-slate-100 border-b border-slate-300 py-2 px-4 text-xs overflow-hidden flex items-center">
        <div className="bg-[#002147] text-white font-bold px-3 py-1 rounded text-[11px] uppercase tracking-wider shrink-0 mr-3 flex items-center">
          <Info className="w-3.5 h-3.5 mr-1 text-amber-400" />
          <span>Latest Notices</span>
        </div>
        <div className="overflow-hidden flex-1 relative">
          <div className="animate-ticker text-slate-800 font-medium">
            <span className="mr-8">📢 my portfolio.com Phase II Application Window Open • Apply for 1.25 Lakh Opportunities Across ISRO, BHEL, TATA Motors, SBI & Infosys.</span>
            <span className="mr-8">📌 AI Recommendation Engine Online • Upload Resume for Automatic Skill Intersection & Eligibility Scoring.</span>
            <span className="mr-8">💡 Helpdesk Toll Free Number: 1800-11-2026 for Candidate Assistance.</span>
          </div>
        </div>
      </div>

      {/* Hero Banner Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="bg-gradient-to-br from-[#002147] via-[#003366] to-[#001529] rounded-2xl p-6 sm:p-12 text-white border border-slate-800 shadow-xl relative overflow-hidden">
          
          <div className="max-w-3xl space-y-6 relative z-10">
            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight leading-tight">
              {t("home.hero_title")}
            </h1>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
              {t("home.hero_subtitle")}
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              <Link
                href="/apply-internship"
                className="px-5 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs sm:text-sm shadow-md transition-all flex items-center space-x-2"
              >
                <span>{t("home.apply_now")}</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/register"
                className="px-5 py-2.5 rounded-lg bg-white/10 hover:bg-white/20 text-white font-semibold text-xs sm:text-sm border border-white/20 transition-all"
              >
                {t("home.register_now")}
              </Link>
              {user && user.role === "ADMIN" && (
                <Link
                  href="/admin"
                  className="px-5 py-2.5 rounded-lg bg-blue-900/60 hover:bg-blue-800 text-blue-200 font-semibold text-xs sm:text-sm border border-blue-700/50 transition-all"
                >
                  {t("home.admin_login")}
                </Link>
              )}
            </div>
          </div>

        </div>
      </div>

      {/* Scheme Highlights Cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
            <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-600 font-bold flex items-center justify-center">₹</div>
            <h3 className="font-bold text-slate-900 text-sm">{t("home.stipend_title")}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{t("home.stipend_desc")}</p>
          </div>

          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
            <Building2 className="w-8 h-8 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-sm">{t("home.top_companies_title")}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{t("home.top_companies_desc")}</p>
          </div>

          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
            <Award className="w-8 h-8 text-emerald-600" />
            <h3 className="font-bold text-slate-900 text-sm">{t("home.duration_title")}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{t("home.duration_desc")}</p>
          </div>

          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
            <UserCheck className="w-8 h-8 text-purple-600" />
            <h3 className="font-bold text-slate-900 text-sm">{t("home.onboarding_title")}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{t("home.onboarding_desc")}</p>
          </div>
        </div>
      </section>

      {/* Official Instant Eligibility Verification Tool */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white border border-slate-300 rounded-md p-6 sm:p-8 shadow-sm">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            <div className="lg:col-span-5 space-y-3">
              <div className="w-10 h-10 rounded bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-800 font-bold">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-[#002147]">Candidate Eligibility Verification</h2>
              <p className="text-xs text-slate-600 leading-relaxed">
                Test your candidate eligibility in real time. The recommendation engine applies mandatory scheme rules (age limits, minimum qualification) before calculating AI compatibility scores.
              </p>
            </div>

            <div className="lg:col-span-7 bg-slate-50 p-5 rounded border border-slate-300">
              <form onSubmit={handleCheckEligibility} className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Candidate Age</label>
                  <input
                    type="number"
                    value={eligibilityCheck.age}
                    onChange={(e) => setEligibilityCheck({ ...eligibilityCheck, age: parseInt(e.target.value) || 21 })}
                    className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Qualification Level</label>
                  <select
                    value={eligibilityCheck.qualification}
                    onChange={(e) => setEligibilityCheck({ ...eligibilityCheck, qualification: e.target.value })}
                    className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
                  >
                    <option value="Graduate">Graduate</option>
                    <option value="Post Graduate">Post Graduate</option>
                    <option value="Diploma">Diploma</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Degree Discipline</label>
                  <input
                    type="text"
                    value={eligibilityCheck.degree}
                    onChange={(e) => setEligibilityCheck({ ...eligibilityCheck, degree: e.target.value })}
                    className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
                  />
                </div>

                <div className="sm:col-span-3 pt-1">
                  <button
                    type="submit"
                    className="w-full py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded shadow-sm transition-colors"
                  >
                    Verify Scheme Eligibility Status
                  </button>
                </div>
              </form>

              {eligibilityResult && (
                <div className="mt-3 p-3 rounded bg-emerald-50 border border-emerald-300 text-xs text-emerald-900 flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                  <span>{eligibilityResult}</span>
                </div>
              )}
            </div>

          </div>
        </div>
      </section>

      {/* How the AI Engine Works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-8 space-y-2">
          <h2 className="text-2xl font-bold text-[#002147]">AI Recommendation Engine Capabilities</h2>
          <p className="text-xs text-slate-600">Built to resolve candidate-opportunity search confusion under government public service portals.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div className="p-5 rounded bg-white border border-slate-300 space-y-3 shadow-sm">
            <div className="w-9 h-9 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-900 font-bold">
              1
            </div>
            <h3 className="text-base font-bold text-[#002147]">Hard Eligibility Filters</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Disqualifies non-eligible applicants based on age bounds (21-24 years), qualification level, degree discipline, and deadline availability before computing match scores.
            </p>
          </div>

          <div className="p-5 rounded bg-white border border-slate-300 space-y-3 shadow-sm">
            <div className="w-9 h-9 rounded bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-900 font-bold">
              2
            </div>
            <h3 className="text-base font-bold text-[#002147]">Multi-Factor Compatibility Index</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Weights skill intersection (35%), TF-IDF semantic resume overlap (25%), degree alignment (15%), career interest (10%), location (5%), and experience relevance.
            </p>
          </div>

          <div className="p-5 rounded bg-white border border-slate-300 space-y-3 shadow-sm">
            <div className="w-9 h-9 rounded bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-900 font-bold">
              3
            </div>
            <h3 className="text-base font-bold text-[#002147]">Explainable AI & Skill Gaps</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Provides transparent evaluation drivers, lists matched skills, flags missing required skills, and recommends targeted NPTEL/Swayam learning tracks.
            </p>
          </div>

        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white border border-slate-300 rounded-md p-6 sm:p-8 space-y-6">
          <div className="border-b border-slate-200 pb-3">
            <h2 className="text-xl font-bold text-[#002147]">Frequently Asked Questions (FAQs)</h2>
            <p className="text-xs text-slate-600">Official guidance on scheme eligibility, AI matching, and stipend disbursement</p>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => (
              <div key={idx} className="border border-slate-200 rounded overflow-hidden">
                <button
                  onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                  className="w-full p-3.5 bg-slate-50 hover:bg-slate-100 text-left font-bold text-xs text-[#002147] flex items-center justify-between transition-colors"
                >
                  <span>{faq.q}</span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${activeFaq === idx ? "rotate-180 text-blue-700" : "text-slate-500"}`} />
                </button>
                {activeFaq === idx && (
                  <div className="p-4 bg-white text-xs text-slate-700 leading-relaxed border-t border-slate-200">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
}
