import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { cleanupCharts } from "@/lib/cleanup"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Insights - Data Analysis & Visualization",
  description: "Data Visualization Application for Everyone",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  
  // Add cleanup on page load/reload
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      cleanupCharts();
    });
  }

  return (
    <html lang="en" className="dark">
      <body className={inter.className} suppressHydrationWarning>{children}</body>
    </html>
  )
}
