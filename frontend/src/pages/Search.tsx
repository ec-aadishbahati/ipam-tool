import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

const CATEGORY_OPTIONS = [
  { value: "Controllers / Management", label: "Controllers / Management" },
  { value: "Connectivity (P2P / Links)", label: "Connectivity (P2P / Links)" },
  { value: "Data Networks", label: "Data Networks" },
  { value: "Pools & Addressing", label: "Pools & Addressing" },
  { value: "Out-of-Band", label: "Out-of-Band" },
];

export default function SearchPage() {
  const [q, setQ] = useState({ 
    site: "", 
    environment: "", 
    text: "", 
    purpose_id: "", 
    category: "",
    vlan_id: "", 
    assigned_to: "", 
    has_gateway: "" 
  });
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [importType, setImportType] = useState<'subnets' | 'devices'>('subnets');
  const { data: purposes } = useQuery({ queryKey: ["purposes"], queryFn: async () => (await api.get("/api/purposes")).data });
  const { data: vlans } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans")).data });
  
  const { data, refetch, isFetching } = useQuery({
    queryKey: ["search", q],
    queryFn: async () => (await api.get("/api/search", { params: q })).data,
    enabled: false,
  });

  const handleCsvImport = async () => {
    if (!csvFile) return;
    
    const formData = new FormData();
    formData.append('file', csvFile);
    
    const endpoint = importType === 'devices' ? '/api/devices/import/csv' : '/api/subnets/import/csv';
    const entityName = importType === 'devices' ? 'devices' : 'subnets';
    
    try {
      const response = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(`Import successful! ${response.data.imported_count} ${entityName} imported.`);
      if (response.data.errors.length > 0) {
        alert(`Errors: ${response.data.errors.join('\n')}`);
      }
      setCsvFile(null);
    } catch (error: any) {
      alert(`Import failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Advanced Search</h2>
      <div className="grid grid-cols-4 gap-2">
        <input className="border rounded p-2" placeholder="Site" value={q.site} onChange={(e) => setQ({ ...q, site: e.target.value })} />
        <input className="border rounded p-2" placeholder="Environment" value={q.environment} onChange={(e) => setQ({ ...q, environment: e.target.value })} />
        <input className="border rounded p-2" placeholder="Text Search" value={q.text} onChange={(e) => setQ({ ...q, text: e.target.value })} />
        <input className="border rounded p-2" placeholder="Assigned To" value={q.assigned_to} onChange={(e) => setQ({ ...q, assigned_to: e.target.value })} />
        <select className="border rounded p-2" value={q.purpose_id} onChange={(e) => setQ({ ...q, purpose_id: e.target.value })}>
          <option value="">Any Purpose</option>
          {(purposes ?? []).map((p: any) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <select className="border rounded p-2" value={q.category} onChange={(e) => setQ({ ...q, category: e.target.value })}>
          <option value="">Any Category</option>
          {CATEGORY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <select className="border rounded p-2" value={q.vlan_id} onChange={(e) => setQ({ ...q, vlan_id: e.target.value })}>
          <option value="">Any VLAN</option>
          {(vlans ?? []).map((v: any) => <option key={v.id} value={v.id}>{v.vlan_id} - {v.name}</option>)}
        </select>
        <select className="border rounded p-2" value={q.has_gateway} onChange={(e) => setQ({ ...q, has_gateway: e.target.value })}>
          <option value="">Any Gateway</option>
          <option value="true">Has Gateway</option>
          <option value="false">No Gateway</option>
        </select>
      </div>
      <div className="flex gap-2 flex-wrap">
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => refetch()} disabled={isFetching}>
          Search
        </button>
        <div className="flex items-center gap-2">
          <select 
            className="border rounded p-2" 
            value={importType} 
            onChange={(e) => setImportType(e.target.value as 'subnets' | 'devices')}
          >
            <option value="subnets">Subnets</option>
            <option value="devices">Devices</option>
          </select>
          <button 
            className="border rounded px-3 py-2" 
            onClick={() => window.open(`${import.meta.env.VITE_API_BASE || ''}/api/${importType}/import/template`, '_blank')}
          >
            Download {importType === 'devices' ? 'Device' : 'Subnet'} Template
          </button>
        </div>
        <div className="flex items-center gap-2">
          <input 
            type="file" 
            accept=".csv" 
            onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
            className="border rounded p-2"
          />
          <button 
            className="bg-blue-600 text-white rounded px-3 py-2" 
            onClick={handleCsvImport}
            disabled={!csvFile}
          >
            Import {importType === 'devices' ? 'Device' : 'Subnet'} CSV
          </button>
        </div>
        <button 
          className="bg-green-600 text-white rounded px-3 py-2" 
          onClick={() => window.open(`${import.meta.env.VITE_API_BASE || ''}/api/export/all`, '_blank')}
        >
          Export All Data
        </button>
      </div>

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Result title="Supernets" rows={data.supernets} cols={["name", "cidr", "site", "environment"]} />
          <Result title="Subnets" rows={data.subnets} cols={["name", "cidr", "site", "environment"]} />
          <Result title="Devices" rows={data.devices} cols={["name", "hostname", "location"]} />
          <Result title="VLANs" rows={data.vlans} cols={["site", "environment", "vlan_id", "name"]} />
        </div>
      )}
    </div>
  );
}

function Result({ title, rows, cols }: { title: string; rows: any[]; cols: string[] }) {
  return (
    <div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm border">
          <thead className="bg-gray-50">
            <tr>
              {cols.map((c) => (
                <th key={c} className="text-left p-2 border">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(rows ?? []).map((r: any, idx: number) => (
              <tr key={idx}>
                {cols.map((c) => (
                  <td key={c} className="p-2 border">
                    {r[c]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
