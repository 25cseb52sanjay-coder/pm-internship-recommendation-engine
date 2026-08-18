"use client";

import { X, CheckCircle2, AlertTriangle, Sparkles, Building, Info } from "lucide-react";

interface ExplainabilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  internshipTitle: string;
  companyName: string;
  score: number;
  matchCategory: string;
  explanation: {
    summary: string;
    matched_skills: string[];
    missing_required_skills: string[];
    education_status: string;
    location_status: string;
    breakdown: {
      skill_match: number;
      semantic_similarity: number;
      education_match: number;
      career_interest: number;
      location_match: number;
      experience_relevance: number;
      internship_preference: number;
    };
    reasons: string[];
  };
}

export default function ExplainabilityModal({
  isOpen,
  onClose,
  internshipTitle,
  companyName,
  score,
  matchCategory,
  explanation,
}: ExplainabilityModalProps) {
  if (!isOpen) return null;

  const getCategoryBadgeClass = (cat: string) => {
    switch (cat) {
      case "Excellent Match":
        return "bg-emerald-100 text-emerald-800 border-emerald-300 font-bold";
      case "Strong Match":
        return "bg-blue-100 text-blue-800 border-blue-300 font-bold";
      case "Good Match":
        return "bg-amber-100 text-amber-800 border-amber-300 font-bold";
      default:
        return "bg-slate-100 text-slate-700 border-slate-300 font-semibold";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="relative w-full max-w-2xl bg-white border border-slate-300 rounded-md shadow-2xl overflow-hidden text-slate-800 max-h-[90vh] flex flex-col">
        
        {/* Government Header */}
        <div className="p-4 bg-[#002147] text-white flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className="flex items-center justify-center w-14 h-14 rounded bg-white text-[#002147] font-black text-xl border-2 border-amber-500 shrink-0">
              {Math.round(score)}%
            </div>
            <div>
              <span className={`inline-block px-2 py-0.5 text-[11px] rounded border mb-1 ${getCategoryBadgeClass(matchCategory)}`}>
                {matchCategory}
              </span>
              <h3 className="text-base font-bold text-white leading-tight">{internshipTitle}</h3>
              <p className="text-xs text-slate-300 flex items-center mt-0.5">
                <Building className="w-3.5 h-3.5 mr-1" /> {companyName}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content Body */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1 custom-scrollbar text-xs">
          
          {/* Official Evaluation Summary Box */}
          <div className="p-4 rounded bg-blue-50 border border-blue-200 text-slate-800 flex items-start space-x-3">
            <Info className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-[#002147] text-sm">AI Recommendation Evaluation Summary</h4>
              <p className="text-slate-700 mt-1 leading-relaxed">{explanation.summary}</p>
            </div>
          </div>

          {/* Sub-score Breakdown Bars */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2.5">AI Compatibility Index Breakdown</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              
              <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                <div className="flex justify-between mb-1">
                  <span className="font-semibold text-slate-700">Skill Match Score</span>
                  <span className="font-bold text-blue-700">{explanation.breakdown.skill_match}%</span>
                </div>
                <div className="w-full h-2 rounded bg-slate-200 overflow-hidden">
                  <div className="h-full bg-blue-600 rounded" style={{ width: `${explanation.breakdown.skill_match}%` }} />
                </div>
              </div>

              <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                <div className="flex justify-between mb-1">
                  <span className="font-semibold text-slate-700">Semantic Overlap</span>
                  <span className="font-bold text-purple-700">{explanation.breakdown.semantic_similarity}%</span>
                </div>
                <div className="w-full h-2 rounded bg-slate-200 overflow-hidden">
                  <div className="h-full bg-purple-600 rounded" style={{ width: `${explanation.breakdown.semantic_similarity}%` }} />
                </div>
              </div>

              <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                <div className="flex justify-between mb-1">
                  <span className="font-semibold text-slate-700">Academic Alignment</span>
                  <span className="font-bold text-emerald-700">{explanation.breakdown.education_match}%</span>
                </div>
                <div className="w-full h-2 rounded bg-slate-200 overflow-hidden">
                  <div className="h-full bg-emerald-600 rounded" style={{ width: `${explanation.breakdown.education_match}%` }} />
                </div>
              </div>

              <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                <div className="flex justify-between mb-1">
                  <span className="font-semibold text-slate-700">Location Compatibility</span>
                  <span className="font-bold text-amber-700">{explanation.breakdown.location_match}%</span>
                </div>
                <div className="w-full h-2 rounded bg-slate-200 overflow-hidden">
                  <div className="h-full bg-amber-600 rounded" style={{ width: `${explanation.breakdown.location_match}%` }} />
                </div>
              </div>

            </div>
          </div>

          {/* Matched Skills */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">Matched Candidate Skills</h4>
            <div className="flex flex-wrap gap-1.5">
              {explanation.matched_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 flex items-center space-x-1"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                  <span>{skill}</span>
                </span>
              ))}
            </div>
          </div>

          {/* Missing Required Skills */}
          {explanation.missing_required_skills.length > 0 && (
            <div>
              <h4 className="font-bold text-amber-800 uppercase tracking-wider mb-2">Missing Skills to Acquire</h4>
              <div className="flex flex-wrap gap-1.5">
                {explanation.missing_required_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-300 flex items-center space-x-1"
                  >
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
                    <span>{skill}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Task 19: Evidence Used & Provenance Breakdown */}
          {explanation.evidence_used && explanation.evidence_used.length > 0 && (
            <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-md space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-emerald-950 uppercase tracking-wider text-[11px] flex items-center space-x-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                  <span>Candidate Evidence Provenance & Confidence</span>
                </h4>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-white text-emerald-900 border border-emerald-300">
                  Confidence: {explanation.confidence || "HIGH"}
                </span>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {explanation.evidence_used.map((ev: any, idx: number) => (
                  <div key={idx} className="p-2 bg-white border border-emerald-200 rounded flex items-center justify-between text-[11px]">
                    <div>
                      <span className="font-bold text-slate-900">{ev.skill}</span>
                      <p className="text-[10px] text-slate-500">{ev.source} • {ev.verification_status}</p>
                    </div>
                    <span className="font-mono text-[10px] font-bold text-emerald-800 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                      {Math.round(ev.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Specific Match Bullet Reasons */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">Primary Recommendation Factors</h4>
            <ul className="space-y-1.5">
              {explanation.reasons.map((reason: string, idx: number) => (
                <li key={idx} className="text-slate-700 flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#002147] mt-1.5 shrink-0" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>

        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-bold bg-[#002147] hover:bg-[#001529] text-white rounded transition-colors"
          >
            Close Evaluation
          </button>
        </div>

      </div>
    </div>
  );
}
