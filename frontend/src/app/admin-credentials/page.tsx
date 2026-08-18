"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { ShieldCheck, Lock, Mail, CheckCircle2, AlertCircle, RefreshCw, Key, ArrowRight, FileText, Server, Trash2 } from "lucide-react";

export default function AdminCredentialsDocPage() {
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [statusData, setStatusData] = useState<any>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingEmail, setDeletingEmail] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadStatus = async () => {
    setLoadingStatus(true);
    try {
      const data = await fetchApi("/admin/credentials/status");
      setStatusData(data);
    } catch (err: any) {
      console.error("Failed to load admin credential status:", err);
    } finally {
      setLoadingStatus(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleDeleteAdmin = async (emailToDelete: string) => {
    setSuccessMsg(null);
    setErrorMsg(null);

    if (!confirm(`Are you sure you want to delete Admin account '${emailToDelete}'? This will permanently delete its email and stored password from the backend database.`)) {
      return;
    }

    setDeletingEmail(emailToDelete);

    try {
      await fetchApi(`/admin/credentials/delete?email=${encodeURIComponent(emailToDelete)}`, {
        method: "DELETE"
      });
      setSuccessMsg(`Successfully deleted Admin account '${emailToDelete}' and purged credentials from database.`);
      await loadStatus();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to delete Admin account.");
    } finally {
      setDeletingEmail(null);
    }
  };

  const handleSaveCredentials = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    setErrorMsg(null);

    if (!adminEmail || !adminEmail.includes("@")) {
      setErrorMsg("Please enter a valid Admin email address (e.g. admin@pminternship.gov.in).");
      return;
    }

    if (!adminPassword || adminPassword.length < 6) {
      setErrorMsg("Password must be at least 6 characters long.");
      return;
    }

    if (adminPassword !== confirmPassword) {
      setErrorMsg("Passwords do not match. Please re-enter passwords.");
      return;
    }

    setSaving(true);

    try {
      const res = await fetchApi("/admin/credentials/update", {
        method: "POST",
        body: JSON.stringify({
          admin_email: adminEmail.trim().toLowerCase(),
          admin_password: adminPassword.trim()
        })
      });

      setSuccessMsg(`Credentials saved! ONLY '${res.admin_email}' with your typed password can access the Admin Portal.`);
      setAdminEmail("");
      setAdminPassword("");
      setConfirmPassword("");
      await loadStatus();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to update admin credentials.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Page Header */}
      <div className="bg-[#002147] text-white rounded-xl p-6 sm:p-8 shadow-md border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-6 h-6 text-amber-400 shrink-0" />
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight">Admin Credentials & Authorization Portal</h1>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Backend Security Documentation & Single/Multi Admin Access Control Management
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <Link
            href="/login"
            className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold shadow-sm transition-colors flex items-center space-x-1"
          >
            <span>Go to Login Page</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Typable Space for Admin Email & Password */}
        <div className="lg:col-span-7 space-y-6">
          
          <div className="bg-white border border-slate-300 rounded-xl p-6 shadow-sm space-y-6">
            
            <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-[#002147] flex items-center space-x-2">
                  <Key className="w-4 h-4 text-blue-700" />
                  <span>Configure Admin Portal Credentials</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Type your Admin Email and Password below. Once saved, ONLY this email and password will be granted Admin Portal access.
                </p>
              </div>
            </div>

            {successMsg && (
              <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-300 text-xs text-emerald-900 font-medium flex items-start space-x-2 animate-in fade-in">
                <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                <span>{successMsg}</span>
              </div>
            )}

            {errorMsg && (
              <div className="p-4 rounded-lg bg-red-50 border border-red-300 text-xs text-red-900 font-medium flex items-start space-x-2 animate-in fade-in">
                <AlertCircle className="w-4 h-4 text-red-700 shrink-0 mt-0.5" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Typable Space Form */}
            <form onSubmit={handleSaveCredentials} autoComplete="off" className="space-y-4 text-xs">
              
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Admin Email Address <span className="text-red-600">*</span>
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="email"
                    required
                    autoComplete="off"
                    value={adminEmail}
                    onChange={(e) => setAdminEmail(e.target.value)}
                    placeholder="Enter Admin Email Address"
                    className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:border-blue-700 font-medium"
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  This exact email will be assigned Admin privileges in PostgreSQL/SQLite database.
                </p>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  New Admin Password <span className="text-red-600">*</span>
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    autoComplete="new-password"
                    value={adminPassword}
                    onChange={(e) => setAdminPassword(e.target.value)}
                    placeholder="Enter new admin password"
                    className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-16 py-2 text-slate-900 focus:border-blue-700 font-medium"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 text-[11px] font-semibold text-slate-500 hover:text-slate-800"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Confirm Admin Password <span className="text-red-600">*</span>
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter admin password to confirm"
                    className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:border-blue-700 font-medium"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="w-full py-2.5 bg-[#002147] hover:bg-[#001529] text-white font-bold text-xs rounded-lg shadow-sm transition-all flex items-center justify-center space-x-2"
                >
                  {saving ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
                      <span>Enforcing Admin Credentials in Database...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4 text-amber-400" />
                      <span>Save & Enforce Admin Portal Credentials</span>
                    </>
                  )}
                </button>
              </div>

            </form>

          </div>

        </div>

        {/* Right Column: Status Card & Backend Security Specifications */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Active Admin Accounts Card */}
          <div className="bg-slate-50 border border-slate-300 rounded-xl p-5 space-y-4 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#002147] flex items-center space-x-1.5">
                <Server className="w-4 h-4 text-emerald-700" />
                <span>Database Admin Status</span>
              </h3>
              <button
                onClick={loadStatus}
                className="text-[11px] text-blue-700 hover:underline flex items-center space-x-1 font-semibold"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Refresh</span>
              </button>
            </div>

            {loadingStatus ? (
              <div className="p-4 text-center text-xs text-slate-500">Loading active admin accounts...</div>
            ) : (
              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Access Control Mode:</span>
                  <span className="font-bold text-emerald-800 text-[11px] bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300">
                    {statusData?.access_control_mode || "Strict Database Enforcement"}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Active Authorized Admins:</span>
                  <span className="font-bold text-[#002147]">{statusData?.active_admin_count || 0} Account(s)</span>
                </div>

                <div className="space-y-2 pt-1">
                  <span className="text-slate-600 block font-semibold text-[11px]">Authorized Admin Email IDs:</span>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {statusData?.authorized_admin_emails?.length > 0 ? (
                      statusData.authorized_admin_emails.map((email: string, idx: number) => (
                        <div key={idx} className="p-3 rounded-lg bg-white border border-slate-300 space-y-1.5 shadow-xs">
                          <div className="flex items-center justify-between font-mono text-[11px] text-slate-900 font-bold border-b border-slate-100 pb-1">
                            <div className="flex items-center space-x-1">
                              <Mail className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                              <span>{email}</span>
                            </div>
                            <div className="flex items-center space-x-1.5">
                              <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-900 font-sans font-bold text-[9px]">ADMIN</span>
                              <button
                                type="button"
                                onClick={() => handleDeleteAdmin(email)}
                                disabled={deletingEmail === email}
                                className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                                title="Delete Admin Account from Database"
                              >
                                {deletingEmail === email ? (
                                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-red-600" />
                                ) : (
                                  <Trash2 className="w-3.5 h-3.5" />
                                )}
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-3 rounded bg-amber-50 border border-amber-200 text-amber-900 text-[11px]">
                        No active admin credentials configured. Type an email and password on the left to set active Admin credentials.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Backend Documentation Card */}
          <div className="bg-white border border-slate-300 rounded-xl p-5 space-y-3 shadow-sm text-xs">
            <h3 className="font-bold text-[#002147] border-b border-slate-200 pb-2 flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-blue-700" />
              <span>Backend Access Rules & Documentation</span>
            </h3>

            <ul className="space-y-2 text-slate-600 leading-relaxed list-disc pl-4 text-[11px]">
              <li>
                <strong className="text-slate-900">Strict Password Hashing:</strong> Passwords typed in the form are hashed using bcrypt/PBKDF2 (`get_password_hash`) before being saved in PostgreSQL/SQLite.
              </li>
              <li>
                <strong className="text-slate-900">Role Gating:</strong> Only users registered with `role = UserRole.ADMIN` receive Admin JWT tokens upon login.
              </li>
              <li>
                <strong className="text-slate-900">Instant Enforcement:</strong> As soon as you click <strong>Save & Enforce Admin Portal Credentials</strong>, your specified email and password become immediately active for `/admin` access.
              </li>
            </ul>
          </div>

        </div>

      </div>

    </div>
  );
}
