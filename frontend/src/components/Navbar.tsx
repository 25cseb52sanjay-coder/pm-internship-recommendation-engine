"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { removeAuthToken, getCurrentUser } from "@/lib/api";
import { Award, Compass, LayoutDashboard, LogOut, ShieldCheck, User, Zap, BookOpen, Globe, Phone, Eye } from "lucide-react";
import LanguageSelector from "@/components/LanguageSelector";
import { useLanguage } from "@/context/LanguageContext";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { t } = useLanguage();
  const [user, setUser] = useState<any>(null);
  const [fontSize, setFontSize] = useState<"sm" | "base" | "lg">("base");

  useEffect(() => {
    setUser(getCurrentUser());
  }, [pathname]);

  const handleLogout = () => {
    removeAuthToken();
    setUser(null);
    router.push("/login");
  };

  return (
    <header className="w-full bg-white border-b border-slate-300">
      
      {/* 1. Formal Top Accessibility & Language Utility Bar */}
      <div className="bg-[#061a40] text-slate-200 text-xs py-1.5 px-4 sm:px-8 border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          
          {/* Left Side: Official Portal Metadata */}
          <div className="flex items-center space-x-3">
            <span className="font-semibold text-slate-300 flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5" />
              {t("nav.gov_service")}
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400 text-[11px]">{t("nav.sih_prototype")}</span>
          </div>

          {/* Right Side: Accessibility & Language Controls */}
          <div className="flex items-center space-x-4">
            
            {/* Helpdesk Phone */}
            <div className="hidden md:flex items-center space-x-1 text-slate-300 text-[11px]">
              <Phone className="w-3 h-3 text-amber-400" />
              <span>{t("nav.helpdesk")}</span>
            </div>

            <span className="text-slate-600 hidden md:inline">|</span>

            {/* Language Selector Dropdown (25 Locales) */}
            <LanguageSelector />

            {/* Accessibility Font Size Controls */}
            <div className="flex items-center space-x-1 text-[11px] font-bold bg-slate-800 rounded px-1.5 py-0.5">
              <span className="text-slate-400 mr-1">{t("nav.font")}</span>
              <button onClick={() => setFontSize("sm")} className={`px-1 hover:text-white ${fontSize === "sm" ? "text-amber-400" : "text-slate-300"}`}>A-</button>
              <button onClick={() => setFontSize("base")} className={`px-1 hover:text-white ${fontSize === "base" ? "text-amber-400" : "text-slate-300"}`}>A</button>
              <button onClick={() => setFontSize("lg")} className={`px-1 hover:text-white ${fontSize === "lg" ? "text-amber-400" : "text-slate-300"}`}>A+</button>
            </div>

          </div>
        </div>
      </div>

      {/* 2. Main Scheme Header Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Emblem Placeholder & Scheme Name */}
        <Link href="/" className="flex items-center space-x-4 group">
          
          {/* Official Emblem Placeholder Badge */}
          <div className="w-12 h-12 rounded bg-slate-100 border border-slate-300 flex flex-col items-center justify-center p-1 shadow-sm group-hover:border-blue-700 transition-colors shrink-0">
            <div className="w-6 h-6 rounded-full border-2 border-[#002147] flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-[#002147] flex items-center justify-center text-[7px] text-white font-black">
                ★
              </div>
            </div>
            <span className="text-[8px] font-bold text-slate-700 tracking-tighter uppercase mt-0.5">GOI DEMO</span>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg sm:text-xl font-bold text-[#002147] tracking-tight leading-none">
                {t("nav.portal_title")}
              </h1>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                {t("nav.ai_match_portal")}
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium mt-1">
              {t("nav.portal_subtitle")}
            </p>
          </div>
        </Link>

        {/* Prototype Verification Badge */}
        <div className="hidden lg:flex items-center space-x-3 bg-slate-50 border border-slate-200 rounded px-3 py-2 text-right">
          <div>
            <p className="text-xs font-bold text-[#002147]">SIH 2026 Technology Solution</p>
            <p className="text-[11px] text-slate-500">Public Service Digital Portal Design</p>
          </div>
          <ShieldCheck className="w-6 h-6 text-emerald-700 shrink-0" />
        </div>

      </div>

      {/* 3. Primary Navigation Bar */}
      <nav className="bg-[#002147] border-t-2 border-amber-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-12">
          
          {/* Nav Links */}
          <div className="flex items-center space-x-1 overflow-x-auto custom-scrollbar py-1">
            <Link
              href="/"
              className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap transition-colors ${
                pathname === "/" ? "bg-white text-[#002147]" : "text-slate-200 hover:text-white hover:bg-white/10"
              }`}
            >
              {t("nav.home")}
            </Link>

            {/* Always visible "Apply Internship" Live 24/7 link */}
            <Link
              href="/apply-internship"
              className={`px-3 py-1.5 rounded text-xs font-bold whitespace-nowrap flex items-center space-x-2 transition-all ${
                pathname === "/apply-internship"
                  ? "bg-amber-400 text-slate-950 shadow-sm"
                  : "bg-emerald-600/30 text-emerald-300 hover:bg-emerald-600/50 hover:text-white border border-emerald-500/40"
              }`}
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>{t("nav.apply_internship")}</span>
              <span className="text-[9px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500 text-slate-950">
                {t("nav.live_24_7")}
              </span>
            </Link>

            {user && user.role === "STUDENT" && (
              <>
                <Link
                  href="/dashboard"
                  className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                    pathname === "/dashboard" ? "bg-white text-[#002147]" : "text-slate-200 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <LayoutDashboard className="w-3.5 h-3.5" />
                  <span>{t("nav.candidate_dashboard")}</span>
                </Link>

                <Link
                  href="/recommendations"
                  className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                    pathname === "/recommendations" ? "bg-white text-[#002147]" : "text-slate-200 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <Zap className="w-3.5 h-3.5 text-amber-300" />
                  <span>{t("nav.ai_recommendations")}</span>
                </Link>

                <Link
                  href="/skill-gap"
                  className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                    pathname === "/skill-gap" ? "bg-white text-[#002147]" : "text-slate-200 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <BookOpen className="w-3.5 h-3.5 text-emerald-300" />
                  <span>{t("nav.skill_gap_matrix")}</span>
                </Link>

                <Link
                  href="/internships"
                  className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                    pathname === "/internships" ? "bg-white text-[#002147]" : "text-slate-200 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <Compass className="w-3.5 h-3.5" />
                  <span>{t("nav.opportunities_catalog")}</span>
                </Link>

                <Link
                  href="/profile"
                  className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                    pathname === "/profile" ? "bg-white text-[#002147]" : "text-slate-200 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <User className="w-3.5 h-3.5" />
                  <span>{t("nav.profile_resume")}</span>
                </Link>
              </>
            )}

            {user && user.role === "ADMIN" && (
              <Link
                href="/admin"
                className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                  pathname === "/admin" ? "bg-amber-500 text-slate-950 font-bold" : "text-amber-300 hover:text-white hover:bg-white/10"
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5 text-amber-300" />
                <span>{t("nav.scheme_admin_portal")}</span>
              </Link>
            )}
          </div>

          {/* User Status / Login Buttons */}
          <div className="flex items-center space-x-2 shrink-0">
            {user ? (
              <div className="flex items-center space-x-3 text-xs">
                <span className="hidden sm:inline font-semibold text-slate-200">
                  {user.full_name} <span className="text-[10px] text-amber-300">({user.role})</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="px-2.5 py-1 rounded bg-red-700 hover:bg-red-600 text-white font-semibold flex items-center space-x-1 transition-colors"
                >
                  <LogOut className="w-3 h-3" />
                  <span>{t("nav.logout")}</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-xs font-semibold">
                <Link
                  href="/login"
                  className="px-3 py-1 rounded bg-white/10 hover:bg-white/20 text-white transition-colors"
                >
                  {t("nav.sign_in")}
                </Link>
                <Link
                  href="/register"
                  className="px-3 py-1 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold shadow-sm transition-colors"
                >
                  {t("nav.register")}
                </Link>
              </div>
            )}
          </div>

        </div>
      </nav>

    </header>
  );
}
