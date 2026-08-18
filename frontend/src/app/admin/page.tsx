"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { ShieldCheck, BarChart3, Sliders, Plus, Trash2, Building, Users, FileText, CheckCircle2, RefreshCw } from "lucide-react";

export default function AdminDashboardPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [weights, setWeights] = useState<any>({
    skill_match_weight: 0.35,
    semantic_weight: 0.25,
    education_weight: 0.15,
    interest_weight: 0.10,
    location_weight: 0.05,
    experience_weight: 0.05,
    preference_weight: 0.05,
  });

  const [internships, setInternships] = useState<any[]>([]);
  const [ingestionSources, setIngestionSources] = useState<any[]>([]);
  const [triggeringIngestion, setTriggeringIngestion] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newOpp, setNewOpp] = useState({
    company_name: "",
    company_sector: "Public Sector",
    title: "",
    description: "",
    location: "Bengaluru",
    work_mode: "On-site",
    duration: "6 Months",
    stipend: "₹12,000 / month",
    deadline: "2026-10-30",
    min_qualification: "Graduate",
    preferred_degree: "B.Tech",
    required_skills: "Python, SQL",
    preferred_skills: "Machine Learning",
  });

  const [loading, setLoading] = useState(true);
  const [savingWeights, setSavingWeights] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadAdminData = async () => {
    try {
      const [anData, wData, oppData, sourcesData] = await Promise.all([
        fetchApi("/admin/analytics"),
        fetchApi("/admin/weights"),
        fetchApi("/internships"),
        fetchApi("/ingestion/sources").catch(() => []),
      ]);
      setAnalytics(anData);
      setWeights(wData);
      setInternships(oppData);
      setIngestionSources(sourcesData);
    } catch (err) {
      console.error("Admin load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleRunLiveIngestion = async (sourceId: number = 1) => {
    setTriggeringIngestion(true);
    setMessage(null);
    try {
      const res = await fetchApi(`/ingestion/trigger?source_id=${sourceId}`, {
        method: "POST",
      });
      setMessage(`Live Ingestion Stream Success: Processed ${res.processed_count} payload items. Added ${res.new_count} new opportunities, filtered ${res.duplicate_count} SHA-256 duplicate fingerprints.`);
      await loadAdminData();
    } catch (err: any) {
      setMessage(`Ingestion Stream Error: ${err.message || "Failed to run ingestion."}`);
    } finally {
      setTriggeringIngestion(false);
    }
  };

  const handleSaveWeights = async () => {
    setSavingWeights(true);
    setMessage(null);
    try {
      await fetchApi("/admin/weights", {
        method: "PUT",
        body: JSON.stringify(weights),
      });
      setMessage("Algorithm Weights updated! Recommendation engine recalibrated system-wide.");
    } catch (err: any) {
      setMessage(err.message || "Failed to update weights");
    } finally {
      setSavingWeights(false);
    }
  };

  const handleCreateInternship = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...newOpp,
        required_skills: newOpp.required_skills.split(",").map((s) => s.trim()).filter(Boolean),
        preferred_skills: newOpp.preferred_skills.split(",").map((s) => s.trim()).filter(Boolean),
      };
      await fetchApi("/admin/internships", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setShowAddModal(false);
      setMessage("New Internship opportunity published under PM Scheme!");
      // Reload internships
      const updated = await fetchApi("/internships");
      setInternships(updated);
    } catch (err: any) {
      setMessage(err.message || "Failed to create internship");
    }
  };

  const handleDeleteInternship = async (id: number) => {
    if (!confirm("Are you sure you want to delete this internship posting?")) return;
    try {
      await fetchApi(`/admin/internships/${id}`, { method: "DELETE" });
      setInternships(internships.filter((i) => i.id !== id));
      setMessage("Posting removed successfully");
    } catch (err: any) {
      setMessage(err.message);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-600">
        <div className="inline-block w-7 h-7 border-3 border-amber-600 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs font-semibold">Loading PM Scheme Administrator Dashboard & Analytics...</p>
      </div>
    );
  }

  const totalWeightSum = Object.values(weights).reduce((a: any, b: any) => a + b, 0) as number;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header Banner */}
      <div className="bg-white border border-slate-300 rounded p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-amber-50 border border-amber-200 text-xs font-bold text-amber-900 mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>NITI Aayog & Scheme Administration Portal</span>
          </div>
          <h1 className="text-2xl font-bold text-[#002147]">Platform Analytics & Algorithm Tuning</h1>
          <p className="text-xs text-slate-600">Monitor candidate demand, configure recommendation algorithm weights, and manage opportunity listings</p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 rounded bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-sm transition-all flex items-center space-x-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>Post New Opportunity</span>
        </button>
      </div>

      {message && (
        <div className="p-3 rounded bg-emerald-50 border border-emerald-300 text-xs text-emerald-900 font-bold flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Analytics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-800 shrink-0">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Registered Candidates</p>
            <p className="text-xl font-black text-slate-900">{analytics?.total_students || 0}</p>
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-800 shrink-0">
            <Building className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Active Scheme Listings</p>
            <p className="text-xl font-black text-slate-900">{analytics?.total_internships || 0}</p>
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-800 shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Submitted Applications</p>
            <p className="text-xl font-black text-slate-900">{analytics?.total_applications || 0}</p>
          </div>
        </div>

        <div className="p-4 rounded bg-white border border-slate-300 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-900 shrink-0">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-500">Avg AI Match Accuracy</p>
            <p className="text-xl font-black text-amber-800">{analytics?.avg_recommendation_score || 82.5}%</p>
          </div>
        </div>

      </div>

      {/* Live Ingestion Stream Control Section */}
      <div className="p-5 rounded-xl bg-white border border-slate-300 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center space-x-2">
            <RefreshCw className="w-5 h-5 text-blue-700" />
            <div>
              <h2 className="text-base font-bold text-[#002147]">Live Ingestion Stream Manager</h2>
              <p className="text-xs text-slate-500">Real-time source registries, SHA-256 deduplication, and vector embedding pipelines</p>
            </div>
          </div>
          <button
            onClick={() => handleRunLiveIngestion(1)}
            disabled={triggeringIngestion}
            className="px-4 py-2 rounded bg-blue-900 hover:bg-blue-800 text-white font-bold text-xs shadow-sm transition-all flex items-center space-x-1.5"
          >
            {triggeringIngestion ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
                <span>Running Ingestion Stream...</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Run Ingestion Stream Now</span>
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          {ingestionSources.map((src: any, idx: number) => (
            <div key={idx} className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#002147]">{src.source_name}</span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[9px]">ACTIVE</span>
              </div>
              <p className="text-[11px] text-slate-600 font-mono truncate">{src.source_url}</p>
              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-200">
                <span>Type: {src.source_type}</span>
                <span>Rate Limit: {src.rate_limit_rpm} RPM</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dynamic AI Recommendation Weight Tuning Section */}
      <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-900 font-bold">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#002147]">Dynamic AI Algorithm Weight Controls</h2>
              <p className="text-xs text-slate-600">Adjust algorithm weights in real time to re-rank candidate recommendations system-wide</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <span className="font-semibold text-slate-600">
              Total Weight Sum: <strong className={Math.abs(totalWeightSum - 1.0) < 0.05 ? "text-emerald-700" : "text-amber-700"}>{(totalWeightSum * 100).toFixed(0)}%</strong>
            </span>
            <button
              onClick={handleSaveWeights}
              disabled={savingWeights}
              className="px-3.5 py-1.5 bg-[#002147] hover:bg-[#001529] text-white font-bold rounded shadow-sm transition-colors flex items-center space-x-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>{savingWeights ? "Updating..." : "Recalibrate Engine"}</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          
          <div className="space-y-1.5 p-3 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Skill Match Weight</span>
              <span className="font-bold text-blue-800">{Math.round(weights.skill_match_weight * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.8"
              step="0.05"
              value={weights.skill_match_weight}
              onChange={(e) => setWeights({ ...weights, skill_match_weight: parseFloat(e.target.value) })}
              className="w-full accent-[#002147]"
            />
          </div>

          <div className="space-y-1.5 p-3 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Semantic Overlap Weight</span>
              <span className="font-bold text-purple-800">{Math.round(weights.semantic_weight * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.8"
              step="0.05"
              value={weights.semantic_weight}
              onChange={(e) => setWeights({ ...weights, semantic_weight: parseFloat(e.target.value) })}
              className="w-full accent-purple-700"
            />
          </div>

          <div className="space-y-1.5 p-3 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Education Match Weight</span>
              <span className="font-bold text-emerald-800">{Math.round(weights.education_weight * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.5"
              step="0.05"
              value={weights.education_weight}
              onChange={(e) => setWeights({ ...weights, education_weight: parseFloat(e.target.value) })}
              className="w-full accent-emerald-700"
            />
          </div>

          <div className="space-y-1.5 p-3 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Career Interest Weight</span>
              <span className="font-bold text-amber-800">{Math.round(weights.interest_weight * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.4"
              step="0.05"
              value={weights.interest_weight}
              onChange={(e) => setWeights({ ...weights, interest_weight: parseFloat(e.target.value) })}
              className="w-full accent-amber-700"
            />
          </div>

          <div className="space-y-1.5 p-3 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Location Match Weight</span>
              <span className="font-bold text-slate-800">{Math.round(weights.location_weight * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.3"
              step="0.05"
              value={weights.location_weight}
              onChange={(e) => setWeights({ ...weights, location_weight: parseFloat(e.target.value) })}
              className="w-full accent-slate-700"
            />
          </div>

          <div className="space-y-1.5 p-3 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Experience Relevance Weight</span>
              <span className="font-bold text-slate-800">{Math.round(weights.experience_weight * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.3"
              step="0.05"
              value={weights.experience_weight}
              onChange={(e) => setWeights({ ...weights, experience_weight: parseFloat(e.target.value) })}
              className="w-full accent-slate-700"
            />
          </div>

        </div>
      </div>

      {/* Internship Postings Table */}
      <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-3">
        <h2 className="text-base font-bold text-[#002147]">Manage Scheme Internship Opportunities</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-800">
            <thead className="bg-slate-100 text-slate-700 uppercase font-bold border-b border-slate-300">
              <tr>
                <th className="p-2.5">Title & Organization</th>
                <th className="p-2.5">Sector</th>
                <th className="p-2.5">Location</th>
                <th className="p-2.5">Stipend</th>
                <th className="p-2.5">Positions</th>
                <th className="p-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {internships.map((opp) => (
                <tr key={opp.id} className="hover:bg-slate-50">
                  <td className="p-2.5">
                    <p className="font-bold text-[#002147]">{opp.title}</p>
                    <p className="text-slate-500 text-[11px]">{opp.company_name}</p>
                  </td>
                  <td className="p-2.5">{opp.company_sector}</td>
                  <td className="p-2.5">{opp.location}</td>
                  <td className="p-2.5 font-bold text-emerald-800">{opp.stipend}</td>
                  <td className="p-2.5">{opp.positions}</td>
                  <td className="p-2.5 text-right">
                    <button
                      onClick={() => handleDeleteInternship(opp.id)}
                      className="p-1.5 rounded bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 transition-colors"
                      title="Delete Posting"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add New Opportunity Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-xl bg-white border border-slate-300 rounded p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
            <h3 className="text-lg font-bold text-[#002147] border-b border-slate-200 pb-2">Post New Scheme Opportunity</h3>
            
            <form onSubmit={handleCreateInternship} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Company / Organization Name</label>
                <input
                  type="text"
                  required
                  value={newOpp.company_name}
                  onChange={(e) => setNewOpp({ ...newOpp, company_name: e.target.value })}
                  placeholder="e.g. ISRO / BHEL / Infosys"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Sector Category</label>
                <input
                  type="text"
                  required
                  value={newOpp.company_sector}
                  onChange={(e) => setNewOpp({ ...newOpp, company_sector: e.target.value })}
                  placeholder="e.g. Public Sector / Aerospace"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Internship Title</label>
                <input
                  type="text"
                  required
                  value={newOpp.title}
                  onChange={(e) => setNewOpp({ ...newOpp, title: e.target.value })}
                  placeholder="e.g. AI & Data Analytics Intern"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  required
                  rows={3}
                  value={newOpp.description}
                  onChange={(e) => setNewOpp({ ...newOpp, description: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Required Skills (Comma-separated)</label>
                  <input
                    type="text"
                    value={newOpp.required_skills}
                    onChange={(e) => setNewOpp({ ...newOpp, required_skills: e.target.value })}
                    className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Preferred Skills (Comma-separated)</label>
                  <input
                    type="text"
                    value={newOpp.preferred_skills}
                    onChange={(e) => setNewOpp({ ...newOpp, preferred_skills: e.target.value })}
                    className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-[#002147] hover:bg-[#001529] text-white font-bold rounded"
                >
                  Publish Listing
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
