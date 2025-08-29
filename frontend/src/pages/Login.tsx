import React from "react";

import { useState } from "react";
import { api } from "../lib/api";
import { setTokens } from "../lib/auth";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState<string>("");
  const nav = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      const res = await api.post("/api/auth/login", { email: username, password: pw });
      setTokens(res.data.access_token, res.data.refresh_token);
      nav("/", { replace: true });
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      let msg = "Login failed";
      if (typeof detail === "string") msg = detail;
      else if (detail && typeof detail === "object") {
        if (Array.isArray(detail)) msg = detail.map((d: any) => d?.msg || JSON.stringify(d)).join("; ");
        else msg = detail?.msg || detail?.message || JSON.stringify(detail);
      }
      setErr(msg);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={onSubmit} className="w-full max-w-sm border rounded p-6 space-y-3">
        <h1 className="text-xl font-semibold">Log in</h1>
        <input className="border rounded p-2 w-full" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="border rounded p-2 w-full" type="password" placeholder="Password" value={pw} onChange={(e) => setPw(e.target.value)} />
        {err && <div className="text-sm text-red-600">{err}</div>}
        <button className="w-full bg-black text-white rounded py-2" type="submit">
          Continue
        </button>
        <div className="text-xs text-gray-500">API: {import.meta.env.VITE_API_BASE}</div>
      </form>
    </div>
  );
}
