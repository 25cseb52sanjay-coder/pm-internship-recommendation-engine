import os
import json

MESSAGES_DIR = r"C:\Users\91733\.gemini\antigravity\scratch\pm-internship-recommendation-engine\frontend\src\messages"
os.makedirs(MESSAGES_DIR, exist_ok=True)

LOCALES = [
    "en", "hi", "te", "ta", "kn", "ml", "ur", "pa", "sd", "mr",
    "gu", "bn", "or", "fr", "zh", "ar", "pt", "de", "ja", "ko",
    "it", "tr", "ms", "ne", "sw"
]

# Base English dictionary
EN = {
  "nav": {
    "home": "Home",
    "apply_internship": "Apply Internship",
    "live_24_7": "LIVE 24/7",
    "candidate_dashboard": "Candidate Dashboard",
    "ai_recommendations": "AI Recommendations",
    "skill_gap_matrix": "Skill Gap Matrix",
    "opportunities_catalog": "Opportunities Catalog",
    "profile_resume": "Profile & Resume",
    "scheme_admin_portal": "Scheme Admin Portal",
    "logout": "Logout",
    "sign_in": "Sign In",
    "register": "Candidate Register",
    "portal_title": "PRIME MINISTER'S INTERNSHIP SCHEME (PMIS)",
    "ai_match_portal": "AI Match Portal",
    "portal_subtitle": "Ministry of Corporate Affairs & NITI Aayog Initiative • AI Recommendation Engine",
    "gov_service": "Government Digital Service Portal",
    "sih_prototype": "Smart India Hackathon (SIH) Prototype",
    "helpdesk": "Toll Free Helpdesk: 1800-11-2026",
    "font": "Font:"
  },
  "home": {
    "hero_title": "AI-Powered National Internship Recommendation Engine",
    "hero_subtitle": "Connecting eligible youth across India with top corporate and public sector opportunities under the Prime Minister's Internship Scheme using eligibility-aware recommendation algorithms.",
    "apply_now": "Explore 24/7 Live Opportunities",
    "register_now": "Register as Candidate",
    "admin_login": "Scheme Admin Portal",
    "scheme_highlights": "PM Internship Scheme Highlights",
    "stipend_title": "₹5,000 / month Financial Support",
    "stipend_desc": "Government stipend support of ₹4,500/month plus company contribution of ₹500/month directly transferred to candidate bank accounts.",
    "top_companies_title": "500 Top Companies & PSUs",
    "top_companies_desc": "Opportunities offered by India's top 500 companies across aerospace, EV tech, banking, energy, IT, and manufacturing sectors.",
    "duration_title": "12 Months Hands-on Training",
    "duration_desc": "Comprehensive 1-year internship experience with minimum 6 months real-world workplace training in leading enterprises.",
    "onboarding_title": "One-Time Grant ₹6,000",
    "onboarding_desc": "Additional one-time incidentals grant provided upon joining the internship for accommodation and preparation."
  },
  "apply": {
    "page_title": "24/7 Live Corporate & PSU Opportunity Stream",
    "page_subtitle": "Real-time automated ingestion stream scanning official career portals across India. Updated continuously with verified openings.",
    "authoritative_verifying": "Authoritative Verification In Progress",
    "authoritative_desc": "All listings undergo mandatory authoritative source URL validation, employer confirmation, and SHA-256 deduplication before being assigned VERIFIED_LIVE. Synthetic or unverified listings are strictly excluded from live public display.",
    "scanning_badge": "24/7 Discovery & Verification Engine Scanning Official Portals",
    "search_placeholder": "Search by company name, role, or city...",
    "all_sectors": "All Sectors",
    "all_work_modes": "All Work Modes",
    "apply_now_btn": "Apply Now →",
    "verified_live_badge": "Verified Live",
    "official_posting_badge": "Official PM Scheme Posting",
    "stipend_label": "Stipend",
    "duration_label": "Duration",
    "deadline_label": "Deadline",
    "seats_label": "Seats",
    "location_label": "Location",
    "work_mode_label": "Work Mode",
    "modal_title": "Submit Application",
    "modal_confirm": "Confirm Application Submission",
    "modal_cancel": "Cancel",
    "submitting": "Submitting Application..."
  },
  "recommendations": {
    "title": "AI Opportunity Match Matrix & Recommendations",
    "subtitle": "Personalized internship matches calculated using multi-dimensional cosine vector similarity, hard eligibility rules, and candidate preferences.",
    "match_score": "Match Score",
    "explainability_title": "AI Match Breakdown",
    "skill_match_weight": "Skill Compatibility",
    "semantic_weight": "Semantic Context",
    "education_weight": "Academic Alignment",
    "location_weight": "Geographic Proximity",
    "no_recs": "No matching recommendations found for your profile criteria."
  },
  "dashboard": {
    "title": "Candidate Control Center & Application Tracker",
    "subtitle": "Track your scheme applications, view real-time status updates, and manage your AI matching profile.",
    "applied_count": "Submitted Applications",
    "saved_count": "Saved Opportunities",
    "status_applied": "Applied",
    "status_shortlisted": "Shortlisted",
    "status_allocated": "Allocated Seat",
    "status_rejected": "Not Selected"
  },
  "internships": {
    "title": "Verified Opportunities Catalog",
    "subtitle": "Browse verified corporate and public sector internship positions.",
    "filter_sector": "Sector",
    "filter_location": "City / Location",
    "filter_mode": "Work Mode",
    "sort_by": "Sort By",
    "newest": "Newest First",
    "stipend_high": "Highest Stipend"
  },
  "profile": {
    "title": "Candidate Profile & Resume Management",
    "subtitle": "Keep your academic qualifications, skill inventory, and resume up to date for optimal AI matching.",
    "personal_info": "Personal & Academic Information",
    "full_name": "Full Name",
    "email": "Email Address",
    "phone": "Phone Number",
    "age": "Age",
    "qualification": "Highest Qualification",
    "degree": "Degree / Stream",
    "institution": "Institution / University",
    "cgpa": "CGPA / Percentage",
    "skills_header": "Skill Inventory",
    "upload_resume": "Upload Resume (PDF/PNG)",
    "save_changes": "Save Profile Changes"
  },
  "auth": {
    "login_title": "Sign In to Candidate Portal",
    "login_subtitle": "Access your AI recommendation matrix and application status",
    "email_label": "Email Address",
    "password_label": "Password",
    "login_btn": "Sign In",
    "register_title": "Create Candidate Account",
    "register_subtitle": "Join the Prime Minister's Internship Scheme AI Portal",
    "register_btn": "Complete Candidate Registration",
    "google_signin": "Sign in with Google",
    "or": "OR"
  },
  "admin": {
    "title": "Scheme Officer Control Center & Seat Allocation Engine",
    "subtitle": "Manage scheme rules, monitor ingestion health, and execute AI-driven seat allocation routines.",
    "total_internships": "Total Live Opportunities",
    "total_candidates": "Registered Candidates",
    "run_allocation": "Execute Smart Seat Allocation",
    "ingestion_health": "Ingestion Pipeline Health",
    "discovery_status": "Discovery Engine Status"
  },
  "footer": {
    "scheme_name": "PRIME MINISTER'S INTERNSHIP SCHEME (PMIS)",
    "scheme_desc": "Initiative by the Ministry of Corporate Affairs and NITI Aayog to empower youth with skill training in top 500 companies across India.",
    "navigation_title": "Portal Navigation",
    "policies_title": "Rules & Policies",
    "helpdesk_title": "Scheme Helpdesk",
    "eligibility_rules": "Eligibility Criteria (21-24 Yrs)",
    "stipend_rules": "Stipend Rules (₹5,000 + Partner Top-Up)",
    "reservation_norms": "Reservation & Quota Norms",
    "privacy_policy": "Data Privacy & Security Norms",
    "helpdesk_phone": "1800-11-2026 (Mon-Sat 9AM-6PM)",
    "helpdesk_email": "support-pmis@mca.gov.in",
    "copyright": "© 2026 Prime Minister's Internship Scheme AI Recommendation Portal. All Rights Reserved."
  },
  "common": {
    "apply": "Apply Now",
    "cancel": "Cancel",
    "submit": "Submit",
    "save": "Save",
    "loading": "Loading...",
    "search": "Search",
    "clear": "Clear Filters",
    "logout": "Logout",
    "success": "Success",
    "error": "Error"
  }
}

# Key phrase overrides for prominent languages
HI = {
  **EN,
  "nav": {
    **EN["nav"],
    "home": "मुख्य पृष्ठ",
    "apply_internship": "इंटर्नशिप आवेदन",
    "candidate_dashboard": "उम्मीदवार डैशबोर्ड",
    "ai_recommendations": "एआई सिफारिशें",
    "skill_gap_matrix": "कौशल अंतर मैट्रिक्स",
    "opportunities_catalog": "अवसर सूची",
    "profile_resume": "प्रोफ़ाइल और बायोडाटा",
    "scheme_admin_portal": "योजना व्यवस्थापक पोर्टल",
    "logout": "लॉग आउट",
    "sign_in": "साइन इन",
    "register": "पंजीकरण करें",
    "portal_title": "प्रधानमंत्री इंटर्नशिप योजना (PMIS)",
    "gov_service": "सरकारी डिजिटल सेवा पोर्टल"
  },
  "common": {
    **EN["common"],
    "apply": "अभी आवेदन करें",
    "cancel": "रद्द करें",
    "submit": "सबमिट करें",
    "save": "सहेजें",
    "loading": "लोड हो रहा है...",
    "search": "खोजें"
  }
}

TA = {
  **EN,
  "nav": {
    **EN["nav"],
    "home": "முகப்பு",
    "apply_internship": "இன்டர்ன்ஷிப்பிற்கு விண்ணப்பிக்கவும்",
    "candidate_dashboard": "வேட்பாளர் டாஷ்போர்டு",
    "ai_recommendations": "AI பரிந்துரைகள்",
    "skill_gap_matrix": "திறன் இடைவெளி மேட்ரிக்ஸ்",
    "opportunities_catalog": "வாய்ப்புகள் பட்டியல்",
    "profile_resume": "சுயவிவரம் மற்றும் சுயவிவரக் குறிப்பு",
    "scheme_admin_portal": "திட்ட நிர்வாகி போர்டல்",
    "logout": "வெளியேறு",
    "sign_in": "உள்நுழைக",
    "register": "பதிவு செய்ய",
    "portal_title": "பிரதமரின் இன்டர்ன்ஷிப் திட்டம் (PMIS)",
    "gov_service": "அரசு டிஜிட்டல் சேவை போர்டல்"
  },
  "common": {
    **EN["common"],
    "apply": "இப்போதே விண்ணப்பிக்கவும்",
    "cancel": "ரத்து செய்",
    "submit": "சமர்ப்பி",
    "save": "சேமி",
    "loading": "ஏற்றுகிறது...",
    "search": "தேடு"
  }
}

TE = {
  **EN,
  "nav": {
    **EN["nav"],
    "home": "హోమ్",
    "apply_internship": "ఇంటర్న్‌షిప్ దరఖాస్తు",
    "candidate_dashboard": "అభ్యర్థి డాష్‌బోర్డ్",
    "ai_recommendations": "AI సిఫార్సులు",
    "skill_gap_matrix": "నైపుణ్య గ్యాప్ మ్యాట్రిక్స్",
    "opportunities_catalog": "అవకాశాల కేటలాగ్",
    "profile_resume": "ప్రొఫైల్ & రెజ్యూమ్",
    "scheme_admin_portal": "స్కీమ్ అడ్మిన్ పోర్టల్",
    "logout": "లాగ్‌అవుట్",
    "sign_in": "సైన్ ఇన్",
    "register": "నమోదు చేసుకోండి",
    "portal_title": "ప్రధాన మంత్రి ఇంటర్న్‌షిప్ పథకం (PMIS)"
  }
}

AR = {
  **EN,
  "nav": {
    **EN["nav"],
    "home": "الرئيسية",
    "apply_internship": "التقديم للتدريب",
    "candidate_dashboard": "لوحة تحكم المرشح",
    "ai_recommendations": "توصيات الذكاء الاصطناعي",
    "skill_gap_matrix": "مصفوفة فجوة المهارات",
    "opportunities_catalog": "كتالوج الفرص",
    "profile_resume": "الملف الشخصي والسيرة الذاتية",
    "scheme_admin_portal": "بوابة مدير البرنامج",
    "logout": "تسجيل الخروج",
    "sign_in": "تسجيل الدخول",
    "register": "تسجيل المرشح",
    "portal_title": "برنامج رئيس الوزراء للتدريب (PMIS)"
  },
  "common": {
    **EN["common"],
    "apply": "قدم الآن",
    "cancel": "إلغاء",
    "submit": "إرسال",
    "save": "حفظ",
    "loading": "جاري التحميل...",
    "search": "بحث"
  }
}

UR = {
  **EN,
  "nav": {
    **EN["nav"],
    "home": "ہوم",
    "apply_internship": "انٹرنشپ کے لیے اپلائی کریں",
    "candidate_dashboard": "امیدوار کا ڈیش بورڈ",
    "ai_recommendations": "اے آئی سفارشات",
    "skill_gap_matrix": "مہارت کا موازنہ",
    "opportunities_catalog": "مواقع کا کیٹلاگ",
    "profile_resume": "پروفائل اور سی وی",
    "scheme_admin_portal": "اسکیم ایڈمن پورٹل",
    "logout": "لاگ آؤٹ",
    "sign_in": "سائن ان",
    "register": "رجسٹر کریں",
    "portal_title": "وزیر اعظم انٹرنشپ اسکیم (PMIS)"
  }
}

def generate_messages():
    for loc in LOCALES:
        filepath = os.path.join(MESSAGES_DIR, f"{loc}.json")
        if loc == "en":
            data = EN
        elif loc == "hi":
            data = HI
        elif loc == "ta":
            data = TA
        elif loc == "te":
            data = TE
        elif loc == "ar":
            data = AR
        elif loc == "ur":
            data = UR
        else:
            # Fallback structure with language badge indicator for clean runtime testing
            data = json.loads(json.dumps(EN))
            data["nav"]["home"] = f"Home ({loc.upper()})"
            data["nav"]["apply_internship"] = f"Apply Internship ({loc.upper()})"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {len(LOCALES)} translation dictionary files in {MESSAGES_DIR}")

if __name__ == "__main__":
    generate_messages()
