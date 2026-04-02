import React, { createContext, useContext, useState, ReactNode } from "react";

interface AuthUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  status: string;
}

interface AuthCtx {
  token: string | null;
  user: AuthUser | null;
  saveToken: (t: string) => void;
  saveUser: (u: AuthUser) => void;
  logout: () => void;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthCtx>({
  token: null,
  user: null,
  saveToken: () => {},
  saveUser: () => {},
  logout: () => {},
  isAdmin: false,
});

const _loadUser = (): AuthUser | null => {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [user, setUser] = useState<AuthUser | null>(_loadUser);

  const saveToken = (t: string) => {
    localStorage.setItem("token", t);
    setToken(t);
  };

  const saveUser = (u: AuthUser) => {
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      token, user, saveToken, saveUser, logout,
      isAdmin: user?.role === "admin",
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
