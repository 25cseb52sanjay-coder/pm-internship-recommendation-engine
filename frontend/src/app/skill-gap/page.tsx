"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { BookOpen, CheckCircle2, AlertTriangle, Compass, Sparkles } from "lucide-react";

export default function SkillGapPage() {
  const [skillGap, setSkillGap] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSkillGap() {
      try {
        const data = await fetchApi("/students/skill-gaps");
        setSkillGap(data);
      } catch (err) {
        console.error("Skill Gap load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadSkillGap();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-600">
        <div className="inline-block w-7 h-7 border-3 border-emerald-700 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs font-semibold">Analyzing Candidate Skill Intersection & Learning Roadmaps...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="border-b border-slate-300 pb-4 space-y-1">
        <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
          <BookOpen className="w-3.5 h-3.5" />
          <span>AI Skill Gap & Career Roadmap</span>
        </div>
        <h1 className="text-2xl font-bold text-[#002147]">Candidate Skill Matrix & Targeted Learning Tracks</h1>
        <p className="text-xs text-slate-600">Identify technical skills required by high-scoring opportunities and access verified NPTEL/Swayam learning modules</p>
      </div>

      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-600">Skill Readiness Score</p>
            <p className="text-2xl font-black text-emerald-800 mt-1">{skillGap?.readiness_score || 85}%</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Based on target opportunity intersection</p>
          </div>
          <div className="w-10 h-10 rounded bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-800 shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-600">Verified Profile Skills</p>
            <p className="text-2xl font-black text-blue-800 mt-1">{skillGap?.student_skills?.length || 0}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Extracted from profile & resume</p>
          </div>
          <div className="w-10 h-10 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-800 shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-600">Priority Missing Skills</p>
            <p className="text-2xl font-black text-amber-800 mt-1">{skillGap?.missing_required_skills?.length || 0}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">High-impact skills to acquire</p>
          </div>
          <div className="w-10 h-10 rounded bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-800 shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

      </div>

      {/* Recommended Career Specialization Tracks */}
      {skillGap?.career_path_suggestions?.length > 0 && (
        <div className="p-5 rounded bg-white border border-slate-300 space-y-3 shadow-sm">
          <h3 className="text-base font-bold text-[#002147] flex items-center space-x-2">
            <Compass className="w-4 h-4 text-blue-700" />
            <span>Suggested Specialization Tracks</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {skillGap.career_path_suggestions.map((track: string, idx: number) => (
              <div key={idx} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs text-blue-900 font-bold flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-blue-700" />
                <span>{track}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills Grid & Learning Recommendations */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold text-[#002147] flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-700" />
          <span>Priority Missing Skills & Recommended Learning Modules</span>
        </h2>

        {skillGap?.missing_required_skills?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {skillGap.missing_required_skills.map((item: any, idx: number) => (
              <div key={idx} className="p-4 rounded bg-white border border-slate-300 flex flex-col justify-between space-y-3 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-amber-100 text-amber-800 border border-amber-300">
                      {item.category}
                    </span>
                    <h3 className="text-base font-bold text-[#002147] mt-1">{item.skill}</h3>
                  </div>

                  <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 border border-red-200">
                    {item.priority} Priority
                  </span>
                </div>

                <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <p className="text-[11px] font-bold text-slate-700">Recommended Government Learning Course:</p>
                  <p className="text-slate-900 font-medium">{item.recommendation_course}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-white border border-slate-300 rounded">
            <CheckCircle2 className="w-6 h-6 text-emerald-700 mx-auto mb-1" />
            <p className="text-xs text-slate-800 font-bold">Excellent! No critical missing skills flagged for your top target opportunities.</p>
          </div>
        )}
      </div>

    </div>
  );
}
