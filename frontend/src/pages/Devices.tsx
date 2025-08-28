import React from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";

export default function Devices() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["devices"], queryFn: async () => (await api.get("/api/devices")).data });
  const { data: vlans } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans")).data });
  const [form, setForm] = useState({ name: "", role: "", hostname: "", location: "", vlan_id: undefined as number | undefined });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/devices", form)).data,
    onSuccess: () => {
      setForm({ name: "", role: "", hostname: "", location: "", vlan_id: undefined });
      qc.invalidateQueries({ queryKey: ["devices"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Devices</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Role" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Hostname" value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <select className="border p-2 rounded" value={form.vlan_id ?? ""} onChange={(e) => setForm({ ...form, vlan_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">VLAN</option>
            {(vlans ?? []).map((v: any) => (
              <option key={v.id} value={v.id}>
                {v.vlan_id} - {v.name}
              </option>
            ))}
          </select>
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create
        </button>
        {create.error && <div className="text-sm text-red-600">{(create.error as any)?.response?.data?.detail || "Error"}</div>}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Name</th>
              <th className="text-left p-2 border">Role</th>
              <th className="text-left p-2 border">Hostname</th>
              <th className="text-left p-2 border">Location</th>
              <th className="text-left p-2 border">VLAN</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((d: any) => (
              <tr key={d.id}>
                <td className="p-2 border">{d.name}</td>
                <td className="p-2 border">{d.role}</td>
                <td className="p-2 border">{d.hostname}</td>
                <td className="p-2 border">{d.location}</td>
                <td className="p-2 border">{d.vlan_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
