"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Layout from "../../components/Layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import Link from "next/link"
import { Facebook, Twitter } from "lucide-react"
import { FcGoogle } from "react-icons/fc"

export default function Signup() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      // TODO: Implement your actual signup logic here
      // const response = await signupUser(email, password, confirmPassword);
      if (password !== confirmPassword) {
        setError("Passwords do not match")
        return
      }
      router.push("/dashboard")
    } catch (err) {
      setError("Failed to sign up")
    } finally {
      setLoading(false)
    }
  }

  const handleSocialSignup = async (provider: string) => {
    try {
      // TODO: Implement your social signup logic here
      // const response = await socialSignup(provider);
      router.push("/dashboard")
    } catch (err) {
      setError(`Failed to sign up with ${provider}`)
    }
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold text-indigo-600">Create your account</CardTitle>
            <CardDescription className="text-center text-indigo-600">
              Sign up to access the Emergency Vehicle System
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-indigo-600">
                  Email address
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-indigo-600">
                  Password
                </label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-indigo-600">
                  Confirm Password
                </label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="mt-1"
                />
              </div>
              {error && (
                <p className="text-sm text-red-600">{error}</p>
              )}
              <div>
                <Button 
                  type="submit" 
                  className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
                  disabled={loading}
                >
                  {loading ? "Signing up..." : "Sign up"}
                </Button>
              </div>
            </form>
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <Separator className="w-full" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or sign up with</span>
                </div>
              </div>
              <div className="mt-6 grid grid-cols-3 gap-3">
                <Button variant="outline" onClick={() => handleSocialSignup("Google")}>
                  <FcGoogle className="h-5 w-5" />
                  <span className="sr-only">Sign up with Google</span>
                </Button>
                <Button variant="outline" onClick={() => handleSocialSignup("Facebook")}>
                  <Facebook className="h-5 w-5 text-blue-600" />
                  <span className="sr-only">Sign up with Facebook</span>
                </Button>
                <Button variant="outline" onClick={() => handleSocialSignup("Twitter")}>
                  <Twitter className="h-5 w-5 text-sky-500" />
                  <span className="sr-only">Sign up with Twitter</span>
                </Button>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Link href="/login" className="text-sm text-indigo-600 hover:text-indigo-500">
              Already have an account? Sign in
            </Link>
          </CardFooter>
        </Card>
      </div>
    </Layout>
  )
}