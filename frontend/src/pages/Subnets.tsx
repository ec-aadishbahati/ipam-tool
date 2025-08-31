import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage, getErrorDetails } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";
import { Pagination } from "../components/Pagination";

export default function Subnets() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const { data: paginatedSubnets } = useQuery({ 
    queryKey: ["subnets", page], 
    queryFn: async () => (await api.get(`/api/subnets?page=${page}&limit=75`)).data 
  });
  const subnets = paginatedSubnets?.items || [];
  const { data: purposes } = useQuery({ queryKey: ["purposes"], queryFn: async () => (await api.get("/api/purposes")).data });
  const { data: vlansResponse } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans?limit=1000")).data });
  const vlans = vlansResponse?.items || [];
  const { data: supernets } = useQuery({ queryKey: ["supernets"], queryFn: async () => (await api.get("/api/supernets")).data });

  const [form, setForm] = useState({
    name: "",
    cidr: "",
    purpose_id: undefined as number | undefined,
    assigned_to: "",
    gateway_ip: "",
    vlan_id: undefined as number | undefined,
    site: "",
    environment: "",
    supernet_id: undefined as number | undefined,
    allocation_mode: "manual",
    gateway_mode: "manual",
    subnet_mask: undefined as number | undefined,
    host_count: undefined as number | undefined,
  });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/subnets", form)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["subnets"] });
      setPage(1);
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Subnets</h2>
      <div className="border rounded p-3 space-y-4">
        <div className="grid grid-cols-2 gap-2">
          <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="border p-2 rounded" value={form.supernet_id ?? ""} onChange={(e) => setForm({ ...form, supernet_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Supernet (required for auto modes)</option>
            {(supernets ?? []).map((s: any) => (
              <option key={s.id} value={s.id}>
                {s.name} - {s.cidr}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">CIDR Allocation Mode</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input type="radio" name="allocation_mode" value="manual" checked={form.allocation_mode === "manual"} onChange={(e) => setForm({ ...form, allocation_mode: e.target.value })} className="mr-2" />
              Manual CIDR
            </label>
            <label className="flex items-center">
              <input type="radio" name="allocation_mode" value="auto_mask" checked={form.allocation_mode === "auto_mask"} onChange={(e) => setForm({ ...form, allocation_mode: e.target.value })} className="mr-2" />
              Auto by Subnet Mask
            </label>
            <label className="flex items-center">
              <input type="radio" name="allocation_mode" value="auto_hosts" checked={form.allocation_mode === "auto_hosts"} onChange={(e) => setForm({ ...form, allocation_mode: e.target.value })} className="mr-2" />
              Auto by Host Count
            </label>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {form.allocation_mode === "manual" && (
            <input className="border p-2 rounded" placeholder="CIDR 10.1.0.0/24" value={form.cidr} onChange={(e) => setForm({ ...form, cidr: e.target.value })} />
          )}
          {form.allocation_mode === "auto_mask" && (
            <input className="border p-2 rounded" placeholder="Subnet mask (e.g., 24)" type="number" value={form.subnet_mask ?? ""} onChange={(e) => setForm({ ...form, subnet_mask: e.target.value ? Number(e.target.value) : undefined })} />
          )}
          {form.allocation_mode === "auto_hosts" && (
            <input className="border p-2 rounded" placeholder="Number of hosts needed" type="number" value={form.host_count ?? ""} onChange={(e) => setForm({ ...form, host_count: e.target.value ? Number(e.target.value) : undefined })} />
          )}
          <select className="border p-2 rounded" value={form.purpose_id ?? ""} onChange={(e) => setForm({ ...form, purpose_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">Purpose</option>
            {(purposes ?? []).map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <input className="border p-2 rounded" placeholder="Assigned To" value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Gateway Assignment</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input type="radio" name="gateway_mode" value="manual" checked={form.gateway_mode === "manual"} onChange={(e) => setForm({ ...form, gateway_mode: e.target.value })} className="mr-2" />
              Manual Gateway
            </label>
            <label className="flex items-center">
              <input type="radio" name="gateway_mode" value="auto_first" checked={form.gateway_mode === "auto_first"} onChange={(e) => setForm({ ...form, gateway_mode: e.target.value })} className="mr-2" />
              Auto First IP
            </label>
            <label className="flex items-center">
              <input type="radio" name="gateway_mode" value="none" checked={form.gateway_mode === "none"} onChange={(e) => setForm({ ...form, gateway_mode: e.target.value })} className="mr-2" />
              No Gateway
            </label>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {form.gateway_mode === "manual" && (
            <input className="border p-2 rounded" placeholder="Gateway IP (optional)" value={form.gateway_ip} onChange={(e) => setForm({ ...form, gateway_ip: e.target.value })} />
          )}
          <select className="border p-2 rounded" value={form.vlan_id ?? ""} onChange={(e) => setForm({ ...form, vlan_id: e.target.value ? Number(e.target.value) : undefined })}>
            <option value="">VLAN (optional)</option>
            {(vlans ?? []).map((v: any) => (
              <option key={v.id} value={v.id}>
                {v.vlan_id} - {v.name}
              </option>
            ))}
          </select>
          <input className="border p-2 rounded" placeholder="Site" value={form.site} onChange={(e) => setForm({ ...form, site: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Environment" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })} />
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create
        </button>
        {create.error && (
          <div className="text-sm text-red-600">
            {getErrorDetails(create.error).map((err: any, idx: number) => (
              <div key={idx}>{err}</div>
            ))}
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-xs border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Name</th>
              <th className="text-left p-2 border">CIDR</th>
              <th className="text-left p-2 border">Utilization</th>
              <th className="text-left p-2 border">Available IPs</th>
              <th className="text-left p-2 border">Valid IP Range</th>
              <th className="text-left p-2 border">Gateway</th>
              <th className="text-left p-2 border">Purpose</th>
              <th className="text-left p-2 border">VLAN</th>
              <th className="text-left p-2 border">Site</th>
              <th className="text-left p-2 border">Env</th>
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(subnets ?? []).map((s: any) => (
              <EditableRow
                key={s.id}
                entity={s}
                entityType="subnets"
                fields={[
                  { key: 'name', label: 'Name', editable: true },
                  { key: 'cidr', label: 'CIDR', editable: false, render: (value: any) => <span className="font-mono">{value}</span> },
                  { 
                    key: 'utilization_percentage', 
                    label: 'Utilization', 
                    editable: false,
                    render: (value: any) => (
                      <span className={`px-2 py-1 rounded text-xs ${value > 80 ? 'bg-red-100 text-red-800' : value > 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                        {value?.toFixed(1)}%
                      </span>
                    )
                  },
                  { 
                    key: 'available_ips', 
                    label: 'Available IPs', 
                    editable: false,
                    render: (value: any) => (
                      <span className={`px-2 py-1 rounded text-xs ${value === 0 ? 'bg-red-100 text-red-800' : value < 10 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                        {value}
                      </span>
                    )
                  },
                  { key: 'first_ip', label: 'Valid IP Range', editable: false, render: (value: any, entity: any) => `${value} - ${entity.last_ip}` },
                  { 
                    key: 'gateway_ip', 
                    label: 'Gateway', 
                    editable: false,
                    render: (value: any, entity: any) => {
                      if (entity.gateway_mode === 'none') return '-';
                      if (entity.gateway_mode === 'auto_first' && entity.first_ip) return entity.first_ip;
                      return value || '-';
                    }
                  },
                  { 
                    key: 'purpose_id', 
                    label: 'Purpose', 
                    type: 'select',
                    editable: true,
                    options: (purposes ?? []).map((p: any) => ({value: p.id, label: p.name})),
                    render: (value: any) => {
                      const purpose = purposes?.find((p: any) => p.id === value);
                      return purpose ? `${purpose.name}${purpose.category ? ` (${purpose.category.name})` : ''}` : value;
                    }
                  },
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
                  { key: 'site', label: 'Site', editable: true },
                  { key: 'environment', label: 'Environment', editable: true },
                ]}
              />
            ))}
          </tbody>
        </table>
      </div>
      {paginatedSubnets && (
        <Pagination
          currentPage={page}
          totalPages={paginatedSubnets.total_pages}
          onPageChange={setPage}
          totalItems={paginatedSubnets.total}
          itemsPerPage={75}
        />
      )}
    </div>
  );
}
