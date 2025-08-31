import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "../components/EditableRow";

export default function Racks() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["racks"], queryFn: async () => (await api.get("/api/racks")).data });
  const [form, setForm] = useState({ 
    aisle: "", 
    rack_number: "", 
    position_count: 42, 
    power_type: "", 
    power_capacity: "", 
    cooling_type: "", 
    location: "", 
    notes: "" 
  });

  const create = useMutation({
    mutationFn: async () => (await api.post("/api/racks", form)).data,
    onSuccess: () => {
      setForm({ aisle: "", rack_number: "", position_count: 42, power_type: "", power_capacity: "", cooling_type: "", location: "", notes: "" });
      qc.invalidateQueries({ queryKey: ["racks"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Racks</h2>
      <div className="border rounded p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <input className="border p-2 rounded" placeholder="Aisle" value={form.aisle} onChange={(e) => setForm({ ...form, aisle: e.target.value })} />
          <input className="border p-2 rounded" placeholder="Rack Number" value={form.rack_number} onChange={(e) => setForm({ ...form, rack_number: e.target.value })} />
          <input className="border p-2 rounded" type="number" placeholder="Position Count" value={form.position_count} onChange={(e) => setForm({ ...form, position_count: Number(e.target.value) })} />
          <select className="border p-2 rounded" value={form.power_type} onChange={(e) => setForm({ ...form, power_type: e.target.value })}>
            <option value="">Power Type</option>
            <option value="single-phase">Single Phase</option>
            <option value="three-phase">Three Phase</option>
            <option value="dc">DC Power</option>
          </select>
          <input className="border p-2 rounded" placeholder="Power Capacity (e.g., 20A 208V)" value={form.power_capacity} onChange={(e) => setForm({ ...form, power_capacity: e.target.value })} />
          <select className="border p-2 rounded" value={form.cooling_type} onChange={(e) => setForm({ ...form, cooling_type: e.target.value })}>
            <option value="">Cooling Type</option>
            <option value="air">Air Cooling</option>
            <option value="liquid">Liquid Cooling</option>
            <option value="hybrid">Hybrid Cooling</option>
          </select>
          <input className="border p-2 rounded" placeholder="Location (Building/Floor/Room)" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <textarea className="border p-2 rounded col-span-2" placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
        <button className="bg-black text-white rounded px-3 py-2" onClick={() => create.mutate()} disabled={create.isPending}>
          Create Rack
        </button>
        {create.error && <div className="text-sm text-red-600">{getErrorMessage(create.error)}</div>}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-xs border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">Aisle</th>
              <th className="text-left p-2 border">Rack #</th>
              <th className="text-left p-2 border">Positions</th>
              <th className="text-left p-2 border">Power Type</th>
              <th className="text-left p-2 border">Power Capacity</th>
              <th className="text-left p-2 border">Cooling</th>
              <th className="text-left p-2 border">Location</th>
              <th className="text-left p-2 border">Notes</th>
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((r: any) => (
              <EditableRow
                key={r.id}
                entity={r}
                entityType="racks"
                fields={[
                  { key: 'aisle', label: 'Aisle', editable: true },
                  { key: 'rack_number', label: 'Rack #', editable: true },
                  { key: 'position_count', label: 'Positions', type: 'number', editable: true },
                  { 
                    key: 'power_type', 
                    label: 'Power Type', 
                    type: 'select',
                    editable: true,
                    options: [
                      {value: 'single-phase', label: 'Single Phase'},
                      {value: 'three-phase', label: 'Three Phase'},
                      {value: 'dc', label: 'DC Power'}
                    ]
                  },
                  { key: 'power_capacity', label: 'Power Capacity', editable: true },
                  { 
                    key: 'cooling_type', 
                    label: 'Cooling', 
                    type: 'select',
                    editable: true,
                    options: [
                      {value: 'air', label: 'Air Cooling'},
                      {value: 'liquid', label: 'Liquid Cooling'},
                      {value: 'hybrid', label: 'Hybrid Cooling'}
                    ]
                  },
                  { key: 'location', label: 'Location', editable: true },
                  { key: 'notes', label: 'Notes', editable: true },
                ]}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
