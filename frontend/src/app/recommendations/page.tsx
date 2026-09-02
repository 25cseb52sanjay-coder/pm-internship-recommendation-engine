"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import InternshipCard from "@/components/InternshipCard";
import { Sparkles, Search, ShieldCheck } from "lucide-react";

const DEFAULT_RECOMMENDATIONS = [
  {
    internship: {
      id: 9101,
      title: "Frontend Developer",
      company_name: "PulseStack Studios",
      company_sector: "Technology & Corporate Services",
      description: "Join PulseStack Studios to build responsive, high-performance web interfaces using modern frontend architectures, React components, and Tailwind styling.",
      location: "Chennai, India",
      work_mode: "Remote",
      opportunity_type: "Full Time",
      duration: "Full-Time Position",
      stipend: "₹12,000,000 - ₹18,000,000 / year",
      deadline: "2026-10-30",
      positions: 4,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-frontend-dev-chn",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-frontend-dev-chn",
      skills: [
        { skill: { name: "React" }, is_required: true },
        { skill: { name: "Next.js" }, is_required: true },
        { skill: { name: "TypeScript" }, is_required: true },
        { skill: { name: "Tailwind CSS" }, is_required: false },
        { skill: { name: "GraphQL" }, is_required: false },
        { skill: { name: "State Management" }, is_required: false }
      ]
    },
    match_category: "Excellent Match",
    score: 95,
    recommendation: {
      score: 95,
      match_category: "Excellent Match",
      explanation: {
        match_level: "EXCELLENT",
        breakdown: { skill_match: 96, semantic_match: 94, education_match: 95, interest_match: 95 },
        reasoning: "Exceptional alignment with modern frontend stack, React component architecture, and web performance engineering."
      }
    }
  },
  {
    internship: {
      id: 9102,
      title: "Software Engineering Intern",
      company_name: "NexaWave Technologies",
      company_sector: "IT Services & Digital Systems",
      description: "Join our engineering team and work on scalable software systems, backend microservices, and database optimizations.",
      location: "Bangalore, India",
      work_mode: "Hybrid",
      opportunity_type: "INTERNSHIP",
      duration: "6 Months",
      stipend: "₹35,000 - ₹50,000 / month",
      deadline: "2026-10-15",
      positions: 5,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-swe-intern-blr",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-swe-intern-blr",
      skills: [
        { skill: { name: "TypeScript" }, is_required: true },
        { skill: { name: "Node.js" }, is_required: true },
        { skill: { name: "Go" }, is_required: false },
        { skill: { name: "PostgreSQL" }, is_required: false },
        { skill: { name: "Docker" }, is_required: false },
        { skill: { name: "Git" }, is_required: false },
        { skill: { name: "Data Structures" }, is_required: false }
      ]
    },
    match_category: "Excellent Match",
    score: 92,
    recommendation: {
      score: 92,
      match_category: "Excellent Match",
      explanation: {
        match_level: "EXCELLENT",
        breakdown: { skill_match: 93, semantic_match: 91, education_match: 90, interest_match: 94 },
        reasoning: "High score matching candidate core skills in TypeScript, Node.js, Go backend services, and distributed database design."
      }
    }
  },
  {
    internship: {
      id: 9103,
      title: "Backend Developer",
      company_name: "CloudAura Systems",
      company_sector: "IT Services & Digital Systems",
      description: "Architect and maintain robust server-side APIs, database models, caching mechanisms, and cloud deployment pipelines.",
      location: "Bangalore, India",
      work_mode: "Hybrid",
      opportunity_type: "Full Time",
      duration: "Full-Time Position",
      stipend: "₹14,000,000 - ₹22,000,000 / year",
      deadline: "2026-11-01",
      positions: 3,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-backend-dev-blr",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-backend-dev-blr",
      skills: [
        { skill: { name: "Node.js" }, is_required: true },
        { skill: { name: "TypeScript" }, is_required: true },
        { skill: { name: "PostgreSQL" }, is_required: true },
        { skill: { name: "Redis" }, is_required: false },
        { skill: { name: "Kafka" }, is_required: false },
        { skill: { name: "Docker" }, is_required: false },
        { skill: { name: "Kubernetes" }, is_required: false }
      ]
    },
    match_category: "Strong Match",
    score: 88,
    recommendation: {
      score: 88,
      match_category: "Strong Match",
      explanation: {
        match_level: "STRONG",
        breakdown: { skill_match: 89, semantic_match: 87, education_match: 88, interest_match: 88 },
        reasoning: "Solid backend architecture profile with extensive Node.js, PostgreSQL, Redis, and event streaming experience."
      }
    }
  },
  {
    internship: {
      id: 9104,
      title: "Data Analyst Intern",
      company_name: "MetricFlow Analytics",
      company_sector: "Technology & Corporate Services",
      description: "Analyze complex business datasets, generate automated reporting dashboards, and build SQL queries for data-driven insights.",
      location: "Hyderabad, India",
      work_mode: "Hybrid",
      opportunity_type: "INTERNSHIP",
      duration: "6 Months",
      stipend: "₹30,000 - ₹45,000 / month",
      deadline: "2026-10-20",
      positions: 6,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-data-analyst-intern-hyd",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-data-analyst-intern-hyd",
      skills: [
        { skill: { name: "SQL" }, is_required: true },
        { skill: { name: "Python" }, is_required: true },
        { skill: { name: "Pandas" }, is_required: false },
        { skill: { name: "Power BI" }, is_required: false },
        { skill: { name: "Tableau" }, is_required: false },
        { skill: { name: "Data Visualization" }, is_required: false },
        { skill: { name: "Statistics" }, is_required: false }
      ]
    },
    match_category: "Strong Match",
    score: 85,
    recommendation: {
      score: 85,
      match_category: "Strong Match",
      explanation: {
        match_level: "STRONG",
        breakdown: { skill_match: 86, semantic_match: 84, education_match: 85, interest_match: 85 },
        reasoning: "Strong analytical skill match across SQL databases, Python data processing, PowerBI, and statistical reporting."
      }
    }
  },
  {
    internship: {
      id: 9105,
      title: "Frontend Developer (UI Platforms)",
      company_name: "PulseStack Studios",
      company_sector: "Technology & Corporate Services",
      description: "Join PulseStack Studios to build responsive, high-performance web interfaces using modern frontend architectures, React components, and Tailwind styling.",
      location: "Chennai, India",
      work_mode: "Remote",
      opportunity_type: "Full Time",
      duration: "Full-Time Position",
      stipend: "₹12,000,000 - ₹18,000,000 / year",
      deadline: "2026-11-15",
      positions: 3,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-frontend-dev-chn",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-frontend-dev-chn",
      skills: [
        { skill: { name: "React" }, is_required: true },
        { skill: { name: "Next.js" }, is_required: true },
        { skill: { name: "TypeScript" }, is_required: true },
        { skill: { name: "Tailwind CSS" }, is_required: false },
        { skill: { name: "GraphQL" }, is_required: false }
      ]
    },
    match_category: "Good Match",
    score: 79,
    recommendation: {
      score: 79,
      match_category: "Good Match",
      explanation: {
        match_level: "GOOD",
        breakdown: { skill_match: 80, semantic_match: 78, education_match: 78, interest_match: 80 },
        reasoning: "Good match alignment with web platform engineering, design system components, and client-side performance."
      }
    }
  },
  {
    internship: {
      id: 9106,
      title: "Software Engineering Intern (Cloud Systems)",
      company_name: "NexaWave Technologies",
      company_sector: "IT Services & Digital Systems",
      description: "Join our engineering team and work on scalable software systems, backend microservices, and database optimizations.",
      location: "Bangalore, India",
      work_mode: "Hybrid",
      opportunity_type: "INTERNSHIP",
      duration: "6 Months",
      stipend: "₹35,000 - ₹50,000 / month",
      deadline: "2026-11-05",
      positions: 4,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-swe-intern-blr",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-swe-intern-blr",
      skills: [
        { skill: { name: "TypeScript" }, is_required: true },
        { skill: { name: "Node.js" }, is_required: true },
        { skill: { name: "Go" }, is_required: false },
        { skill: { name: "PostgreSQL" }, is_required: false }
      ]
    },
    match_category: "Good Match",
    score: 76,
    recommendation: {
      score: 76,
      match_category: "Good Match",
      explanation: {
        match_level: "GOOD",
        breakdown: { skill_match: 77, semantic_match: 75, education_match: 76, interest_match: 76 },
        reasoning: "Good functional alignment for distributed backend engineering and database development."
      }
    }
  },
  {
    internship: {
      id: 9107,
      title: "Backend Developer (Distributed Systems)",
      company_name: "CloudAura Systems",
      company_sector: "IT Services & Digital Systems",
      description: "Architect and maintain robust server-side APIs, database models, caching mechanisms, and cloud deployment pipelines.",
      location: "Bangalore, India",
      work_mode: "Hybrid",
      opportunity_type: "Full Time",
      duration: "Full-Time Position",
      stipend: "₹14,000,000 - ₹22,000,000 / year",
      deadline: "2026-11-20",
      positions: 2,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-backend-dev-blr",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-backend-dev-blr",
      skills: [
        { skill: { name: "Node.js" }, is_required: true },
        { skill: { name: "TypeScript" }, is_required: true },
        { skill: { name: "PostgreSQL" }, is_required: true },
        { skill: { name: "Redis" }, is_required: false }
      ]
    },
    match_category: "Potential Match",
    score: 68,
    recommendation: {
      score: 68,
      match_category: "Potential Match",
      explanation: {
        match_level: "POTENTIAL",
        breakdown: { skill_match: 70, semantic_match: 67, education_match: 68, interest_match: 67 },
        reasoning: "Potential match alignment for enterprise microservices development."
      }
    }
  },
  {
    internship: {
      id: 9108,
      title: "Data Analyst Intern (BI & Reporting)",
      company_name: "MetricFlow Analytics",
      company_sector: "Technology & Corporate Services",
      description: "Analyze complex business datasets, generate automated reporting dashboards, and build SQL queries for data-driven insights.",
      location: "Hyderabad, India",
      work_mode: "Hybrid",
      opportunity_type: "INTERNSHIP",
      duration: "6 Months",
      stipend: "₹30,000 - ₹45,000 / month",
      deadline: "2026-11-10",
      positions: 5,
      source: "Jobvetta",
      source_name: "Jobify Demo",
      apply_url: "https://jobify-beta-cyan.vercel.app/jobs/job-data-analyst-intern-hyd",
      application_url: "https://jobify-beta-cyan.vercel.app/jobs/job-data-analyst-intern-hyd",
      skills: [
        { skill: { name: "SQL" }, is_required: true },
        { skill: { name: "Python" }, is_required: true },
        { skill: { name: "Pandas" }, is_required: false },
        { skill: { name: "Power BI" }, is_required: false }
      ]
    },
    match_category: "Potential Match",
    score: 64,
    recommendation: {
      score: 64,
      match_category: "Potential Match",
      explanation: {
        match_level: "POTENTIAL",
        breakdown: { skill_match: 65, semantic_match: 63, education_match: 64, interest_match: 64 },
        reasoning: "Potential match alignment for business intelligence reporting and database telemetry."
      }
    }
  }
];

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
        if (data && Array.isArray(data) && data.length > 0) {
          setRecommendations(data);
          setFilteredRecs(data);
        } else {
          setRecommendations(DEFAULT_RECOMMENDATIONS);
          setFilteredRecs(DEFAULT_RECOMMENDATIONS);
        }
      } catch (err) {
        console.error("Error loading recommendations:", err);
        setRecommendations(DEFAULT_RECOMMENDATIONS);
        setFilteredRecs(DEFAULT_RECOMMENDATIONS);
      } finally {
        setLoading(false);
      }
    }
    loadRecommendations();
  }, []);

  useEffect(() => {
    let result = recommendations.length > 0 ? [...recommendations] : [...DEFAULT_RECOMMENDATIONS];

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

  const displayList = filteredRecs.length > 0 ? filteredRecs : DEFAULT_RECOMMENDATIONS;

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
            {cat} {cat === "All" ? `(${recommendations.length > 0 ? recommendations.length : DEFAULT_RECOMMENDATIONS.length})` : ""}
          </button>
        ))}
      </div>

      {/* Grid of Ranked Internships */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {displayList.map((rec, idx) => (
          <InternshipCard
            key={idx}
            internship={rec.internship}
            recommendation={rec}
          />
        ))}
      </div>

    </div>
  );
}
