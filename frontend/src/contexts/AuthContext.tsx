"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { api } from "@/services/api"
import { getToken, removeToken, setToken } from "@/services/auth"
import type { User } from "@/types/user"

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      const token = getToken()
      if (token) {
        try {
          const userData = await api.getCurrentUser()
          setUser(userData)
        } catch (error) {
          console.error("Failed to fetch user data:", error)
          removeToken()
        }
      }
      setLoading(false)
    }

    loadUser()
  }, [])

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password)
    setToken(response.access_token)
    const userData = await api.getCurrentUser()
    setUser(userData)
  }

  const logout = () => {
    removeToken()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, login, logout, loading }}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

