"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Settings, Bell, LogOut, Moon, Sun } from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const pathname = usePathname();
  const [showSettings, setShowSettings] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Detect user's system theme preference
  useEffect(() => {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDarkMode(systemTheme);
  }, []);

  // Reset settings dialog when navigating away from dashboard
  useEffect(() => {
    if (pathname !== '/dashboard') {
      setShowSettings(false);
    }
  }, [pathname]);

  const handleLogout = () => {
    // Redirect to sign-in page
    window.location.href = "/login";
  };

  const toggleTheme = () => {
    setIsDarkMode(prevMode => !prevMode);
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-black'}`}>
      {/* Header - Only shown on dashboard */}
      {pathname === '/dashboard' && (
        <header className={`bg-white shadow-sm ${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-black'}`}>
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              {/* Logo/Title */}
              <div className="flex items-center space-x-3">
                <span className="text-xl font-bold text-indigo-600">Emergency Response</span>
              </div>

              {/* Profile and Actions */}
              <div className="flex items-center space-x-4">
                {/* Notifications */}
                <Button variant="outline" size="icon" className="relative">
                  <Bell className="h-5 w-5" />
                  <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-[10px] text-white flex items-center justify-center">
                    3
                  </span>
                </Button>

                {/* Settings */}
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowSettings(true)}
                >
                  <Settings className="h-5 w-5" />
                </Button>

                {/* Logout button */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  className="text-gray-500 hover:text-red-600"
                >
                  <LogOut className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Settings Dialog - Only shown on dashboard */}
      {pathname === '/dashboard' && (
        <Dialog open={showSettings} onOpenChange={setShowSettings}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Settings</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <h3 className="font-medium">Notifications</h3>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Enable Push Notifications</span>
                  <Button variant="outline" size="sm">
                    Enable
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium">Profile Settings</h3>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Update Profile Picture</span>
                  <Button variant="outline" size="sm">
                    Upload
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium">System</h3>
                <div className="flex items-center justify-between">
                  <span className="text-sm flex items-center">
                    <Moon className="h-5 w-5 mr-2" />
                    Dark Mode
                  </span>
                  <Button variant="outline" size="sm" onClick={toggleTheme}>
                    Toggle
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm flex items-center">
                    <Sun className="h-5 w-5 mr-2" />
                    Bright Mode
                  </span>
                  <Button variant="outline" size="sm" onClick={toggleTheme}>
                    Toggle
                  </Button>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Main Content */}
      <main className="py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;
