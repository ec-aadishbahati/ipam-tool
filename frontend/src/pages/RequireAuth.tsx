import React from "react";

import { ReactNode, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAccessToken } from "../lib/auth";

export function RequireAuth({ children }: { children: ReactNode }) {
  const nav = useNavigate();
  useEffect(() => {
    if (!getAccessToken()) {
      nav("/login", { replace: true });
    }
  }, [nav]);
  return <>{children}</>;
}
