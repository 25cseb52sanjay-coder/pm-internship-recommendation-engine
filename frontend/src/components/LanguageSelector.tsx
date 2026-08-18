"use client";

import { useState, useRef, useEffect } from "react";
import { useLanguage, SUPPORTED_LOCALES } from "@/context/LanguageContext";
import { Globe, Check, Search, ChevronDown } from "lucide-react";

export default function LanguageSelector() {
  const { locale, setLocale } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLocale = SUPPORTED_LOCALES.find((l) => l.code === locale) || SUPPORTED_LOCALES[0];

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredLocales = SUPPORTED_LOCALES.filter(
    (l) =>
      l.nativeName.toLowerCase().includes(search.toLowerCase()) ||
      l.englishName.toLowerCase().includes(search.toLowerCase()) ||
      l.code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      {/* Selector Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold text-[11px] border border-slate-700 transition-colors shadow-sm focus:outline-none focus:ring-1 focus:ring-amber-400"
        title="Select Language / भाषा चुनें"
        aria-expanded={isOpen}
      >
        <Globe className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span>{currentLocale.nativeName}</span>
        <span className="text-[10px] text-slate-400">({currentLocale.code.toUpperCase()})</span>
        <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform duration-150 ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-1.5 w-64 rounded-xl bg-white border border-slate-300 shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
          
          {/* Header & Search */}
          <div className="p-2.5 bg-slate-50 border-b border-slate-200 space-y-2">
            <div className="flex items-center justify-between px-1">
              <span className="text-[11px] font-bold text-[#002147] uppercase tracking-wider">Select Portal Language</span>
              <span className="text-[10px] font-semibold text-slate-500">25 Locales</span>
            </div>

            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search language / भाषा ढूँढें..."
                className="w-full bg-white border border-slate-300 rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-blue-700"
              />
            </div>
          </div>

          {/* Languages List */}
          <div className="max-h-64 overflow-y-auto custom-scrollbar divide-y divide-slate-100 text-xs">
            {filteredLocales.length > 0 ? (
              filteredLocales.map((item) => {
                const isSelected = item.code === locale;
                return (
                  <button
                    key={item.code}
                    onClick={() => {
                      setLocale(item.code);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 text-left hover:bg-blue-50 transition-colors ${
                      isSelected ? "bg-blue-50/80 font-bold text-blue-900" : "text-slate-800"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-slate-900">{item.nativeName}</span>
                      {item.englishName !== item.nativeName && (
                        <span className="text-[11px] text-slate-500">({item.englishName})</span>
                      )}
                      {item.dir === "rtl" && (
                        <span className="px-1 py-0.2 text-[9px] font-bold bg-amber-100 text-amber-900 rounded">RTL</span>
                      )}
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-blue-700 shrink-0 ml-2" />}
                  </button>
                );
              })
            ) : (
              <div className="p-4 text-center text-xs text-slate-500">No language matches search</div>
            )}
          </div>

          {/* Footer Note */}
          <div className="p-2 bg-slate-100 border-t border-slate-200 text-[10px] text-slate-600 text-center">
            Official PM Scheme Multilingual Engine
          </div>

        </div>
      )}
    </div>
  );
}
