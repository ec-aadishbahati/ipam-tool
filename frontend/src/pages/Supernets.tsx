
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { api } from "../lib/api";
import { useNavigate } from "react-router-dom";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";
import { AllocationBar } from "../components/AllocationBar";

export default function Supernets() {
  const qc = useQueryClient();
  const nav = useNavigate();
  const { data, isLoading, error } = useQuery({ queryKey: ["supernets"], queryFn: async () => (await api.get("/api/supernets")).data });
  const [form, setForm] = useState({ name: "", cidr: "", site: "", environment: "" });
  const [expandedSupernets, setExpandedSupernets] = useState<Set<number>>(new Set());
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

  const toggleExpanded = (supernetId: number) => {
    const newExpanded = new Set(expandedSupernets);
    if (newExpanded.has(supernetId)) {
      newExpanded.delete(supernetId);
    } else {
      newExpanded.add(supernetId);
    }
    setExpandedSupernets(newExpanded);
  };

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
          <table className="min-w-full text-xs border">
            <thead className="bg-gray-50">
              <tr>
                 <th className="text-left p-2 border">Name</th>
                 <th className="text-left p-2 border">CIDR</th>
                 <th className="text-left p-2 border">Allocation</th>
                 <th className="text-left p-2 border">Available IPs</th>
                 <th className="text-left p-2 border">Site</th>
                 <th className="text-left p-2 border">Env</th>
                 <th className="text-left p-2 border">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((s: any) => (
                <>
                  <EditableRow
                    key={s.id}
                    entity={s}
                    entityType="supernets"
                    fields={[
                      { 
                        key: 'name', 
                        label: 'Name', 
                        editable: true,
                        render: (value: any, entity: any) => (
                          <div className="flex items-center gap-2">
                            {entity.subnets && entity.subnets.length > 0 && (
                              <button
                                onClick={() => toggleExpanded(entity.id)}
                                className="text-gray-500 hover:text-gray-700"
                              >
                                {expandedSupernets.has(entity.id) ? '▼' : '▶'}
                              </button>
                            )}
                            <span>{value}</span>
                          </div>
                        )
                      },
                      { key: 'cidr', label: 'CIDR', editable: false, render: (value: any) => <span className="font-mono">{value}</span> },
                      { 
                        key: 'utilization_percentage', 
                        label: 'Allocation', 
                        editable: false,
                        render: (value: any) => (
                          <div className="flex flex-col gap-1">
                            <AllocationBar utilizationPercentage={value} showPercentage={false} />
                            <span className={`px-2 py-1 rounded text-xs self-start ${value > 80 ? 'bg-red-100 text-red-800' : value > 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                              {value?.toFixed(1)}%
                            </span>
                          </div>
                        )
                      },
                      { 
                        key: 'available_ips', 
                        label: 'Available IPs', 
                        editable: false,
                        render: (value: any) => (
                          <span className={`px-2 py-1 rounded text-xs ${value === 0 ? 'bg-red-100 text-red-800' : value < 100 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                            {value?.toLocaleString()}
                          </span>
                        )
                      },
                      { key: 'site', label: 'Site', editable: true },
                      { key: 'environment', label: 'Environment', editable: true },
                    ]}
                  />
                  {expandedSupernets.has(s.id) && s.subnets && s.subnets.length > 0 && (
                    <tr>
                      <td colSpan={7} className="p-0 border">
                        <div className="bg-gray-50 p-3">
                          <h4 className="text-sm font-medium mb-2">Allocated Subnets:</h4>
                          <div className="space-y-1">
                            {s.subnets.map((subnet: any) => (
                              <div key={subnet.id} className="flex items-center gap-4 text-xs bg-white p-2 rounded border">
                                <span className="font-mono text-blue-600 min-w-[7rem]">{subnet.cidr}</span>
                                <span className="text-gray-700 min-w-[6rem]">{subnet.name || 'Unnamed'}</span>
                                <div className="flex-1 min-w-[8rem]">
                                  <AllocationBar utilizationPercentage={subnet.utilization_percentage} />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
