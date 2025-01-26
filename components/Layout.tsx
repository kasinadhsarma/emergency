import type React from "react"

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <main className="flex-grow text-indigo-600">{children}</main>
      <footer className="bg-white shadow-sm mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-indigo-600">© 2025 Emergency Vehicle System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout

