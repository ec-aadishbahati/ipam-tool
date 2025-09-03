import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { BulkActionTable } from "../components/BulkActionTable";
import { Pagination } from "../components/Pagination";

export default function Devices() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const { data: paginatedDevices } = useQuery({ 
    queryKey: ["devices", page], 
    queryFn: async () => (await api.get(`/api/devices?page=${page}&limit=75`)).data 
  });
  const data = paginatedDevices?.items || [];
  const { data: vlansResponse } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans?limit=1000")).data });
  const vlans = vlansResponse?.items || [];
  const { data: racks } = useQuery({ queryKey: ["racks"], queryFn: async () => (await api.get("/api/racks")).data });
  const [form, setForm] = useState({ name: "", role: "", hostname: "", location: "", vendor: "", serial_number: "", vlan_id: undefined as number | undefined, rack_id: undefined as number | undefined, rack_position: undefined as number | undefined });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/devices", form)).data,
    onSuccess: () => {
      setForm({ name: "", role: "", hostname: "", location: "", vendor: "", serial_number: "", vlan_id: undefined, rack_id: undefined, rack_position: undefined });
      qc.invalidateQueries({ queryKey: ["devices"] });
      setPage(1);
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

      <div className="flex gap-2 mb-4">
        <button
          onClick={async () => {
            try {
              const response = await api.get('/api/devices/export/csv', {
                responseType: 'blob'
              });
              const blob = new Blob([response.data], { type: 'text/csv' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'devices.csv';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);
            } catch (error: any) {
              const errorMsg = error.response?.data?.detail || error.message || 'Export failed';
              alert(`Export failed: ${errorMsg}`);
            }
          }}
          className="bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700"
        >
          Export CSV
        </button>
        <button
          onClick={async () => {
            try {
              const response = await api.get('/api/devices/import/template', {
                responseType: 'blob'
              });
              const blob = new Blob([response.data], { type: 'text/csv' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'devices-template.csv';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);
            } catch (error: any) {
              const errorMsg = error.response?.data?.detail || error.message || 'Template download failed';
              alert(`Download failed: ${errorMsg}`);
            }
          }}
          className="bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700"
        >
          Download Import Template
        </button>
      </div>

      <BulkActionTable
        data={data ?? []}
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
      {paginatedDevices && (
        <Pagination
          currentPage={page}
          totalPages={paginatedDevices.total_pages}
          onPageChange={setPage}
          totalItems={paginatedDevices.total}
          itemsPerPage={75}
        />
      )}
    </div>
  );
}
