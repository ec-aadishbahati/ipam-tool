import { ReactNode, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAccessToken, startActivityTracking, stopActivityTracking } from "../lib/auth";

export function RequireAuth({ children }: { children: ReactNode }) {
  const nav = useNavigate();
  
  useEffect(() => {
    if (!getAccessToken()) {
      nav("/login", { replace: true });
    }
  }, [nav]);

  useEffect(() => {
    if (getAccessToken()) {
      startActivityTracking();
      return () => stopActivityTracking();
    }
  }, []);

  return <>{children}</>;
}
