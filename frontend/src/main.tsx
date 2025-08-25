import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import "./index.css";
import Login from "./pages/Login";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Supernets from "./pages/Supernets";
import Subnets from "./pages/Subnets";
import Devices from "./pages/Devices";
import IpAssignments from "./pages/IpAssignments";
import VLANs from "./pages/VLANs";
import Purposes from "./pages/Purposes";
import Audits from "./pages/Audits";
import SearchPage from "./pages/Search";
import { RequireAuth } from "./pages/RequireAuth";

const qc = new QueryClient();

const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: (
      <RequireAuth>
        <Layout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: "supernets", element: <Supernets /> },
      { path: "subnets", element: <Subnets /> },
      { path: "devices", element: <Devices /> },
      { path: "ip-assignments", element: <IpAssignments /> },
      { path: "vlans", element: <VLANs /> },
      { path: "purposes", element: <Purposes /> },
      { path: "audits", element: <Audits /> },
      { path: "search", element: <SearchPage /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);
