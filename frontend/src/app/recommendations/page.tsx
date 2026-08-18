"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import InternshipCard from "@/components/InternshipCard";
import { Sparkles, Search, ShieldCheck } from "lucide-react";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [filteredRecs, setFilteredRecs] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecommendations() {
      try {
        const data = await fetchApi("/students/recommendations");
        setRecommendations(data);
        setFilteredRecs(data);
      } catch (err) {
        console.error("Error loading recommendations:", err);
      } finally {
        setLoading(false);
      }
    }
    loadRecommendations();
  }, []);

  useEffect(() => {
    let result = [...recommendations];

    if (selectedCategory !== "All") {
      result = result.filter((item) => item.match_category === selectedCategory);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (item) =>
          item.internship.title.toLowerCase().includes(q) ||
          item.internship.company_name.toLowerCase().includes(q) ||
          item.internship.company_sector.toLowerCase().includes(q)
      );
    }

    setFilteredRecs(result);
  }, [selectedCategory, searchQuery, recommendations]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-600">
        <div className="inline-block w-7 h-7 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs font-semibold">Running AI Compatibility Engine & Generating Ranked Recommendations...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-300 pb-4">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-xs font-bold text-blue-900 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>Explainable AI Recommendation Engine</span>
          </div>
          <h1 className="text-2xl font-bold text-[#002147]">Ranked AI Internship Recommendations</h1>
          <p className="text-xs text-slate-600">Hard scheme eligibility rules enforced • Dynamically evaluated from 0 to 100%</p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by title or sector..."
            className="w-full bg-white border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:border-blue-700"
          />
        </div>
      </div>

      {/* Category Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 custom-scrollbar">
        {["All", "Excellent Match", "Strong Match", "Good Match", "Potential Match"].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded text-xs font-bold whitespace-nowrap transition-colors ${
              selectedCategory === cat
                ? "bg-[#002147] text-white"
                : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-300"
            }`}
          >
            {cat} {cat === "All" ? `(${recommendations.length})` : ""}
          </button>
        ))}
      </div>

      {/* Grid of Ranked Internships */}
      {filteredRecs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredRecs.map((rec, idx) => (
            <InternshipCard
              key={idx}
              internship={rec.internship}
              recommendation={rec}
            />
          ))}
        </div>
      ) : (
        <div className="p-8 text-center bg-white border border-slate-300 rounded">
          <p className="text-slate-600 text-xs font-medium">No opportunities match the selected category filter.</p>
        </div>
      )}

    </div>
  );
}
