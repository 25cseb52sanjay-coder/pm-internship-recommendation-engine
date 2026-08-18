"use client";

import Link from "next/link";
import { ShieldCheck, Phone, Mail, HelpCircle, FileText, ExternalLink } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="w-full bg-[#001529] text-slate-300 border-t border-slate-300">
      
      {/* Subtle Flag Tricolor Accent Line */}
      <div className="h-1 w-full flex">
        <div className="h-full w-1/3 bg-amber-600" />
        <div className="h-full w-1/3 bg-white" />
        <div className="h-full w-1/3 bg-emerald-700" />
      </div>

      {/* Main Footer Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Col 1: Scheme Intro */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded border border-slate-500 bg-white flex items-center justify-center text-[10px] font-black text-[#002147]">
                GOI
              </div>
              <h3 className="font-bold text-white text-sm tracking-tight">{t("footer.scheme_name")}</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {t("footer.scheme_desc")}
            </p>
            <p className="text-[11px] text-amber-400 font-semibold">Smart India Hackathon (SIH) 2026 Prototype</p>
          </div>

          {/* Col 2: Quick Links */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-700 pb-1">{t("footer.navigation_title")}</h4>
            <ul className="space-y-1.5 text-xs text-slate-300">
              <li><Link href="/" className="hover:text-amber-400 transition-colors flex items-center"><span className="mr-1.5 text-slate-500">›</span> {t("nav.home")}</Link></li>
              <li><Link href="/dashboard" className="hover:text-amber-400 transition-colors flex items-center"><span className="mr-1.5 text-slate-500">›</span> {t("nav.candidate_dashboard")}</Link></li>
              <li><Link href="/recommendations" className="hover:text-amber-400 transition-colors flex items-center"><span className="mr-1.5 text-slate-500">›</span> {t("nav.ai_recommendations")}</Link></li>
              <li><Link href="/skill-gap" className="hover:text-amber-400 transition-colors flex items-center"><span className="mr-1.5 text-slate-500">›</span> {t("nav.skill_gap_matrix")}</Link></li>
              <li><Link href="/internships" className="hover:text-amber-400 transition-colors flex items-center"><span className="mr-1.5 text-slate-500">›</span> {t("nav.opportunities_catalog")}</Link></li>
            </ul>
          </div>

          {/* Col 3: Guidelines & Policies */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-700 pb-1">{t("footer.policies_title")}</h4>
            <ul className="space-y-1.5 text-xs text-slate-300">
              <li className="flex items-center space-x-1"><FileText className="w-3 h-3 text-emerald-400" /><span>{t("footer.eligibility_rules")}</span></li>
              <li className="flex items-center space-x-1"><FileText className="w-3 h-3 text-emerald-400" /><span>{t("footer.stipend_rules")}</span></li>
              <li className="flex items-center space-x-1"><FileText className="w-3 h-3 text-emerald-400" /><span>{t("footer.reservation_norms")}</span></li>
              <li className="flex items-center space-x-1"><FileText className="w-3 h-3 text-emerald-400" /><span>Explainable AI Evaluation Standards</span></li>
              <li className="flex items-center space-x-1"><FileText className="w-3 h-3 text-emerald-400" /><span>{t("footer.privacy_policy")}</span></li>
            </ul>
          </div>

          {/* Col 4: Helpdesk & Support */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-700 pb-1">{t("footer.helpdesk_title")}</h4>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-start space-x-2">
                <Phone className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Toll-Free Helpline</p>
                  <p className="text-slate-400">{t("footer.helpdesk_phone")}</p>
                </div>
              </div>

              <div className="flex items-start space-x-2">
                <Mail className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Official Help Desk Email</p>
                  <p className="text-slate-400">{t("footer.helpdesk_email")}</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Copyright & Disclaimer Bar */}
      <div className="bg-[#000d1a] border-t border-slate-800 text-[11px] text-slate-400 py-4 px-4 sm:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
          <p>
            {t("footer.copyright")}
          </p>
          <div className="flex items-center space-x-3 text-slate-300">
            <span className="hover:underline cursor-pointer">Terms of Service</span>
            <span>•</span>
            <span className="hover:underline cursor-pointer">Privacy Policy</span>
            <span>•</span>
            <span className="hover:underline cursor-pointer">Accessibility Statement</span>
            <span>•</span>
            <span className="hover:underline cursor-pointer">Sitemap</span>
          </div>
        </div>
      </div>

    </footer>
  );
}
