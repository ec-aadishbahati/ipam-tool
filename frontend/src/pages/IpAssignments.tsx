import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { BulkActionTable } from "../components/BulkActionTable";
import { Pagination } from "../components/Pagination";

export default function IpAssignments() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const { data: paginatedIpAssignments, isLoading: ipLoading, error: ipError } = useQuery({ 
    queryKey: ["ip-assignments", page], 
    queryFn: async () => (await api.get(`/api/ip-assignments?page=${page}&limit=75`)).data 
  });
  const data = paginatedIpAssignments?.items || [];
  const { data: availableSubnets, isLoading: availableSubnetsLoading, error: availableSubnetsError } = useQuery({ 
    queryKey: ["subnets-available"], 
    queryFn: async () => (await api.get("/api/subnets/available")).data 
  });
  const { data: allSubnetsResponse, isLoading: allSubnetsLoading, error: allSubnetsError } = useQuery({ 
    queryKey: ["subnets-all"], 
    queryFn: async () => (await api.get("/api/subnets?page=1&limit=100")).data 
  });
  const allSubnets = allSubnetsResponse?.items || [];
  const { data: devicesResponse, isLoading: devicesLoading, error: devicesError } = useQuery({ 
    queryKey: ["devices"], 
    queryFn: async () => (await api.get("/api/devices?page=1&limit=100")).data 
  });
  const devices = devicesResponse?.items || [];
  const [form, setForm] = useState({ subnet_id: undefined as number | undefined, device_id: undefined as number | undefined, ip_address: "", role: "", interface: "" });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/ip-assignments", form)).data,
    onSuccess: () => {
      setForm({ subnet_id: undefined, device_id: undefined, ip_address: "", role: "", interface: "" });
      qc.invalidateQueries({ queryKey: ["ip-assignments"] });
      setPage(1);
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">IP Assignments</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <select className="border p-2 rounded" value={form.subnet_id ?? ""} onChange={(e) => setForm({ ...form, subnet_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Subnet</option>
            {(availableSubnets ?? []).map((s: any) => (
              <option key={s.id} value={s.id}>
                {s.name} - {s.cidr} ({s.available_ips} available)
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
          <input className="border p-2 rounded" placeholder="Interface (optional)" value={form.interface} onChange={(e) => setForm({ ...form, interface: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Role (optional)" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create
        </button>
        {create.error && <div className="text-sm text-red-600">{getErrorMessage(create.error)}</div>}
        {availableSubnetsError && <div className="text-sm text-red-600">Failed to load available subnets: {getErrorMessage(availableSubnetsError, "Network error")}</div>}
        {allSubnetsError && <div className="text-sm text-red-600">Failed to load subnets: {getErrorMessage(allSubnetsError, "Network error")}</div>}
        {devicesError && <div className="text-sm text-red-600">Failed to load devices: {getErrorMessage(devicesError, "Network error")}</div>}
        {ipError && <div className="text-sm text-red-600">Failed to load IP assignments: {getErrorMessage(ipError, "Network error")}</div>}
      </div>

      <div className="flex gap-2 mb-4">
        <button
          onClick={async () => {
            try {
              const response = await api.get('/api/ip-assignments/export/csv', {
                responseType: 'blob'
              });
              const blob = new Blob([response.data], { type: 'text/csv' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'ip-assignments.csv';
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
              const response = await api.get('/api/ip-assignments/import/template', {
                responseType: 'blob'
              });
              const blob = new Blob([response.data], { type: 'text/csv' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'ip-assignments-template.csv';
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
        <label className="bg-orange-600 text-white px-3 py-2 rounded text-sm hover:bg-orange-700 cursor-pointer">
          Import CSV
          <input
            type="file"
            accept=".csv"
            className="hidden"
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (file) {
                const formData = new FormData();
                formData.append('file', file);
                try {
                  const response = await api.post('/api/ip-assignments/import/csv', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                  });
                  alert(`Import successful: ${response.data.imported_count} IP assignments imported`);
                  qc.invalidateQueries({ queryKey: ["ip-assignments"] });
                } catch (error: any) {
                  const errorMsg = error.response?.data?.detail || error.message || 'Import failed';
                  alert(`Import failed: ${errorMsg}`);
                }
              }
            }}
          />
        </label>
      </div>

      <BulkActionTable
        data={data ?? []}
        entityType="ip-assignments"
        fields={[
          { 
            key: 'subnet_id', 
            label: 'Subnet', 
            editable: false,
            render: (value: any) => {
              const subnet = allSubnets?.find((s: any) => s.id === value);
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
          { 
            key: 'hostname', 
            label: 'Hostname', 
            editable: false,
            render: (value: any, entity: any) => {
              const device = devices?.find((d: any) => d.id === entity.device_id);
              return device?.hostname || '-';
            }
          },
          { key: 'ip_address', label: 'IP', editable: true, render: (value: any) => <span className="font-mono">{value}</span> },
          { key: 'interface', label: 'Interface', editable: true },
          { key: 'role', label: 'Role', editable: true },
        ]}
      />
      {paginatedIpAssignments && (
        <Pagination
          currentPage={page}
          totalPages={paginatedIpAssignments.total_pages}
          onPageChange={setPage}
          totalItems={paginatedIpAssignments.total}
          itemsPerPage={75}
        />
      )}
    </div>
  );
}
