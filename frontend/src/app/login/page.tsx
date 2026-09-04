"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Script from "next/script";
import { fetchApi, setAuthToken } from "@/lib/api";
import { Lock, Mail, Shield, User, ArrowRight, ShieldCheck, RefreshCw, AlertCircle, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [activeRole, setActiveRole] = useState<"STUDENT" | "ADMIN">("STUDENT");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const googleBtnContainerRef = useRef<HTMLDivElement>(null);

  const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "609018289565-qltf0pmrvl7hi1tbu6k445ikb6p3q4ea.apps.googleusercontent.com";

  useEffect(() => {
    const checkAndInit = () => {
      if (typeof window !== "undefined" && (window as any).google?.accounts?.id) {
        initGoogleAuth();
        return true;
      }
      return false;
    };

    if (!checkAndInit()) {
      const interval = setInterval(() => {
        if (checkAndInit()) {
          clearInterval(interval);
        }
      }, 200);
      return () => clearInterval(interval);
    }
  }, []);

  const initGoogleAuth = () => {
    if (!(window as any).google?.accounts?.id) return;

    try {
      (window as any).google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCallback,
        auto_select: false,
        cancel_on_tap_outside: true,
      });

      if (googleBtnContainerRef.current) {
        googleBtnContainerRef.current.innerHTML = "";
        (window as any).google.accounts.id.renderButton(googleBtnContainerRef.current, {
          theme: "outline",
          size: "large",
          text: "continue_with",
          shape: "rectangular",
          logo_alignment: "left",
          width: "320",
        });
      }
      setScriptLoaded(true);
    } catch (err) {
      console.error("GIS initialization error:", err);
    }
  };

  const handleGoogleCallback = async (response: any) => {
    if (!response || !response.credential) {
      setError("Google authentication was cancelled or returned no credentials.");
      return;
    }

    setGoogleLoading(true);
    setError(null);

    try {
      // Send verified ID token to backend
      const data = await fetchApi("/auth/google", {
        method: "POST",
        body: JSON.stringify({ credential: response.credential }),
      });

      setAuthToken(data.access_token);
      
      if (data.role === "ADMIN" || data.email?.toLowerCase() === "adminpminternship@gmail.com") {
        data.role = "ADMIN";
        localStorage.setItem("pm_internship_user", JSON.stringify(data));
        router.push("/admin");
      } else {
        localStorage.setItem("pm_internship_user", JSON.stringify(data));
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Google authentication failed on server verification.");
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanEmail = email.trim().toLowerCase();

    // Client-side email format verification
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(cleanEmail)) {
      setError("Invalid Email Format: Please enter a valid email address (e.g. name@domain.com)");
      return;
    }

    setLoading(true);

    try {
      const data = await fetchApi("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: cleanEmail,
          password: password,
          requested_role: activeRole
        }),
      });

      setAuthToken(data.access_token);
      localStorage.setItem("pm_internship_user", JSON.stringify(data));

      if (data.role === "ADMIN") {
        router.push("/admin");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-10">
      
      <Script
        src="https://accounts.google.com/gsi/client"
        onLoad={initGoogleAuth}
        strategy="afterInteractive"
      />

      <div className="w-full max-w-md bg-white border border-slate-300 rounded p-8 shadow-sm space-y-6">
        
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-[#002147] mx-auto font-bold">
            <ShieldCheck className="w-6 h-6 text-blue-900" />
          </div>
          <h2 className="text-xl font-bold text-[#002147]">Candidate & Administrator Login</h2>
          <p className="text-xs text-slate-600">my portfolio.com Digital Portal</p>
        </div>

        {/* 1. Official Google Identity Services Button Container */}
        <div className="space-y-2 text-center">
          <div className="flex justify-center min-h-[44px]">
            {googleLoading ? (
              <div className="w-full py-2.5 bg-slate-100 border border-slate-300 rounded text-xs font-semibold text-slate-700 flex items-center justify-center space-x-2">
                <RefreshCw className="w-4 h-4 animate-spin text-blue-700" />
                <span>Verifying Google Identity Server-Side...</span>
              </div>
            ) : (
              <div className="w-full flex justify-center">
                <div ref={googleBtnContainerRef} className="w-full flex justify-center" />
                {!scriptLoaded && (
                  <button
                    type="button"
                    onClick={initGoogleAuth}
                    className="w-full py-2.5 bg-white hover:bg-slate-50 border border-slate-300 rounded text-xs font-bold text-slate-700 flex items-center justify-center space-x-2 shadow-xs transition-colors"
                  >
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                    </svg>
                    <span>Continue with Google</span>
                  </button>
                )}
              </div>
            )}
          </div>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-[11px] uppercase">
              <span className="bg-white px-2 text-slate-500 font-semibold">Or Login with Password</span>
            </div>
          </div>
        </div>

        {/* Visible Student and Admin Portal Tags */}
        <div className="p-2.5 rounded bg-slate-50 border border-slate-200 space-y-2">
          <p className="text-[11px] font-bold text-slate-600 uppercase tracking-wider text-center">Select Portal Access</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => {
                setActiveRole("STUDENT");
                setError(null);
              }}
              className={`px-2.5 py-1.5 rounded text-xs font-bold flex items-center justify-center space-x-1.5 transition-all ${
                activeRole === "STUDENT"
                  ? "bg-[#002147] text-white border border-[#002147] shadow-xs"
                  : "bg-white text-slate-700 border border-slate-300 hover:bg-slate-100"
              }`}
            >
              <User className="w-3.5 h-3.5" />
              <span>Student Account</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setActiveRole("ADMIN");
                setError(null);
              }}
              className={`px-2.5 py-1.5 rounded text-xs font-bold flex items-center justify-center space-x-1.5 transition-all ${
                activeRole === "ADMIN"
                  ? "bg-amber-700 text-white border border-amber-800 shadow-xs"
                  : "bg-white text-slate-700 border border-slate-300 hover:bg-slate-100"
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Admin Portal</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded bg-red-50 border border-red-200 text-xs text-red-800 font-bold flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-700 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} autoComplete="off" className="space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="email"
                required
                autoComplete="off"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                className="w-full bg-white border border-slate-300 rounded pl-9 pr-3 py-2 text-slate-900 focus:border-blue-700 font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type={showPassword ? "text" : "password"}
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full bg-white border border-slate-300 rounded pl-9 pr-10 py-2 text-slate-900 focus:border-blue-700 font-medium"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 focus:outline-none"
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-[#002147] hover:bg-[#001529] text-white font-bold text-xs rounded shadow-sm transition-all flex items-center justify-center space-x-2"
          >
            <span>{loading ? "Authenticating..." : "Sign In to Portal"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-xs text-slate-600">
          New Candidate?{" "}
          <Link href="/register" className="text-blue-800 hover:underline font-bold">
            Create Account Here
          </Link>
        </p>

      </div>
    </div>
  );
}
