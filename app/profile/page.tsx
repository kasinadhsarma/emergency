"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/router"
import { getUserProfile } from "@/lib/api"

// Define the profile type
interface Profile {
  name: string
  email: string
  role: string
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getUserProfile()
        setProfile(data)
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message)
        } else {
          setError('An unknown error occurred')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  if (error) {
    return <div>Error: {error}</div>
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      {profile ? (
        <div>
          <p>Name: {profile.name}</p>
          <p>Email: {profile.email}</p>
          <p>Role: {profile.role}</p>
        </div>
      ) : (
        <p>No profile data available.</p>
      )}
    </div>
  )
}
