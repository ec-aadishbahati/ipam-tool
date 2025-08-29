import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";

const CATEGORY_OPTIONS = [
  { value: "Controllers / Management", label: "Controllers / Management" },
  { value: "Connectivity (P2P / Links)", label: "Connectivity (P2P / Links)" },
  { value: "Data Networks", label: "Data Networks" },
  { value: "Pools & Addressing", label: "Pools & Addressing" },
  { value: "Out-of-Band", label: "Out-of-Band" },
];

export default function Purposes() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["purposes"], queryFn: async () => (await api.get("/api/purposes")).data });
  const [form, setForm] = useState({ name: "", description: "", category: "" });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/purposes", form)).data,
    onSuccess: () => {
      setForm({ name: "", description: "", category: "" });
      qc.invalidateQueries({ queryKey: ["purposes"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Purposes</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <input className="border p-2 rounded" placeholder="Purpose Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="border p-2 rounded" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
            <option value="">Select Category</option>
            {CATEGORY_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <input className="border p-2 rounded col-span-2" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
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
              <th className="text-left p-2 border">Name</th>
              <th className="text-left p-2 border">Category</th>
              <th className="text-left p-2 border">Description</th>
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((p: any) => (
              <EditableRow
                key={p.id}
                entity={p}
                entityType="purposes"
                fields={[
                  { key: 'name', label: 'Purpose Name', editable: true },
                  { key: 'category', label: 'Category', editable: true, type: 'select', options: CATEGORY_OPTIONS },
                  { key: 'description', label: 'Description', editable: true },
                ]}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
