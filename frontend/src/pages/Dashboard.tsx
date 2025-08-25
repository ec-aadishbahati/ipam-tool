import React from "react";

import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export default function Dashboard() {
  const { data: supernets } = useQuery({ queryKey: ["supernets"], queryFn: async () => (await api.get("/supernets")).data });
  const { data: subnets } = useQuery({ queryKey: ["subnets"], queryFn: async () => (await api.get("/subnets")).data });
  const { data: vlans } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/vlans")).data });
  const { data: devices } = useQuery({ queryKey: ["devices"], queryFn: async () => (await api.get("/devices")).data });
  const { data: audits } = useQuery({ queryKey: ["audits"], queryFn: async () => (await api.get("/audits")).data });

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Dashboard</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat title="Supernets" value={supernets?.length ?? 0} />
        <Stat title="Subnets" value={subnets?.length ?? 0} />
        <Stat title="VLANs" value={vlans?.length ?? 0} />
        <Stat title="Devices" value={devices?.length ?? 0} />
      </div>
      <div>
        <h3 className="font-semibold mb-2">Recent Audits</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-2 border">Time</th>
                <th className="text-left p-2 border">User</th>
                <th className="text-left p-2 border">Entity</th>
                <th className="text-left p-2 border">Action</th>
              </tr>
            </thead>
            <tbody>
              {(audits ?? []).slice(0, 10).map((a: any) => (
                <tr key={a.id}>
                  <td className="p-2 border">{new Date(a.created_at).toLocaleString()}</td>
                  <td className="p-2 border">{a.user_id}</td>
                  <td className="p-2 border">
                    {a.entity_type} #{a.entity_id}
                  </td>
                  <td className="p-2 border">{a.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Stat({ title, value }: { title: string; value: number }) {
  return (
    <div className="border rounded p-4">
      <div className="text-xs uppercase text-gray-500">{title}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}
