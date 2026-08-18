"use client";

import React, { createContext, useContext, useEffect, useState, useTransition } from "react";
import { getCurrentUser, fetchApi } from "@/lib/api";

// 25 Supported Locales Metadata
export interface LocaleInfo {
  code: string;
  nativeName: string;
  englishName: string;
  dir: "ltr" | "rtl";
}

export const SUPPORTED_LOCALES: LocaleInfo[] = [
  { code: "en", nativeName: "English", englishName: "English", dir: "ltr" },
  { code: "hi", nativeName: "हिन्दी", englishName: "Hindi", dir: "ltr" },
  { code: "te", nativeName: "తెలుగు", englishName: "Telugu", dir: "ltr" },
  { code: "ta", nativeName: "தமிழ்", englishName: "Tamil", dir: "ltr" },
  { code: "kn", nativeName: "ಕನ್ನಡ", englishName: "Kannada", dir: "ltr" },
  { code: "ml", nativeName: "മലയാളം", englishName: "Malayalam", dir: "ltr" },
  { code: "ur", nativeName: "اردو", englishName: "Urdu", dir: "rtl" },
  { code: "pa", nativeName: "ਪੰਜਾਬੀ", englishName: "Punjabi", dir: "ltr" },
  { code: "sd", nativeName: "سنڌي", englishName: "Sindhi", dir: "rtl" },
  { code: "mr", nativeName: "मराठी", englishName: "Marathi", dir: "ltr" },
  { code: "gu", nativeName: "ગુજરાતી", englishName: "Gujarati", dir: "ltr" },
  { code: "bn", nativeName: "বাংলা", englishName: "Bengali", dir: "ltr" },
  { code: "or", nativeName: "ଓଡ଼ିଆ", englishName: "Odia", dir: "ltr" },
  { code: "fr", nativeName: "Français", englishName: "French", dir: "ltr" },
  { code: "zh", nativeName: "中文", englishName: "Chinese", dir: "ltr" },
  { code: "ar", nativeName: "العربية", englishName: "Arabic", dir: "rtl" },
  { code: "pt", nativeName: "Português", englishName: "Portuguese", dir: "ltr" },
  { code: "de", nativeName: "Deutsch", englishName: "German", dir: "ltr" },
  { code: "ja", nativeName: "日本語", englishName: "Japanese", dir: "ltr" },
  { code: "ko", nativeName: "한국어", englishName: "Korean", dir: "ltr" },
  { code: "it", nativeName: "Italiano", englishName: "Italian", dir: "ltr" },
  { code: "tr", nativeName: "Türkçe", englishName: "Turkish", dir: "ltr" },
  { code: "ms", nativeName: "Bahasa Melayu", englishName: "Malay", dir: "ltr" },
  { code: "ne", nativeName: "नेपाली", englishName: "Nepali", dir: "ltr" },
  { code: "sw", nativeName: "Kiswahili", englishName: "Swahili", dir: "ltr" }
];

// Dynamically import translation dictionaries
import enMessages from "@/messages/en.json";
import hiMessages from "@/messages/hi.json";
import teMessages from "@/messages/te.json";
import taMessages from "@/messages/ta.json";
import knMessages from "@/messages/kn.json";
import mlMessages from "@/messages/ml.json";
import urMessages from "@/messages/ur.json";
import paMessages from "@/messages/pa.json";
import sdMessages from "@/messages/sd.json";
import mrMessages from "@/messages/mr.json";
import guMessages from "@/messages/gu.json";
import bnMessages from "@/messages/bn.json";
import orMessages from "@/messages/or.json";
import frMessages from "@/messages/fr.json";
import zhMessages from "@/messages/zh.json";
import arMessages from "@/messages/ar.json";
import ptMessages from "@/messages/pt.json";
import deMessages from "@/messages/de.json";
import jaMessages from "@/messages/ja.json";
import koMessages from "@/messages/ko.json";
import itMessages from "@/messages/it.json";
import trMessages from "@/messages/tr.json";
import msMessages from "@/messages/ms.json";
import neMessages from "@/messages/ne.json";
import swMessages from "@/messages/sw.json";

const MESSAGE_CATALOG: Record<string, any> = {
  en: enMessages,
  hi: hiMessages,
  te: teMessages,
  ta: taMessages,
  kn: knMessages,
  ml: mlMessages,
  ur: urMessages,
  pa: paMessages,
  sd: sdMessages,
  mr: mrMessages,
  gu: guMessages,
  bn: bnMessages,
  or: orMessages,
  fr: frMessages,
  zh: zhMessages,
  ar: arMessages,
  pt: ptMessages,
  de: deMessages,
  ja: jaMessages,
  ko: koMessages,
  it: itMessages,
  tr: trMessages,
  ms: msMessages,
  ne: neMessages,
  sw: swMessages
};

interface LanguageContextType {
  locale: string;
  dir: "ltr" | "rtl";
  t: (key: string, params?: Record<string, any>) => string;
  setLocale: (newLocale: string) => void;
  isPending: boolean;
}

const LanguageContext = createContext<LanguageContextType>({
  locale: "en",
  dir: "ltr",
  t: (key: string) => key,
  setLocale: () => {},
  isPending: false
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<string>("en");
  const [dir, setDir] = useState<"ltr" | "rtl">("ltr");
  const [isPending, startTransition] = useTransition();

  // Helper to read nested dictionary keys (e.g. "nav.home")
  const getNestedValue = (obj: any, path: string) => {
    return path.split(".").reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined), obj);
  };

  // Translation function with automatic English fallback
  const t = (key: string, params?: Record<string, any>): string => {
    const currentDict = MESSAGE_CATALOG[locale] || MESSAGE_CATALOG["en"];
    let val = getNestedValue(currentDict, key);

    // Fallback to English dictionary if key is missing or blank
    if (val === undefined || val === null || val === "") {
      val = getNestedValue(MESSAGE_CATALOG["en"], key);
    }

    // Final fallback to key name
    if (val === undefined || val === null) {
      return key;
    }

    if (typeof val !== "string") {
      return key;
    }

    // Parameter interpolation (e.g., {name})
    if (params) {
      Object.keys(params).forEach((paramKey) => {
        val = val.replace(new RegExp(`{${paramKey}}`, "g"), params[paramKey]);
      });
    }

    return val;
  };

  // Change locale, update HTML attributes, cookies, localStorage, and sync with backend API if logged in
  const setLocale = (newLocale: string) => {
    const targetInfo = SUPPORTED_LOCALES.find((l) => l.code === newLocale) || SUPPORTED_LOCALES[0];

    startTransition(() => {
      setLocaleState(targetInfo.code);
      setDir(targetInfo.dir);

      // Set HTML document attributes for accessibility & RTL
      if (typeof document !== "undefined") {
        document.documentElement.lang = targetInfo.code;
        document.documentElement.dir = targetInfo.dir;
      }

      // Persist in localStorage and Cookie
      if (typeof window !== "undefined") {
        localStorage.setItem("NEXT_LOCALE", targetInfo.code);
        document.cookie = `NEXT_LOCALE=${targetInfo.code}; path=/; max-age=31536000; SameSite=Lax`;
      }

      // Sync user language preference with backend API if logged in
      const user = getCurrentUser();
      if (user) {
        fetchApi("/users/preferences", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ preferred_locale: targetInfo.code })
        }).catch((err) => console.error("Failed to persist user preferred_locale to backend:", err));
      }
    });
  };

  // Initial load: Restore saved locale from backend preference, cookie, or localStorage
  useEffect(() => {
    let initialLocale = "en";

    // 1. Check authenticated user preference
    const user = getCurrentUser();
    if (user && user.preferred_locale) {
      initialLocale = user.preferred_locale;
    } else if (typeof window !== "undefined") {
      // 2. Check localStorage
      const local = localStorage.getItem("NEXT_LOCALE");
      if (local && SUPPORTED_LOCALES.some((l) => l.code === local)) {
        initialLocale = local;
      } else {
        // 3. Check Cookie
        const match = document.cookie.match(/NEXT_LOCALE=([^;]+)/);
        if (match && SUPPORTED_LOCALES.some((l) => l.code === match[1])) {
          initialLocale = match[1];
        }
      }
    }

    setLocale(initialLocale);
  }, []);

  return (
    <LanguageContext.Provider value={{ locale, dir, t, setLocale, isPending }}>
      <div dir={dir} className={dir === "rtl" ? "rtl" : "ltr"}>
        {children}
      </div>
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
