import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Emergency Vehicle System',
  description: 'Track emergency vehicles in real-time',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
