
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { api } from "../lib/api";
import { useNavigate } from "react-router-dom";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";

export default function Supernets() {
  const qc = useQueryClient();
  const nav = useNavigate();
  const { data, isLoading, error } = useQuery({ queryKey: ["supernets"], queryFn: async () => (await api.get("/api/supernets")).data });
  const [form, setForm] = useState({ name: "", cidr: "", site: "", environment: "" });
  const create = useMutation({
    mutationFn: async () => (await api.post("/api/supernets", form)).data,
    onSuccess: () => {
      setForm({ name: "", cidr: "", site: "", environment: "" });
      qc.invalidateQueries({ queryKey: ["supernets"] });
    },
  });

  useEffect(() => {
    const status = (error as any)?.response?.status;
    if (status === 401) {
      nav("/login");
    }
  }, [error, nav]);

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
        {create.error && <div className="text-sm text-red-600">{getErrorMessage(create.error)}</div>}
      </div>

      {isLoading ? (
        <div>Loading…</div>
      ) : error ? (
        <div className="text-red-600">
          {(error as any)?.response?.data?.detail || (error as Error).message || "Failed to load"}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-2 border">Name</th>
                <th className="text-left p-2 border">CIDR</th>
                <th className="text-left p-2 border">Utilization</th>
                <th className="text-left p-2 border">Site</th>
                <th className="text-left p-2 border">Env</th>
                <th className="text-left p-2 border">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((s: any) => (
                <EditableRow
                  key={s.id}
                  entity={s}
                  entityType="supernets"
                  fields={[
                    { key: 'name', label: 'Name', editable: true },
                    { key: 'cidr', label: 'CIDR', editable: false, render: (value: any) => <span className="font-mono">{value}</span> },
                    { 
                      key: 'utilization_percentage', 
                      label: 'Utilization', 
                      editable: false,
                      render: (value: any) => (
                        <span className={`px-2 py-1 rounded text-sm ${value > 80 ? 'bg-red-100 text-red-800' : value > 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                          {value?.toFixed(1)}%
                        </span>
                      )
                    },
                    { key: 'site', label: 'Site', editable: true },
                    { key: 'environment', label: 'Environment', editable: true },
                  ]}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
