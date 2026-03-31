import { useState } from "react";

export function useAuthState() {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));

  const saveToken = (t: string) => {
    localStorage.setItem("token", t);
    setToken(t);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return { token, saveToken, logout, isLoggedIn: !!token };
}
