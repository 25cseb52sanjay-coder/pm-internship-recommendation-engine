# 🏛️ PM Internship Scheme AI Platform - Comprehensive Technical Summary

> **Document Purpose**: This file provides a complete technical summary of the Prime Minister's Internship Scheme AI Recommendation & Allocation Platform built during this session. It can be shared directly with ChatGPT, Claude, or any developer/LLM to explain the architecture, tech stack, codebase structure, security implementation, database schemas, and current project status.

---

## 📌 Executive Overview

The **PM Internship Scheme Platform** is an enterprise-grade digital governance web application designed to connect eligible Indian youth (ages 21–24) with internship opportunities across public sector enterprises, government ministries, and private corporations.

The solution features:
1. **Frontend Portal (Next.js 14 + TypeScript)**: Indian Government Digital Service aesthetic, drag-and-drop resume upload, full-view image lightbox previews, explainable AI recommendation cards, and Google OAuth 2.0 authentication.
2. **AI Recommendation Microservice (FastAPI + Python 3.13)**: Real-time multi-factor candidate compatibility scoring (Skill Match 35%, Semantic Overlap 25%, Degree Alignment 15%, Location 5%), resume OCR parser, and skill-gap diagnostics.
3. **High-Scale Seat Allocation Engine (Spring Boot 3.3.4 + OpenJDK 26)**: Multi-threaded seat allocation optimizer, deterministic PM Scheme eligibility verifier, simulation dry-runs, `@Transactional` atomic publishing, and immutable audit logs.
4. **Two-Stage Production Security Architecture**: Stage 1 Google OAuth 2.0 cryptographic server-side token validation + Stage 2 SQL database candidate authorization. Strict BCrypt password hashing.

---

## 🏗️ System Architecture & Technology Stack

```
+-------------------------------------------------------------------------------+
|                        INDIAN DIGITAL PORTAL FRONTEND                         |
|                 Next.js 14 App Router / TypeScript / Vanilla CSS              |
|                             http://localhost:3000                             |
+--------------------------------───────┬───────────────────────────────────────+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+---------------------------------+           +---------------------------------+
|     FASTAPI AI MICROSERVICE     |           |  SPRING BOOT ALLOCATION ENGINE  |
|   Python 3.13 / Async SQLite    |           |   Java 26 / Spring Boot 3.3.4   |
|     http://127.0.0.1:8000       |           |     http://127.0.0.1:8080      |
+---------------------------------+           +---------------------------------+
```

### Stack Breakdown:
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, TailwindCSS / Vanilla CSS, Lucide Icons.
- **AI Microservice**: Python 3.13, FastAPI, SQLAlchemy (Async SQLite `aiosqlite`), PyJWT, PassLib (BCrypt), Google Auth OAuth 2.0 library.
- **Allocation Engine**: OpenJDK 26, Spring Boot 3.3.4, Spring Security 6, Spring Data JPA, HikariCP (30 conn), JJWT, Gradle 9.5.1.
- **Database**: SQLite (`pm_internships.db`) & H2/PostgreSQL-compatible JPA schema.

---

## 🎨 1. Frontend UI Portal (`pm-internship-recommendation-engine/frontend`)

### Key Features & Design System:
- **Government Portal Theme**: Deep Navy (`#002147`), Ashoka emblem branding, accessibility top bar with `A- A A+` font size controls, English/Hindi language toggle, live news ticker, and SIH prototype disclaimers.
- **Candidate & Admin Authentication Forms**:
  - **Google OAuth 2.0 GIS**: Client-side Google Identity Services button linked to Client ID `609018289565-qltf0pmrvl7hi1tbu6k445ikb6p3q4ea.apps.googleusercontent.com`.
  - **Permanently Visible Eye Toggle**: Built a custom, permanently visible, and clickable `Eye`/`EyeOff` password visibility icon on both Registration and Login forms.
  - **Clean Form Hygiene**: Disabled browser autofill clutter (`autoComplete="off"` & `autoComplete="new-password"`) with clean placeholder prompts.
  - **Visible Access Tags**: Interactive `Student Account` and `Admin Portal` role selector tags allowing seamless switching without autofilling text into inputs.
  - **Updated Registration Callout**: `"New Candidate? Create Account Here"`.
- **Candidate Dashboard (`/dashboard` & `/profile`)**:
  - **Document & Resume Dropzone**: Native HTML5 Drag-and-Drop resume uploader, `+` Add Image/Document button, upload progress indicator, and resume deletion API.
  - **Full-View Lightbox Preview Modal**: Image/document viewer for uploaded candidate resumes and certificates.
  - **Explainable AI Recommendation Cards**: Displays compatibility scores with progress bars breaking down component contributions (Skill Match 35%, Semantic Overlap 25%, Degree 15%, Location 5%).
  - **Skill Tag Safe Formatting**: Formats both object skill payloads (`{ skill: { name: "Python" } }`) and raw string arrays safely.

---

## 🤖 2. FastAPI AI Microservice (`pm-internship-recommendation-engine/backend`)

### REST API Endpoints:
- `POST /api/v1/auth/register`: Candidate registration with BCrypt password hashing.
- `POST /api/v1/auth/login`: Case-insensitive email lookup with strict BCrypt hash verification (`bcrypt.checkpw`).
- `POST /api/v1/auth/google`: Two-stage Google authentication & SQL database candidate authorization.
- `POST /api/v1/auth/logout`: Clears the HTTP-only `pm_session` cookie.
- `GET /api/v1/students/profile`: Retrieves logged-in candidate profile.
- `PUT /api/v1/students/profile`: Updates candidate academic, industry, and location preferences.
- `POST /api/v1/students/resume`: Multipart file upload with automated OCR text extraction.
- `GET /api/v1/students/recommendations`: Calculates real-time AI compatibility scores across available internships.
- `GET /api/v1/students/skill-gaps`: Computes missing skills and generates targeted learning path recommendations.

---

## 🚀 3. Spring Boot Allocation Engine (`smart-allocation-backend`)

### High-Scale Architecture:
- Built to handle millions of candidates using stateless JWT sessions, HikariCP connection pooling (30 connections), and JDBC batching (`batch_size=500`).
- **Deterministic Scheme Eligibility**: Validates mandatory PM Scheme age bounds (21 to 24 years) and educational qualifications.
- **Multi-Factor AI Matching**: Native Java algorithm computing skill overlap, location preference, and degree relevance.
- **Optimal Seat Allocation Engine**: Multi-threaded seat allocation optimizer, simulation dry-runs, `@Transactional` atomic publishing, and immutable audit logging.
- **20 REST Controllers**: Verified 100% working via end-to-end Python integration scripts.

---

## 🔒 4. Two-Stage Authentication & Security Architecture

```
[ Frontend Client ] 
       │ 
       ├─► Stage 1: Google OAuth 2.0 (OpenID Connect)
       │      • Google verifies user account credentials.
       │      • Issues cryptographically signed ID Token.
       │
       └─► Stage 2: SQL Database Candidate Authorization
              • Backend validates Google Token signature using official Google JWKS.
              • Extracts verified email: clean_google_email = raw_email.strip().lower()
              • Queries SQL DB: SELECT * FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))
              │
              ├─► Email Found in SQL DB -> GRANT ACCESS (JWT Issued + HTTP 200)
              └─► Email NOT in SQL DB   -> DENY ACCESS (HTTP 401: "Google account not registered")
```

### Security Rules:
1. **No Google Passwords Handled**: At no point does the application collect, transmit, or verify Gmail passwords.
2. **Strict BCrypt Hashing**: Application passwords strictly evaluate BCrypt hashes (`bcrypt.checkpw`). Arbitrary passwords (such as `"123"`) or unregistered emails are strictly rejected with `HTTP 400`.
3. **No User Enumeration**: Invalid emails, wrong passwords, and empty inputs return the identical error response: `"Invalid email or password"`.
4. **Protected Routes**: All private candidate and administrator endpoints require a valid JWT token (`HTTP 401 Unauthorized` enforced).

---

## 🗄️ 5. Relational Database Schema (13 Entities)

```
User (id, email, password_hash, role, full_name, provider, google_subject_id, avatar_url, created_at)
  ├── StudentProfile (id, user_id, phone, age, qualification, degree, branch, institution, graduation_year, cgpa, preferred_industry, preferred_role, preferred_location, work_mode, preferred_duration, resume_url, raw_resume_text, projects_summary)
  │     ├── StudentSkill (id, student_id, skill_id, proficiency_level)
  │     └── EligibilityResult (id, student_id, is_eligible, eligibility_status, age_valid, qualification_valid, checked_at)
  └── Application (id, student_id, internship_id, status, applied_at)

Company (id, name, sector, website, contact_email)
  └── Internship (id, company_id, title, description, location, work_mode, duration, stipend, deadline, positions, min_qualification, preferred_degree, min_age, max_age, is_active)
        └── InternshipSkill (id, internship_id, skill_id, is_required)

Skill (id, name, category)
AllocationRun (id, run_timestamp, status, total_candidates, total_seats, total_allocated, strategy_used, published_at, executed_by)
  └── Allocation (id, run_id, student_id, internship_id, match_score, rank_position, status)
AuditLog (id, action, performed_by, entity_type, entity_id, details, timestamp)
```

---

## 🔑 6. Active Local Server Endpoints & Credentials

### **Active Local Server URLs**
* **Frontend Portal (Home)**: [http://localhost:3000](http://localhost:3000)
* **Login Page**: [http://localhost:3000/login](http://localhost:3000/login)
* **Register Page**: [http://localhost:3000/register](http://localhost:3000/register)
* **FastAPI AI Microservice Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Spring Boot Allocation API**: [http://127.0.0.1:8080/api/internships](http://127.0.0.1:8080/api/internships)

### **Working Access Credentials**
1. **Google Sign-In**: Click **Continue with Google** at the top of the login page to authenticate with your real account (`sanjay2205e@gmail.com`).
2. **Student Demo Account**: `student@sih.gov.in` / `password123`
3. **Admin Authentication**: Configure custom admin email & password via `/admin-credentials` portal or environment variables.
4. **Custom Account**: Click **[Create Account Here](http://localhost:3000/register)** to register any new email and custom password.

---

*(Note: All code and database files remain 100% local on your machine. Nothing has been pushed to Git or GitHub.)*
