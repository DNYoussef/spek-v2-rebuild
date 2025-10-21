/**
 * Root Layout Component
 *
 * Main layout wrapper with Header, Sidebar, and Footer.
 *
 * Version: 8.0.0
 * Week: 7 Day 1
 */

import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';

export function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
}
