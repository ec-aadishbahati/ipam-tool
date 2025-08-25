import React from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";

export default function IpAssignments() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["ip-assignments"], queryFn: async () => (await api.get("/ip-assignments")).data });
  const { data: subnets } = useQuery({ queryKey: ["subnets"], queryFn: async () => (await api.get("/subnets")).data });
  const { data: devices } = useQuery({ queryKey: ["devices"], queryFn: async () => (await api.get("/devices")).data });
  const [form, setForm] = useState({ subnet_id: undefined as number | undefined, device_id: undefined as number | undefined, ip_address: "", role: "" });

  const create = useMutation({
    mutationFn: async () => (await api.post("/ip-assignments", form)).data,
    onSuccess: () => {
      setForm({ subnet_id: undefined, device_id: undefined, ip_address: "", role: "" });
      qc.invalidateQueries({ queryKey: ["ip-assignments"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">IP Assignments</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <select className="border p-2 rounded" value={form.subnet_id ?? ""} onChange={(e) => setForm({ ...form, subnet_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Subnet</option>
            {(subnets ?? []).map((s: any) => (
              <option key={s.id} value={s.id}>
                {s.name} - {s.cidr}
              </option>
            ))}
          </select>
          <select className="border p-2 rounded" value={form.device_id ?? ""} onChange={(e) => setForm({ ...form, device_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Device</option>
            {(devices ?? []).map((d: any) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
          <input className="border p-2 rounded" placeholder="IP Address" value={form.ip_address} onChange={(e) => setForm({ ...form, ip_address: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Role (optional)" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
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
              <th className="text-left p-2 border">Subnet</th>
              <th className="text-left p-2 border">Device</th>
              <th className="text-left p-2 border">IP</th>
              <th className="text-left p-2 border">Role</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((a: any) => (
              <tr key={a.id}>
                <td className="p-2 border">{a.subnet_id}</td>
                <td className="p-2 border">{a.device_id}</td>
                <td className="p-2 border">{a.ip_address}</td>
                <td className="p-2 border">{a.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
