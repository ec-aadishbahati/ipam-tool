import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";

export default function VLANs() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans")).data });
  const { data: purposes } = useQuery({ queryKey: ["purposes"], queryFn: async () => (await api.get("/api/purposes")).data });
  const [form, setForm] = useState({ site: "", environment: "", vlan_id: "", name: "", purpose_id: undefined as number | undefined });

  const create = useMutation({
    mutationFn: async () =>
      (await api.post("/api/vlans", { ...form, vlan_id: form.vlan_id ? Number(form.vlan_id) : undefined, purpose_id: form.purpose_id })).data,
    onSuccess: () => {
      setForm({ site: "", environment: "", vlan_id: "", name: "", purpose_id: undefined });
      qc.invalidateQueries({ queryKey: ["vlans"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">VLANs</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <input className="border p-2 rounded" placeholder="Site" value={form.site} onChange={(e) => setForm({ ...form, site: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Environment" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })} />
          <input className="border p-2 rounded" placeholder="VLAN ID" value={form.vlan_id} onChange={(e) => setForm({ ...form, vlan_id: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="border p-2 rounded" value={form.purpose_id ?? ""} onChange={(e) => setForm({ ...form, purpose_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Purpose</option>
            {(purposes ?? []).map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create
        </button>
        {create.error && <div className="text-sm text-red-600">{getErrorMessage(create.error)}</div>}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Site</th>
              <th className="text-left p-2 border">Env</th>
              <th className="text-left p-2 border">VLAN ID</th>
              <th className="text-left p-2 border">Name</th>
              <th className="text-left p-2 border">Purpose</th>
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((v: any) => (
              <EditableRow
                key={v.id}
                entity={v}
                entityType="vlans"
                fields={[
                  { key: 'site', label: 'Site', editable: true },
                  { key: 'environment', label: 'Environment', editable: true },
                  { key: 'vlan_id', label: 'VLAN ID', type: 'number', editable: true },
                  { key: 'name', label: 'Name', editable: true },
                  { 
                    key: 'purpose_id', 
                    label: 'Purpose', 
                    type: 'select',
                    editable: true,
                    options: (purposes ?? []).map((p: any) => ({value: p.id, label: p.name})),
                    render: (value: any) => {
                      const purpose = purposes?.find((p: any) => p.id === value);
                      return purpose ? purpose.name : value;
                    }
                  },
                ]}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
