import React from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";

export default function Supernets() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({ queryKey: ["supernets"], queryFn: async () => (await api.get("/supernets")).data });
  const [form, setForm] = useState({ name: "", cidr: "", site: "", environment: "" });
  const create = useMutation({
    mutationFn: async () => (await api.post("/supernets", form)).data,
    onSuccess: () => {
      setForm({ name: "", cidr: "", site: "", environment: "" });
      qc.invalidateQueries({ queryKey: ["supernets"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Supernets</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="border p-2 rounded" placeholder="CIDR 10.0.0.0/8" value={form.cidr} onChange={(e) => setForm({ ...form, cidr: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Site" value={form.site} onChange={(e) => setForm({ ...form, site: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Environment" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })} />
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create
        </button>
        {create.error && <div className="text-sm text-red-600">{(create.error as any)?.response?.data?.detail || "Error"}</div>}
      </div>

      {isLoading ? (
        <div>Loading…</div>
      ) : error ? (
        <div className="text-red-600">Failed to load</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-2 border">Name</th>
                <th className="text-left p-2 border">CIDR</th>
                <th className="text-left p-2 border">Site</th>
                <th className="text-left p-2 border">Env</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((s: any) => (
                <tr key={s.id}>
                  <td className="p-2 border">{s.name}</td>
                  <td className="p-2 border">{s.cidr}</td>
                  <td className="p-2 border">{s.site}</td>
                  <td className="p-2 border">{s.environment}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
