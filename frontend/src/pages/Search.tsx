import React from "react";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export default function SearchPage() {
  const [q, setQ] = useState({ site: "", environment: "", text: "" });
  const { data, refetch, isFetching } = useQuery({
    queryKey: ["search", q],
    queryFn: async () => (await api.get("/search", { params: q })).data,
    enabled: false,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Search</h2>
      <div className="grid grid-cols-3 gap-2">
        <input className="border rounded p-2" placeholder="Site" value={q.site} onChange={(e) => setQ({ ...q, site: e.target.value })} />
        <input className="border rounded p-2" placeholder="Environment" value={q.environment} onChange={(e) => setQ({ ...q, environment: e.target.value })} />
        <input className="border rounded p-2" placeholder="Text" value={q.text} onChange={(e) => setQ({ ...q, text: e.target.value })} />
      </div>
      <button className="bg-black text-white rounded px-3 py-2" onClick={() => refetch()} disabled={isFetching}>
        Run Search
      </button>

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
