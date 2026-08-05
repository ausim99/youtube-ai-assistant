"use client";

import Link from "next/link";
import Script from "next/script";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  BarChart3, Home, Lightbulb, FileText, Video, Upload, Clock, Settings, Menu, X, Moon, Sun,
} from "lucide-react";
import "./globals.css";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/ideas", label: "Ideas", icon: Lightbulb },
  { href: "/scripts", label: "Scripts", icon: FileText },
  { href: "/videos", label: "Videos", icon: Video },
  { href: "/uploads", label: "Uploads", icon: Upload },
  { href: "/pipeline", label: "Pipeline", icon: Clock },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

function Sidebar({ pathname, sidebarOpen, onClose }: { pathname: string; sidebarOpen: boolean; onClose: () => void }) {
  return (
    <>
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-gray-100 transform transition-transform lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
          <Link href="/" className="text-xl font-bold text-blue-400">YouTube AI</Link>
          <button className="lg:hidden text-gray-400 hover:text-white" onClick={onClose}><X size={24} /></button>
        </div>
        <nav className="mt-4 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${pathname === item.href ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"}`}>
                <Icon size={18} />{item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      {sidebarOpen && <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={onClose} />}
    </>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => { setMounted(true); }, []);

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    document.documentElement.classList.toggle("dark", next);
  };

  return (
    <html lang="en" className={darkMode ? "dark" : ""} suppressHydrationWarning>
      <body className="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
        {mounted ? (
          <div className="min-h-screen flex">
            <Sidebar pathname={pathname} sidebarOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <div className="flex-1 lg:pl-64">
              <header className="h-16 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-6 bg-white dark:bg-gray-950">
                <button className="lg:hidden text-gray-600 dark:text-gray-400" onClick={() => setSidebarOpen(true)}><Menu size={24} /></button>
                <div className="flex-1" />
                <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400">
                  {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>
              </header>
              <main className="p-6 min-h-[calc(100vh-4rem)]">{children}</main>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center min-h-screen">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          </div>
        )}
      </body>
    </html>
  );
}
