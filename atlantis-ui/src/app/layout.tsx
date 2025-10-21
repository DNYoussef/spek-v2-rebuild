/**
 * Root Layout - SPEK Atlantis UI
 *
 * Version: 8.1.0 (Week 24 - Performance Optimization)
 * Week: 7 Day 1
 * Week 24: Added resource hints, optimized font loading, added Vercel Analytics
 */

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { TRPCProvider } from "@/lib/trpc/Provider";

// Week 24: Optimized font loading with display swap (FOUT instead of FOIT)
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap", // Prevents FOIT (Flash of Invisible Text)
  preload: true,   // Preload fonts for faster initial render
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

export const metadata: Metadata = {
  title: "SPEK Atlantis - AI-Powered Agent Coordination Platform",
  description: "SPEK Platform v8.0.0 - Advanced agent coordination with three-loop methodology",
  // Week 24: Resource hints for performance
  other: {
    'theme-color': '#f59e0b', // Amber-500 brand color
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Week 24: Resource hints for performance */}
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://fonts.gstatic.com" />
        <link rel="preconnect" href="https://fonts.googleapis.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />

        {/* Viewport meta for responsive design */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <TRPCProvider>
          {children}
        </TRPCProvider>
      </body>
    </html>
  );
}
