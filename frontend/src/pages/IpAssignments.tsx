import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";

export default function IpAssignments() {
  const qc = useQueryClient();
  const { data, isLoading: ipLoading, error: ipError } = useQuery({ 
    queryKey: ["ip-assignments"], 
    queryFn: async () => (await api.get("/api/ip-assignments")).data 
  });
  const { data: subnets, isLoading: subnetsLoading, error: subnetsError } = useQuery({ 
    queryKey: ["subnets"], 
    queryFn: async () => (await api.get("/api/subnets")).data 
  });
  const { data: devices, isLoading: devicesLoading, error: devicesError } = useQuery({ 
    queryKey: ["devices"], 
    queryFn: async () => (await api.get("/api/devices")).data 
  });
  const [form, setForm] = useState({ subnet_id: undefined as number | undefined, device_id: undefined as number | undefined, ip_address: "", role: "" });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/ip-assignments", form)).data,
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
        {create.error && <div className="text-sm text-red-600">{getErrorMessage(create.error)}</div>}
        {subnetsError && <div className="text-sm text-red-600">Failed to load subnets: {getErrorMessage(subnetsError, "Network error")}</div>}
        {devicesError && <div className="text-sm text-red-600">Failed to load devices: {getErrorMessage(devicesError, "Network error")}</div>}
        {ipError && <div className="text-sm text-red-600">Failed to load IP assignments: {getErrorMessage(ipError, "Network error")}</div>}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Subnet</th>
              <th className="text-left p-2 border">Device</th>
              <th className="text-left p-2 border">IP</th>
              <th className="text-left p-2 border">Role</th>
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((a: any) => (
              <EditableRow
                key={a.id}
                entity={a}
                entityType="ip-assignments"
                fields={[
                  { 
                    key: 'subnet_id', 
                    label: 'Subnet', 
                    editable: false,
                    render: (value: any) => {
                      const subnet = subnets?.find((s: any) => s.id === value);
                      return subnet ? `${subnet.name} - ${subnet.cidr}` : value;
                    }
                  },
                  { 
                    key: 'device_id', 
                    label: 'Device', 
                    type: 'select',
                    editable: true,
                    options: (devices ?? []).map((d: any) => ({value: d.id, label: d.name})),
                    render: (value: any) => {
                      const device = devices?.find((d: any) => d.id === value);
                      return device ? device.name : value;
                    }
                  },
                  { key: 'ip_address', label: 'IP', editable: true, render: (value: any) => <span className="font-mono">{value}</span> },
                  { key: 'role', label: 'Role', editable: true },
                ]}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
