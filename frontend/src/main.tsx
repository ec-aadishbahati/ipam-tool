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
import Racks from "./pages/Racks";
import IpAssignments from "./pages/IpAssignments";
import VLANs from "./pages/VLANs";
import Categories from "./pages/Categories";
import Purposes from "./pages/Purposes";
import Audits from "./pages/Audits";
import SearchPage from "./pages/Search";
import Backup from "./pages/Backup";
import { RequireAuth } from "./pages/RequireAuth";

const qc = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if ((error as any)?.response?.status === 401 && failureCount < 2) {
          return true;
        }
        return failureCount < 1;
      },
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
});

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
      { path: "racks", element: <Racks /> },
      { path: "ip-assignments", element: <IpAssignments /> },
      { path: "vlans", element: <VLANs /> },
      { path: "categories", element: <Categories /> },
      { path: "purposes", element: <Purposes /> },
      { path: "audits", element: <Audits /> },
      { path: "search", element: <SearchPage /> },
      { path: "backup", element: <Backup /> },
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
