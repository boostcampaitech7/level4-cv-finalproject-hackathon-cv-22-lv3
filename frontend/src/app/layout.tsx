import type { Metadata } from "next"
import { Geist, Azeret_Mono as Geist_Mono } from "next/font/google"
import "./globals.css"
import type React from "react"
import { AuthProvider } from "@/contexts/AuthContext"
import Layout from "@/components/Layout"
import { ToastProvider } from "@/components/ui/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { Toaster as SonnerToaster } from "sonner" // Added import for Sonner Toaster

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: "Big Star - AI-Powered Salary Negotiation Insights",
  description: "Optimize employee retention with data-driven salary recommendations",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AuthProvider>
          <ToastProvider>
            <Layout>{children}</Layout>
            <Toaster /> {/*Original Toaster*/}
            <SonnerToaster /> {/* Added SonnerToaster */}
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  )
}

