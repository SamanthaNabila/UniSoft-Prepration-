import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

const TOKEN_KEY = "unidesk_token";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    function handleUnauthorized() {
      setToken(null);
      setUser(null);
      setIsLoading(false);
    }

    window.addEventListener("unidesk:unauthorized", handleUnauthorized);
    return () =>
      window.removeEventListener("unidesk:unauthorized", handleUnauthorized);
  }, []);

  useEffect(() => {
    let ignore = false;

    if (!token) {
      setUser(null);
      setIsLoading(false);
      return undefined;
    }

    setIsLoading(true);
    api
      .get("/auth/me")
      .then((response) => {
        if (!ignore) setUser(response.data);
      })
      .catch(() => {
        if (!ignore) {
          localStorage.removeItem(TOKEN_KEY);
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (!ignore) setIsLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [token]);

  async function login(email, password) {
    const response = await api.post("/auth/login", { email, password });
    localStorage.setItem(TOKEN_KEY, response.data.access_token);
    setToken(response.data.access_token);
  }

  async function register({ name, email, password, role }) {
    await api.post("/auth/register", { name, email, password, role });
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  const value = {
    user,
    token,
    isAuthenticated: Boolean(user),
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
