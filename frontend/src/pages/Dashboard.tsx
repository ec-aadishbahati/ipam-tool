import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const { data: supernets } = useQuery({ queryKey: ["supernets"], queryFn: async () => (await api.get("/api/supernets")).data });
  const { data: subnetsResponse } = useQuery({ queryKey: ["subnets"], queryFn: async () => (await api.get("/api/subnets?limit=1000")).data });
  const subnets = subnetsResponse?.items || [];
  const { data: vlansResponse } = useQuery({ queryKey: ["vlans"], queryFn: async () => (await api.get("/api/vlans?limit=1000")).data });
  const vlans = vlansResponse?.items || [];
  const { data: devicesResponse } = useQuery({ queryKey: ["devices"], queryFn: async () => (await api.get("/api/devices?limit=1000")).data });
  const devices = devicesResponse?.items || [];

  const devicesByRole = (devices ?? []).reduce((acc: any, device: any) => {
    const role = device.role || "Unassigned";
    acc[role] = (acc[role] || 0) + 1;
    return acc;
  }, {});

  const devicesByVendor = (devices ?? []).reduce((acc: any, device: any) => {
    const vendor = device.vendor || "Unknown";
    acc[vendor] = (acc[vendor] || 0) + 1;
    return acc;
  }, {});

  const roleChartData = Object.entries(devicesByRole).map(([role, count]) => ({
    name: role,
    value: count,
  }));

  const vendorChartData = Object.entries(devicesByVendor).map(([vendor, count]) => ({
    name: vendor,
    count: count,
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Dashboard</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat title="Supernets" value={supernets?.length ?? 0} />
        <Stat title="Subnets" value={subnets?.length ?? 0} />
        <Stat title="VLANs" value={vlans?.length ?? 0} />
        <Stat title="Devices" value={devices?.length ?? 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="border rounded p-4">
          <h3 className="font-semibold mb-4">Devices by Role</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={roleChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {roleChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="border rounded p-4">
          <h3 className="font-semibold mb-4">Devices by Vendor</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vendorChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="border rounded p-4">
          <h3 className="font-semibold mb-4">Network Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Total Supernets:</span>
              <span className="font-medium">{supernets?.length ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Subnets:</span>
              <span className="font-medium">{subnets?.length ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Total VLANs:</span>
              <span className="font-medium">{vlans?.length ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Avg Subnets per Supernet:</span>
              <span className="font-medium">
                {supernets?.length > 0 ? ((subnets?.length ?? 0) / supernets.length).toFixed(1) : '0'}
              </span>
            </div>
          </div>
        </div>

        <div className="border rounded p-4">
          <h3 className="font-semibold mb-4">Device Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Total Devices:</span>
              <span className="font-medium">{devices?.length ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Devices with Vendors:</span>
              <span className="font-medium">
                {(devices ?? []).filter((d: any) => d.vendor && d.vendor.trim()).length}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Devices with Serial Numbers:</span>
              <span className="font-medium">
                {(devices ?? []).filter((d: any) => d.serial_number && d.serial_number.trim()).length}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Devices in Racks:</span>
              <span className="font-medium">
                {(devices ?? []).filter((d: any) => d.rack_id).length}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ title, value }: { title: string; value: number }) {
  return (
    <div className="border rounded p-4">
      <div className="text-xs uppercase text-gray-500">{title}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}
