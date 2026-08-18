"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import InternshipCard from "@/components/InternshipCard";
import { Sparkles, BookOpen, User, Bookmark, CheckCircle, ArrowRight, ShieldCheck, AlertCircle } from "lucide-react";

export default function StudentDashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [skillGap, setSkillGap] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [profData, recData, gapData] = await Promise.all([
          fetchApi("/students/profile"),
          fetchApi("/students/recommendations"),
          fetchApi("/students/skill-gaps"),
        ]);
        setProfile(profData);
        setRecommendations(recData);
        setSkillGap(gapData);
      } catch (err) {
        console.error("Dashboard error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-600">
        <div className="inline-block w-7 h-7 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs font-semibold">Running AI Compatibility Engine & Generating Ranked Recommendations...</p>
      </div>
    );
  }

  const topMatch = recommendations[0]?.score || 0;
  const profileCompletion = Math.min(100, Math.round(((profile?.skills?.length || 0) * 15 + (profile?.degree ? 30 : 0) + (profile?.resume_url ? 25 : 0) + 30)));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Official Candidate Banner */}
      <div className="bg-white border border-slate-300 rounded-md p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded bg-emerald-50 border border-emerald-300 text-xs font-bold text-emerald-800">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
            <span>Eligible Candidate under PM Scheme Guidelines</span>
          </div>
          <h1 className="text-2xl font-bold text-[#002147]">
            Candidate Portal: {profile?.degree ? `${profile.degree} Candidate` : "Student Profile"}
          </h1>
          <p className="text-xs text-slate-600">
            {profile?.institution || "Ensure your profile and technical skills are complete for maximum precision AI matching."}
          </p>
        </div>

        <Link
          href="/profile"
          className="px-4 py-2 rounded bg-[#002147] hover:bg-[#001529] text-white font-bold text-xs shadow-sm transition-all shrink-0 flex items-center space-x-1.5"
        >
          <User className="w-4 h-4" />
          <span>Edit Profile & Resume</span>
        </Link>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-800 shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Highest AI Compatibility</p>
            <p className="text-xl font-bold text-emerald-800">{topMatch}%</p>
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-800 shrink-0">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Skill Readiness Index</p>
            <p className="text-xl font-bold text-blue-800">{skillGap?.readiness_score || 85}%</p>
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-800 shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Eligible Opportunities</p>
            <p className="text-xl font-bold text-slate-900">{recommendations.length}</p>
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-900 shrink-0">
            <User className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Profile Completion</p>
            <p className="text-xl font-bold text-amber-800">{profileCompletion}%</p>
          </div>
        </div>

      </div>

      {/* Top 3 AI Ranked Recommended Internships */}
      <div className="space-y-3">
        <div className="flex items-center justify-between border-b border-slate-300 pb-2">
          <div>
            <h2 className="text-lg font-bold text-[#002147] flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <span>Top AI Ranked Recommendations</span>
            </h2>
            <p className="text-xs text-slate-600">Scored dynamically based on skill intersection, academic background & semantic resume overlap</p>
          </div>

          <Link
            href="/recommendations"
            className="text-xs font-bold text-[#0056b3] hover:underline flex items-center space-x-1"
          >
            <span>View All ({recommendations.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {recommendations.slice(0, 3).map((rec, idx) => (
            <InternshipCard
              key={idx}
              internship={rec.internship}
              recommendation={rec}
            />
          ))}
        </div>
      </div>

      {/* Skill Gap Matrix Teaser */}
      {skillGap && (
        <div className="bg-white border border-slate-300 rounded p-5 space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-900 font-bold">
                <BookOpen className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-base font-bold text-[#002147]">Candidate Skill Gap Matrix</h3>
                <p className="text-xs text-slate-600">Target technical skills required by top opportunities</p>
              </div>
            </div>

            <Link
              href="/skill-gap"
              className="px-3 py-1 rounded text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition-colors"
            >
              Full Skill Matrix
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {skillGap.missing_required_skills.slice(0, 3).map((item: any, idx: number) => (
              <div key={idx} className="p-3 rounded bg-slate-50 border border-slate-200 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900">{item.skill}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-red-100 text-red-800 border border-red-200 font-bold">{item.priority} Priority</span>
                </div>
                <p className="text-[11px] text-slate-600 line-clamp-1">{item.recommendation_course}</p>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
