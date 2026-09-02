"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import InternshipCard from "@/components/InternshipCard";
import { Compass, Search, Filter } from "lucide-react";

export default function InternshipCatalogPage() {
  const [internships, setInternships] = useState<any[]>([]);
  const [sector, setSector] = useState("All");
  const [workMode, setWorkMode] = useState("All");
  const [sourceFilter, setSourceFilter] = useState("All");
  const [oppTypeFilter, setOppTypeFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInternships() {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        if (sector !== "All") queryParams.append("sector", sector);
        if (workMode !== "All") queryParams.append("work_mode", workMode);
        if (sourceFilter !== "All") queryParams.append("source", sourceFilter);
        if (oppTypeFilter !== "All") queryParams.append("opportunity_type", oppTypeFilter);
        if (search) queryParams.append("search", search);

        const data = await fetchApi(`/internships?${queryParams.toString()}`);
        setInternships(data);
      } catch (err) {
        console.error("Error fetching internships:", err);
      } finally {
        setLoading(false);
      }
    }
    loadInternships();
  }, [sector, workMode, sourceFilter, oppTypeFilter, search]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="border-b border-slate-300 pb-4 space-y-1">
        <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-xs font-bold text-blue-900">
          <Compass className="w-3.5 h-3.5" />
          <span>PM Scheme Verified Opportunities Catalog</span>
        </div>
        <h1 className="text-2xl font-bold text-[#002147]">Explore Scheme Postings</h1>
        <p className="text-xs text-slate-600">Browse verified 12-month internship opportunities posted by participating public & private sector partners</p>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded bg-white border border-slate-300 shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 text-xs">
        
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search title, company..."
            className="w-full bg-white border border-slate-300 rounded pl-9 pr-3 py-1.5 text-slate-900 focus:border-blue-700"
          />
        </div>

        {/* Opportunity Type Filter */}
        <div>
          <select
            value={oppTypeFilter}
            onChange={(e) => setOppTypeFilter(e.target.value)}
            className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 font-semibold focus:border-blue-700"
          >
            <option value="All">All Types (Jobs & Internships)</option>
            <option value="Jobs">Jobs Only</option>
            <option value="Internships">Internships Only</option>
          </select>
        </div>

        {/* Source Filter */}
        <div>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
          >
            <option value="All">All Sources</option>
            <option value="Jobvetta">Jobvetta Official</option>
            <option value="Adzuna">Adzuna Official</option>
            <option value="Greenhouse">Greenhouse Official</option>
            <option value="Lever">Lever Official</option>
            <option value="NCS">NCS (National Career Service)</option>
            <option value="PMIS">PM Scheme Official</option>
            <option value="COMPANY_CAREER">Official Company Careers</option>
          </select>
        </div>

        {/* Sector Filter */}
        <div>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
          >
            <option value="All">All Sectors</option>
            <option value="Public Sector / Aerospace">Public Sector / Aerospace</option>
            <option value="Government Policy & Public Admin">Government Policy & Public Admin</option>
            <option value="Public Sector / Heavy Engineering">Public Sector / Heavy Engineering</option>
            <option value="Automotive & Mobility Tech">Automotive & Mobility Tech</option>
            <option value="Banking & Financial Services">Banking & Financial Services</option>
            <option value="IT & Software Services">IT & Software Services</option>
            <option value="Clean Energy & Renewable Tech">Clean Energy & Renewable Tech</option>
          </select>
        </div>

        {/* Work Mode Filter */}
        <div>
          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
          >
            <option value="All">All Work Modes</option>
            <option value="On-site">On-site</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
          </select>
        </div>

      </div>

      {/* Grid */}
      {loading ? (
        <div className="py-12 text-center text-slate-600">
          <div className="inline-block w-7 h-7 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mb-3" />
          <p className="text-xs font-semibold">Loading scheme opportunities catalog...</p>
        </div>
      ) : internships.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {internships.map((opp, idx) => (
            <InternshipCard key={idx} internship={opp} />
          ))}
        </div>
      ) : (
        <div className="p-8 text-center bg-white border border-slate-300 rounded">
          <p className="text-xs text-slate-600 font-medium">No internships found matching your filter criteria.</p>
        </div>
      )}

    </div>
  );
}
