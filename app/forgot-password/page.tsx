"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Layout from "../../components/Layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function ForgotPassword() {
  const [email, setEmail] = useState("")
  const [step, setStep] = useState(1)
  const [resetCode, setResetCode] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      if (step === 1) {
        // TODO: Implement sending reset code logic
        console.log("Sending reset code to:", email)
        setStep(2)
      } else if (step === 2) {
        // TODO: Implement verifying reset code logic
        console.log("Verifying reset code:", resetCode)
        setStep(3)
      } else {
        if (newPassword !== confirmPassword) {
          setError("Passwords do not match")
          return
        }
        // TODO: Implement password reset logic
        console.log("Resetting password for:", email)
        setSuccess(true)
      }
    } catch (err) {
      setError("Failed to process your request")
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
          <Card className="w-full max-w-md mx-auto">
            <CardHeader>
              <CardTitle className="text-center text-indigo-600">Password Reset Successful</CardTitle>
            </CardHeader>
            <CardContent>
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertTitle className="text-indigo-600">Success</AlertTitle>
                <AlertDescription className="text-indigo-600">
                  Your password has been successfully reset. You can now log in with your new password.
                </AlertDescription>
              </Alert>
            </CardContent>
            <CardFooter>
              <Button
                className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
                onClick={() => router.push("/login")}
              >
                Go to Login
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardFooter>
          </Card>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="text-indigo-600">
              {step === 1 ? "Reset your password" : step === 2 ? "Enter reset code" : "Set new password"}
            </CardTitle>
            <CardDescription className="text-indigo-600">
              {step === 1
                ? "Enter your email address to receive a password reset code"
                : step === 2
                  ? "Enter the reset code sent to your email"
                  : "Choose a new password for your account"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {step === 1 && (
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-indigo-600">
                    Email address
                  </Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="text-indigo-600"
                  />
                </div>
              )}
              {step === 2 && (
                <div className="space-y-2">
                  <Label htmlFor="resetCode" className="text-indigo-600">
                    Reset Code
                  </Label>
                  <Input
                    id="resetCode"
                    name="resetCode"
                    type="text"
                    required
                    value={resetCode}
                    onChange={(e) => setResetCode(e.target.value)}
                    className="text-indigo-600"
                  />
                </div>
              )}
              {step === 3 && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="newPassword" className="text-indigo-600">
                      New Password
                    </Label>
                    <Input
                      id="newPassword"
                      name="newPassword"
                      type="password"
                      required
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="text-indigo-600"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword" className="text-indigo-600">
                      Confirm New Password
                    </Label>
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="text-indigo-600"
                    />
                  </div>
                </>
              )}
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle className="text-indigo-600">Error</AlertTitle>
                  <AlertDescription className="text-indigo-600">{error}</AlertDescription>
                </Alert>
              )}
              <Button
                type="submit"
                className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
                disabled={loading}
              >
                {loading
                  ? "Processing..."
                  : step === 1
                    ? "Send Reset Code"
                    : step === 2
                      ? "Verify Code"
                      : "Reset Password"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
