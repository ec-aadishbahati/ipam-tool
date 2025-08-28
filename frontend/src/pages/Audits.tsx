import React from "react";

import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export default function Audits() {
  const { data, isLoading, error } = useQuery({ queryKey: ["audits"], queryFn: async () => (await api.get("/audits")).data });

  if (isLoading) return <div>Loading…</div>;
  if (error) return <div className="text-red-600">Failed to load</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Audit Logs</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Time</th>
              <th className="text-left p-2 border">User</th>
              <th className="text-left p-2 border">Entity</th>
              <th className="text-left p-2 border">Action</th>
              <th className="text-left p-2 border">Before</th>
              <th className="text-left p-2 border">After</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((a: any) => (
              <tr key={a.id}>
                <td className="p-2 border">{new Date(a.timestamp).toLocaleString()}</td>
                <td className="p-2 border">{a.user_id}</td>
                <td className="p-2 border">
                  {a.entity_type} #{a.entity_id}
                </td>
                <td className="p-2 border">{a.action}</td>
                <td className="p-2 border whitespace-pre-wrap">{a.before ? JSON.stringify(a.before, null, 2) : ""}</td>
                <td className="p-2 border whitespace-pre-wrap">{a.after ? JSON.stringify(a.after, null, 2) : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
