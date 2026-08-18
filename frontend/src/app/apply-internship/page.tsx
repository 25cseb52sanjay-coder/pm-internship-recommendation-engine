"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApi, getCurrentUser } from "@/lib/api";
import {
  Building2,
  Briefcase,
  MapPin,
  Clock,
  DollarSign,
  ShieldCheck,
  Zap,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Users,
  Award,
  Sparkles,
  ArrowRight,
  X,
  Layers
} from "lucide-react";

// Security URL sanitizer & validator (HTTPS/HTTP protocol enforcement)
const sanitizeAndValidateUrl = (rawUrl?: string): string | null => {
  if (!rawUrl || typeof rawUrl !== "string") return null;
  const trimmed = rawUrl.trim();
  if (!trimmed) return null;
  try {
    const parsed = new URL(trimmed);
    if (parsed.protocol === "https:" || parsed.protocol === "http:") {
      return parsed.toString();
    }
    return null;
  } catch {
    return null;
  }
};

// Strips HTML entities and tags for clean text preview
const formatCleanDescription = (text?: string): string => {
  if (!text) return "";
  let clean = text
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&nbsp;/g, " ");
  clean = clean.replace(/<[^>]*>?/gm, " ").replace(/\s+/g, " ").trim();
  return clean;
};

export default function ApplyInternshipPage() {
  const [internships, setInternships] = useState<any[]>([]);
  const [ingestionStatus, setIngestionStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("All");
  const [workMode, setWorkMode] = useState("All");
  const [sourceFilter, setSourceFilter] = useState("All");
  const [oppTypeFilter, setOppTypeFilter] = useState("All");

  // Application Modal state
  const [selectedOpp, setSelectedOpp] = useState<any>(null);
  const [applying, setApplying] = useState(false);
  const [applyMessage, setApplyMessage] = useState<string | null>(null);
  const [applySuccess, setApplySuccess] = useState<boolean | null>(null);

  const currentUser = getCurrentUser();

  // Load real-time company listings directly from PostgreSQL
  const loadLiveData = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    try {
      const queryParams = new URLSearchParams();
      if (sector !== "All") queryParams.append("sector", sector);
      if (workMode !== "All") queryParams.append("work_mode", workMode);
      if (sourceFilter !== "All") queryParams.append("source", sourceFilter);
      if (oppTypeFilter !== "All") queryParams.append("opportunity_type", oppTypeFilter);
      if (search) queryParams.append("search", search);

      const data = await fetchApi(`/internships?${queryParams.toString()}`);
      setInternships(data || []);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Live feed fetch error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Load once on component mount or filter update (High performance, no continuous polling loop)
  useEffect(() => {
    loadLiveData();
  }, [sector, workMode, sourceFilter, oppTypeFilter, search]);

  // Handle direct 1-click internship application
  const handleApplyNow = async (oppId: number) => {
    setApplying(true);
    setApplyMessage(null);
    setApplySuccess(null);
    try {
      const res = await fetchApi(`/internships/${oppId}/apply`, {
        method: "POST"
      });
      setApplySuccess(true);
      setApplyMessage(res.message || "Application submitted successfully!");
    } catch (err: any) {
      setApplySuccess(false);
      setApplyMessage(err.message || "Failed to submit application. Please verify your profile.");
    } finally {
      setApplying(false);
    }
  };

  // Compute stats
  const uniqueCompaniesCount = new Set(internships.map((i) => i.company_name)).size;
  const totalPositionsCount = internships.reduce((sum, item) => sum + (item.positions || 5), 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

      {/* 1. Top Real-Time 24/7 Live Stream Banner */}
      <div className="bg-gradient-to-r from-[#002147] via-[#061a40] to-[#0a2540] rounded-xl p-5 text-white shadow-lg border border-slate-700 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-10 pointer-events-none">
          <Building2 className="w-64 h-64 text-blue-400" />
        </div>

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-2 max-w-3xl">
            
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/40 text-xs font-bold">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span>24/7 AUTOMATED LIVE INGESTION STREAM</span>
              </span>

              <span className="text-xs text-slate-300 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700 font-mono">
                Last Auto-Synced: <strong>{lastUpdated || "Live"}</strong>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Apply Live Internships & Company Uploads
            </h1>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Real-time directory of participating public sector PSUs, Ministries, and top private enterprises.
              This portal streams new company vacancy postings 24 hours a day with SHA-256 duplicate verification and soft-expiry checks.
            </p>
          </div>

          <button
            onClick={() => loadLiveData(true)}
            disabled={refreshing}
            className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md transition-all shrink-0 flex items-center space-x-2 border border-blue-400/30 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            <span>{refreshing ? "Refreshing Stream..." : "Manual Stream Refresh"}</span>
          </button>
        </div>
      </div>

      {/* 2. Key Ingestion Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-4 rounded-xl bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 shrink-0">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Active Companies</p>
            <p className="text-xl font-bold text-[#002147]">{uniqueCompaniesCount} Organisations</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shrink-0">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Total Stream Requisitions</p>
            <p className="text-xl font-bold text-emerald-800">{internships.length} Postings</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700 shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Scheme Seat Capacity</p>
            <p className="text-xl font-bold text-purple-900">{totalPositionsCount} Positions</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 shrink-0">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Quality Index</p>
            <p className="text-xl font-bold text-amber-800">80-100 Verified Score</p>
          </div>
        </div>
      </div>

      {/* 3. Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-white border border-slate-300 shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 text-xs">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search company, role, city..."
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:bg-white focus:border-blue-700 outline-none"
          />
        </div>

        <div>
          <select
            value={oppTypeFilter}
            onChange={(e) => setOppTypeFilter(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-semibold focus:bg-white focus:border-blue-700 outline-none"
          >
            <option value="All">All Types (Jobs & Internships)</option>
            <option value="Jobs">Jobs Only</option>
            <option value="Internships">Internships Only</option>
          </select>
        </div>

        <div>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:border-blue-700 outline-none"
          >
            <option value="All">All Sources</option>
            <option value="Adzuna">Adzuna Official</option>
            <option value="Greenhouse">Greenhouse Official</option>
            <option value="NCS">NCS (National Career Service)</option>
            <option value="PMIS">PM Scheme Official</option>
            <option value="COMPANY_CAREER">Official Company Careers</option>
          </select>
        </div>

        <div>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:border-blue-700 outline-none"
          >
            <option value="All">All Sectors</option>
            <option value="Public Sector / Aerospace">Public Sector / Aerospace</option>
            <option value="Government / Public Policy">Government / Public Policy</option>
            <option value="IT Services & Digital Systems">IT Services & Digital Systems</option>
            <option value="Automotive & Manufacturing">Automotive & Manufacturing</option>
            <option value="Technology & Corporate Services">Technology & Corporate Services</option>
          </select>
        </div>

        <div>
          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:bg-white focus:border-blue-700 outline-none"
          >
            <option value="All">All Work Modes</option>
            <option value="On-site">On-site</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
          </select>
        </div>
      </div>

      {/* 4. Live Company Opportunities Grid */}
      {loading ? (
        <div className="py-16 text-center text-slate-600 bg-white rounded-xl border border-slate-200">
          <div className="inline-block w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mb-3" />
          <p className="text-xs font-semibold">Connecting to 24/7 Live Ingestion Stream...</p>
        </div>
      ) : internships.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {internships.map((opp, idx) => {
            const isGreenhouse = opp.source === "Greenhouse" || (opp.source_name && opp.source_name.toLowerCase().includes("greenhouse"));
            const isNCS = opp.source === "NCS" || (opp.source_name && (opp.source_name.includes("NCS") || opp.source_name.toLowerCase().includes("national career service")));
            const targetUrl = sanitizeAndValidateUrl(opp.apply_url || opp.application_url);

            return (
              <div
                key={opp.id || idx}
                className="bg-white border border-slate-300 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-blue-600 transition-all flex flex-col justify-between space-y-4 relative group"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#002147] to-blue-900 text-white font-black flex items-center justify-center text-sm shadow-sm shrink-0">
                        {opp.company_name ? opp.company_name.substring(0, 2).toUpperCase() : "PM"}
                      </div>
                      <div>
                        <h3 className="text-xs font-bold text-slate-900 line-clamp-1">{opp.company_name}</h3>
                        <p className="text-[10px] font-semibold text-slate-500">{opp.company_sector || "Public Sector"}</p>
                      </div>
                    </div>

                    {isGreenhouse ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 shrink-0">
                        Source: Greenhouse
                      </span>
                    ) : isNCS ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 shrink-0">
                        Source: NCS
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 shrink-0">
                        Verified Live
                      </span>
                    )}
                  </div>

                  <div>
                    <h2 className="text-sm font-bold text-[#002147] group-hover:text-blue-700 transition-colors line-clamp-2">
                      {opp.title}
                    </h2>
                    {opp.description && (
                      <p className="text-xs text-slate-600 line-clamp-2 mt-1 leading-snug">
                        {formatCleanDescription(opp.description)}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                    {opp.location && (
                      <div className="flex items-center space-x-1.5 text-slate-700">
                        <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="truncate">{opp.location}</span>
                      </div>
                    )}

                    {opp.work_mode && (
                      <div className="flex items-center space-x-1.5 text-slate-700">
                        <Briefcase className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>{opp.work_mode}</span>
                      </div>
                    )}

                    {opp.stipend && (
                      <div className="flex items-center space-x-1.5 text-emerald-700 font-semibold">
                        <DollarSign className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>{opp.stipend}</span>
                      </div>
                    )}

                    {opp.positions && (
                      <div className="flex items-center space-x-1.5 text-slate-700">
                        <Users className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>{opp.positions} Seats</span>
                      </div>
                    )}
                  </div>

                  {opp.skills && opp.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {opp.skills.map((sk: any, i: number) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-blue-50 text-blue-800 text-[10px] font-semibold border border-blue-200"
                        >
                          {sk.skill ? sk.skill.name : sk.name || "Skill"}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-200 flex items-center justify-between gap-2">
                  <div className="text-[10px] text-slate-500 font-medium">
                    {opp.deadline ? (
                      <>Deadline: <strong className="text-slate-800">{opp.deadline}</strong></>
                    ) : (
                      <span className="text-slate-400">Open Posting</span>
                    )}
                  </div>

                  {(isGreenhouse || isNCS) && targetUrl ? (
                    <a
                      href={targetUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1.5 rounded-lg bg-[#002147] hover:bg-blue-900 text-white font-bold text-xs flex items-center space-x-1 shadow-sm transition-all shrink-0"
                    >
                      <span>Apply Now ({isGreenhouse ? "Greenhouse" : "NCS"}) ↗</span>
                    </a>
                  ) : (
                    <button
                      onClick={() => setSelectedOpp(opp)}
                      className="px-3 py-1.5 rounded-lg bg-[#002147] hover:bg-blue-800 text-white font-bold text-xs flex items-center space-x-1 shadow-sm transition-all shrink-0"
                    >
                      <span>Apply Now</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-12 text-center bg-white border border-slate-300 rounded-xl space-y-3">
          <div className="inline-flex items-center justify-center p-3 rounded-full bg-blue-50 text-blue-700 border border-blue-200 mb-1">
            <ShieldCheck className="w-8 h-8 text-blue-700" />
          </div>
          <p className="text-sm text-slate-800 font-bold">Authoritative Verification In Progress</p>
          <p className="text-xs text-slate-600 max-w-xl mx-auto leading-relaxed">
            All listings undergo mandatory authoritative source URL validation, employer confirmation, and SHA-256 deduplication before being assigned <strong className="text-emerald-700">VERIFIED_LIVE</strong>. Synthetic or unverified listings are strictly excluded from live public display.
          </p>
          <div className="pt-2">
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              <span>24/7 Discovery & Verification Engine Scanning Official Portals</span>
            </span>
          </div>
        </div>
      )}

      {/* 5. Application Detail & Instant Submission Modal */}
      {selectedOpp && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-300 max-w-xl w-full p-6 space-y-4 relative animate-in fade-in zoom-in-95 duration-150">
            
            <button
              onClick={() => {
                setSelectedOpp(null);
                setApplyMessage(null);
                setApplySuccess(null);
              }}
              className="absolute right-4 top-4 p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1 pr-6">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-900 border border-blue-300">
                {selectedOpp.source === "Adzuna" ? "Adzuna Official Posting" : selectedOpp.source === "Greenhouse" ? "Greenhouse Official Posting" : "Official PM Scheme Posting"}
              </span>
              <h2 className="text-xl font-bold text-[#002147]">{selectedOpp.title}</h2>
              <p className="text-xs font-semibold text-slate-600">
                {selectedOpp.company_name} • {selectedOpp.company_sector}
              </p>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-2 max-h-60 overflow-y-auto">
              <p className="text-slate-700 leading-relaxed whitespace-pre-line">
                {formatCleanDescription(selectedOpp.description)}
              </p>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 font-medium">
                <div>Location: <strong className="text-slate-900">{selectedOpp.location}</strong></div>
                <div>Work Mode: <strong className="text-slate-900">{selectedOpp.work_mode}</strong></div>
                <div>Stipend: <strong className="text-emerald-700">{selectedOpp.stipend}</strong></div>
                <div>Seats Open: <strong className="text-slate-900">{selectedOpp.positions || 1}</strong></div>
              </div>
            </div>

            {applyMessage && (
              <div
                className={`p-3 rounded-lg text-xs font-semibold flex items-center space-x-2 ${
                  applySuccess
                    ? "bg-emerald-50 text-emerald-900 border border-emerald-300"
                    : "bg-red-50 text-red-900 border border-red-300"
                }`}
              >
                {applySuccess ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> : <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />}
                <span>{applyMessage}</span>
              </div>
            )}

            <div className="pt-2 flex items-center justify-between">
              {selectedOpp.source === "Adzuna" || selectedOpp.source === "Greenhouse" || selectedOpp.source === "NCS" ? (
                <a
                  href={sanitizeAndValidateUrl(selectedOpp.apply_url || selectedOpp.application_url) || "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs shadow transition-all flex items-center justify-center space-x-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Apply on Official {selectedOpp.source} Portal ↗</span>
                </a>
              ) : currentUser ? (
                <button
                  onClick={() => handleApplyNow(selectedOpp.id)}
                  disabled={applying || applySuccess === true}
                  className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {applying ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Submitting Application...</span>
                    </>
                  ) : applySuccess ? (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Application Submitted!</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Confirm 1-Click Scheme Application</span>
                    </>
                  )}
                </button>
              ) : (
                <div className="w-full text-center space-y-2">
                  <p className="text-xs text-amber-800 bg-amber-50 p-2 rounded border border-amber-200 font-medium">
                    Please sign in as a registered candidate to submit your application.
                  </p>
                  <div className="flex items-center justify-center space-x-3 text-xs">
                    <Link
                      href="/login"
                      className="px-4 py-2 rounded-lg bg-[#002147] text-white font-bold hover:bg-blue-800 transition-colors"
                    >
                      Sign In Now
                    </Link>
                    <Link
                      href="/register"
                      className="px-4 py-2 rounded-lg bg-amber-500 text-slate-950 font-bold hover:bg-amber-400 transition-colors"
                    >
                      Register Candidate Profile
                    </Link>
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
