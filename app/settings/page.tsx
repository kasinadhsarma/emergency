"use client"

import { useState } from "react"

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: false,
    language: "en"
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setSettings(prevSettings => ({
      ...prevSettings,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle settings submission
    console.log("Settings submitted:", settings)
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700" htmlFor="notifications">Notifications</label>
          <input
            type="checkbox"
            id="notifications"
            name="notifications"
            checked={settings.notifications}
            onChange={handleChange}
            className="mt-1"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700" htmlFor="darkMode">Dark Mode</label>
          <input
            type="checkbox"
            id="darkMode"
            name="darkMode"
            checked={settings.darkMode}
            onChange={handleChange}
            className="mt-1"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700" htmlFor="language">Language</label>
          <select
            id="language"
            name="language"
            value={settings.language}
            onChange={handleChange}
            className="mt-1"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
          </select>
        </div>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Save Settings
        </button>
      </form>
    </div>
  )
}
