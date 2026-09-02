"use client";

import { useState } from "react";
import { Building, MapPin, Clock, DollarSign, Sparkles, Bookmark, CheckCircle, Info } from "lucide-react";
import ExplainabilityModal from "./ExplainabilityModal";
import { fetchApi } from "@/lib/api";

interface InternshipCardProps {
  internship: {
    id: number;
    company_name: string;
    company_sector: string;
    title: string;
    description: string;
    location?: string;
    work_mode?: string;
    duration?: string;
    stipend?: string;
    deadline?: string;
    positions?: number;
    source?: string;
    source_name?: string;
    opportunity_type?: string;
    apply_url?: string;
    application_url?: string;
    external_id?: string;
    skills?: { skill: { name: string }; is_required: boolean }[];
  };
  recommendation?: {
    score: number;
    match_category: string;
    explanation: any;
  };
  onActionSuccess?: () => void;
}

export default function InternshipCard({ internship, recommendation, onActionSuccess }: InternshipCardProps) {
  const [showModal, setShowModal] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const score = recommendation?.score || 0;
  const matchCategory = recommendation?.match_category || "Potential Match";

  // Source Detection & Redirection Target URL
  const isNCS = internship.source === "NCS" || 
                (internship.source_name && (internship.source_name.includes("NCS") || internship.source_name.toLowerCase().includes("national career service")));
  
  const isGreenhouse = internship.source === "Greenhouse" ||
                      (internship.source_name && internship.source_name.toLowerCase().includes("greenhouse"));

  const isAdzuna = internship.source === "Adzuna" ||
                   (internship.source_name && internship.source_name.toLowerCase().includes("adzuna"));

  const isLever = internship.source === "Lever" ||
                  (internship.source_name && internship.source_name.toLowerCase().includes("lever"));

  const isJobvetta = internship.source === "Jobvetta" ||
                     (internship.source_name && internship.source_name.toLowerCase().includes("jobvetta"));

  const rawApplyUrl = internship.apply_url || internship.application_url;

  const getScoreBadgeClass = (sc: number) => {
    if (sc >= 85) return "bg-emerald-100 text-emerald-800 border-emerald-300 font-bold";
    if (sc >= 70) return "bg-blue-100 text-blue-800 border-blue-300 font-bold";
    if (sc >= 55) return "bg-amber-100 text-amber-800 border-amber-300 font-bold";
    return "bg-slate-100 text-slate-700 border-slate-300 font-semibold";
  };

  const sanitizeAndValidateUrl = (rawUrl?: string): string | null => {
    if (!rawUrl || typeof rawUrl !== "string") return null;
    const trimmed = rawUrl.trim();
    if (!trimmed || trimmed === "APPLICATION_URL_UNAVAILABLE") return null;
    
    try {
      const parsed = new URL(trimmed);
      if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;

      const host = parsed.hostname.toLowerCase();
      const path = parsed.pathname.replace(/\/$/, "");

      // Generic provider or company root rejection
      if ((host.includes("boards.greenhouse.io") || host.includes("greenhouse.io")) && (!path || path === "")) return null;
      if ((host.includes("jobs.lever.co") || host.includes("lever.co")) && (!path || path === "")) return null;
      if (host.includes("adzuna") && (!path || path === "" || path === "/search" || path === "/jobs")) return null;
      if (host.includes("pminternship.mca.gov.in") && (!path || path === "")) return null;
      if (host.includes("ncs.gov.in") && (!path || path === "" || path === "/internships-jobs")) return null;

      return parsed.toString();
    } catch {
      return null;
    }
  };

  const safeUrl = sanitizeAndValidateUrl(rawApplyUrl);

  // Adzuna-Specific Target URL Resolution (Strictly Isolated — Greenhouse, Lever & NCS Untouched)
  let adzunaTargetUrl: string | null = null;
  if (isAdzuna) {
    if (rawApplyUrl && rawApplyUrl !== "APPLICATION_URL_UNAVAILABLE") {
      adzunaTargetUrl = sanitizeAndValidateUrl(rawApplyUrl);
    }
    if (!adzunaTargetUrl) {
      const fallbackId = internship.external_id || internship.id;
      if (fallbackId) {
        adzunaTargetUrl = `https://www.adzuna.in/details/${fallbackId}`;
      }
    }
  }

  // Effective destination URL: Adzuna uses isolated resolution; Greenhouse/Lever/NCS/PMIS use original safeUrl
  const effectiveApplyUrl = isAdzuna ? adzunaTargetUrl : safeUrl;

  const handleSave = async () => {
    setLoading(true);
    try {
      await fetchApi(`/internships/${internship.id}/save`, { method: "POST" });
      setIsSaved(true);
      setMessage("Saved to profile!");
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (effectiveApplyUrl) {
      window.open(effectiveApplyUrl, "_blank", "noopener,noreferrer");
      setIsApplied(true);
      setMessage(`Redirecting to official application page...`);
      return;
    }

    if (rawApplyUrl === "APPLICATION_URL_UNAVAILABLE" && !isAdzuna) {
      setMessage("Application link is currently unavailable for this listing.");
      return;
    }

    setLoading(true);
    try {
      await fetchApi(`/internships/${internship.id}/apply`, { method: "POST" });
      setIsApplied(true);
      setMessage("Application submitted successfully!");
      if (onActionSuccess) onActionSuccess();
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="bg-white border border-slate-300 rounded-md p-5 shadow-sm hover:border-slate-400 transition-all flex flex-col justify-between relative">
        
        <div>
          {/* Top Row: Sector Badge + Source Label + Opportunity Type Badge + Match Score Badge */}
          <div className="flex items-center justify-between gap-2 mb-3">
            <div className="flex items-center space-x-1.5 flex-wrap gap-1">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-300">
                {internship.company_sector || "Public Sector"}
              </span>

              {/* Source Label Badge */}
              {isJobvetta ? (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-indigo-100 text-indigo-900 border border-indigo-300">
                  Source: Jobvetta
                </span>
              ) : isAdzuna ? (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-teal-100 text-teal-900 border border-teal-300">
                  Source: Adzuna
                </span>
              ) : isGreenhouse ? (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                  Source: Greenhouse
                </span>
              ) : isLever ? (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-purple-100 text-purple-900 border border-purple-300">
                  Source: Lever
                </span>
              ) : isNCS ? (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                  Source: NCS
                </span>
              ) : (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-800 border border-blue-200">
                  {internship.source_name || "PM Scheme"}
                </span>
              )}

              {/* Opportunity Type Badge */}
              {internship.opportunity_type && internship.opportunity_type !== "UNKNOWN" && (
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  internship.opportunity_type === "JOB"
                    ? "bg-purple-100 text-purple-900 border-purple-300"
                    : "bg-blue-100 text-blue-900 border-blue-300"
                }`}>
                  {internship.opportunity_type}
                </span>
              )}
            </div>

            {recommendation && (
              <div className={`px-2.5 py-0.5 rounded text-xs border flex items-center space-x-1 ${getScoreBadgeClass(score)}`}>
                <Sparkles className="w-3 h-3" />
                <span>{score}% AI Match</span>
              </div>
            )}
          </div>

          {/* Title & Company */}
          <h3 className="text-base font-bold text-[#002147] hover:text-blue-700 transition-colors leading-snug">
            {internship.title}
          </h3>
          <p className="text-xs font-semibold text-slate-600 flex items-center mt-1">
            <Building className="w-3.5 h-3.5 mr-1 text-slate-500 shrink-0" />
            <span>{internship.company_name}</span>
          </p>

          {/* Metadata Chips (Display only non-empty fields) */}
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 my-3.5 bg-slate-50 p-2.5 rounded border border-slate-200">
            {internship.location && (
              <div className="flex items-center">
                <MapPin className="w-3.5 h-3.5 mr-1.5 text-slate-500 shrink-0" />
                <span className="truncate">{internship.location} {internship.work_mode ? `(${internship.work_mode})` : ""}</span>
              </div>
            )}

            {internship.stipend && (
              <div className="flex items-center">
                <DollarSign className="w-3.5 h-3.5 mr-1.5 text-emerald-700 shrink-0" />
                <span className="font-semibold text-emerald-800 truncate">{internship.stipend}</span>
              </div>
            )}

            {internship.duration && (
              <div className="flex items-center">
                <Clock className="w-3.5 h-3.5 mr-1.5 text-slate-500 shrink-0" />
                <span>{internship.duration}</span>
              </div>
            )}

            {internship.deadline && (
              <div className="flex items-center">
                <Info className="w-3.5 h-3.5 mr-1.5 text-slate-500 shrink-0" />
                <span>Deadline: {internship.deadline}</span>
              </div>
            )}
          </div>

          {/* Description snippet (Only display if non-empty) */}
          {internship.description && (
            <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-3">
              {internship.description}
            </p>
          )}

          {/* Skill tags */}
          {internship.skills && internship.skills.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-4">
              {internship.skills.slice(0, 4).map((item: any, idx: number) => {
                const skillName = typeof item === "string"
                  ? item
                  : (item?.skill?.name || item?.name || item?.skill_name || "Skill");
                const isRequired = typeof item === "object" && Boolean(item?.is_required || item?.isRequired);
                return (
                  <span
                    key={idx}
                    className={`px-2 py-0.5 rounded text-[11px] font-medium border ${
                      isRequired
                        ? "bg-blue-50 text-blue-800 border-blue-200"
                        : "bg-slate-100 text-slate-600 border-slate-200"
                    }`}
                  >
                    {skillName} {isRequired && "*"}
                  </span>
                );
              })}
            </div>
          )}
        </div>

        {/* Action Row */}
        <div className="pt-3 border-t border-slate-200 flex items-center justify-between">
          {recommendation ? (
            <button
              onClick={() => setShowModal(true)}
              className="text-xs font-semibold text-[#0056b3] hover:underline flex items-center space-x-1"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              <span>Why Recommended?</span>
            </button>
          ) : (
            <span className="text-[11px] font-medium text-slate-500">
              {isGreenhouse ? "Greenhouse Partner Posting" : isNCS ? "National Career Service Listing" : "Verified PM Scheme Posting"}
            </span>
          )}

          <div className="flex items-center space-x-2">
            <button
              onClick={handleSave}
              disabled={loading || isSaved}
              className={`p-1.5 rounded text-xs font-medium border transition-colors ${
                isSaved
                  ? "bg-amber-100 text-amber-800 border-amber-300"
                  : "bg-white hover:bg-slate-100 text-slate-700 border-slate-300"
              }`}
              title="Save Opportunity"
            >
              <Bookmark className="w-4 h-4" />
            </button>

            <button
              onClick={handleApply}
              disabled={loading || (!effectiveApplyUrl && rawApplyUrl === "APPLICATION_URL_UNAVAILABLE" && !isAdzuna)}
              className={`px-3.5 py-1.5 rounded text-xs font-bold transition-all ${
                !effectiveApplyUrl && rawApplyUrl === "APPLICATION_URL_UNAVAILABLE" && !isAdzuna
                  ? "bg-slate-200 text-slate-500 cursor-not-allowed border border-slate-300"
                  : isApplied
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-[#002147] hover:bg-[#001529] text-white shadow-sm flex items-center space-x-1"
              }`}
            >
              {isApplied ? (
                <span className="flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-700" />
                  <span>Applied</span>
                </span>
              ) : !effectiveApplyUrl && rawApplyUrl === "APPLICATION_URL_UNAVAILABLE" && !isAdzuna ? (
                <span>Link Unavailable</span>
              ) : (
                <span>Apply Now ↗</span>
              )}
            </button>
          </div>
        </div>

        {message && (
          <p className="text-[11px] text-emerald-700 font-semibold mt-2 text-right">{message}</p>
        )}
      </div>

      {/* Modal */}
      {recommendation && (
        <ExplainabilityModal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          internshipTitle={internship.title}
          companyName={internship.company_name}
          score={score}
          matchCategory={matchCategory}
          explanation={recommendation.explanation}
        />
      )}
    </>
  );
}
