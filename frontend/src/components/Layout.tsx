"use client"

import Link from "next/link"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"
import type React from "react"

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout, loading } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="flex flex-col min-h-screen">
      <header className="p-4 flex justify-between items-center border-b">
        <div className="flex items-center">
          <Link href="/" className="text-2xl font-bold text-blue-600 hover:text-blue-800 transition-colors">
            BigStar
          </Link>
        </div>
        <nav>
          <ul className="flex items-center space-x-6">
            <li>
              <Link href="/about" className="hover:text-blue-600 transition-colors">
                About
              </Link>
            </li>
            <li>
              <Link href="/contact" className="hover:text-blue-600 transition-colors">
                Contact
              </Link>
            </li>
            <li>
              {user ? (
                <button onClick={handleLogout} className="hover:text-blue-600 transition-colors">
                  Logout
                </button>
              ) : (
                <Link href="/login" className="hover:text-blue-600 transition-colors">
                  Login
                </Link>
              )}
            </li>
          </ul>
        </nav>
      </header>
      <main className="flex-grow">{children}</main>
    </div>
  )
}

