import React, { createContext, useContext, useState, ReactNode } from "react";

interface AuthCtx {
  token: string | null;
  saveToken: (t: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx>({
  token: null,
  saveToken: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));

  const saveToken = (t: string) => {
    localStorage.setItem("token", t);
    setToken(t);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, saveToken, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
