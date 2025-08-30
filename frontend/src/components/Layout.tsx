import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { clearTokens } from "../lib/auth";
import logoSvg from "../assets/logo.svg?url";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/supernets", label: "Supernets" },
  { to: "/subnets", label: "Subnets" },
  { to: "/devices", label: "Devices" },
  { to: "/racks", label: "Racks" },
  { to: "/ip-assignments", label: "IP Assignments" },
  { to: "/vlans", label: "VLANs" },
  { to: "/categories", label: "Categories" },
  { to: "/purposes", label: "Purposes" },
  { to: "/audits", label: "Audits" },
  { to: "/search", label: "Search" },
  { to: "/backup", label: "Backup" },
];

export default function Layout() {
  const loc = useLocation();
  const nav = useNavigate();
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 border-r p-4 space-y-2">
        <div className="text-lg font-semibold mb-1">EE SPARK</div>
        <div className="text-xs text-gray-600 mb-4">Essential Energy - Subnet Planning & Address Registry Kit</div>
        <nav className="space-y-2">
          {links.map((l) => (
            <Link key={l.to} to={l.to} className={`block px-2 py-1 rounded ${loc.pathname === l.to ? "bg-gray-200" : "hover:bg-gray-100"}`}>
              {l.label}
            </Link>
          ))}
        </nav>
        <button
          className="mt-6 text-sm text-red-600"
          onClick={() => {
            clearTokens();
            nav("/login");
          }}
        >
          Logout
        </button>
      </aside>
      <main className="flex-1 p-6">
        <div className="flex justify-between items-center mb-6">
          <div></div>
          <img src={logoSvg} alt="Essential Energy Logo" className="h-10" />
        </div>
        <Outlet />
      </main>
    </div>
  );
}
