import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";

export default function Devices() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["devices"], queryFn: async () => (await api.get("/api/devices")).data });
  const { data: vlans } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans")).data });
  const { data: racks } = useQuery({ queryKey: ["racks"], queryFn: async () => (await api.get("/api/racks")).data });
  const [form, setForm] = useState({ name: "", role: "", hostname: "", location: "", vendor: "", serial_number: "", vlan_id: undefined as number | undefined, rack_id: undefined as number | undefined, rack_position: undefined as number | undefined });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/devices", form)).data,
    onSuccess: () => {
      setForm({ name: "", role: "", hostname: "", location: "", vendor: "", serial_number: "", vlan_id: undefined, rack_id: undefined, rack_position: undefined });
      qc.invalidateQueries({ queryKey: ["devices"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Devices</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-3 gap-2">
          <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Role" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Hostname" value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Vendor" value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Serial Number" value={form.serial_number} onChange={(e) => setForm({ ...form, serial_number: e.target.value })} />
          <select className="border p-2 rounded" value={form.vlan_id ?? ""} onChange={(e) => setForm({ ...form, vlan_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">VLAN</option>
            {(vlans ?? []).map((v: any) => (
              <option key={v.id} value={v.id}>
                {v.vlan_id} - {v.name}
              </option>
            ))}
          </select>
          <select className="border p-2 rounded" value={form.rack_id ?? ""} onChange={(e) => setForm({ ...form, rack_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Rack</option>
            {(racks ?? []).map((r: any) => (
              <option key={r.id} value={r.id}>
                {r.aisle}-{r.rack_number}
              </option>
            ))}
          </select>
          <input className="border p-2 rounded" type="number" placeholder="Rack Position (U)" value={form.rack_position ?? ""} onChange={(e) => setForm({ ...form, rack_position: e.target.value ? Number(e.target.value) : undefined })} />
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create
        </button>
        {create.error && <div className="text-sm text-red-600">{getErrorMessage(create.error)}</div>}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-xs border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Name</th>
              <th className="text-left p-2 border">Role</th>
              <th className="text-left p-2 border">Hostname</th>
              <th className="text-left p-2 border">Location</th>
              <th className="text-left p-2 border">Vendor</th>
              <th className="text-left p-2 border">Serial Number</th>
              <th className="text-left p-2 border">VLAN</th>
              <th className="text-left p-2 border">Rack</th>
              <th className="text-left p-2 border">Position</th>
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((d: any) => (
              <EditableRow
                key={d.id}
                entity={d}
                entityType="devices"
                fields={[
                  { key: 'name', label: 'Name', editable: true },
                  { key: 'role', label: 'Role', editable: true },
                  { key: 'hostname', label: 'Hostname', editable: true },
                  { key: 'location', label: 'Location', editable: true },
                  { key: 'vendor', label: 'Vendor', editable: true },
                  { key: 'serial_number', label: 'Serial Number', editable: true },
                  { 
                    key: 'vlan_id', 
                    label: 'VLAN', 
                    type: 'select',
                    editable: true,
                    options: (vlans ?? []).map((v: any) => ({value: v.id, label: `${v.vlan_id} - ${v.name}`})),
                    render: (value: any) => {
                      const vlan = vlans?.find((v: any) => v.id === value);
                      return vlan ? `${vlan.vlan_id} - ${vlan.name}` : value;
                    }
                  },
                  { 
                    key: 'rack_id', 
                    label: 'Rack', 
                    type: 'select',
                    editable: true,
                    options: (racks ?? []).map((r: any) => ({value: r.id, label: `${r.aisle}-${r.rack_number}`})),
                    render: (value: any) => {
                      const rack = racks?.find((r: any) => r.id === value);
                      return rack ? `${rack.aisle}-${rack.rack_number}` : '';
                    }
                  },
                  { key: 'rack_position', label: 'Position', type: 'number', editable: true, render: (value: any) => value ? `${value}U` : '' },
                ]}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
