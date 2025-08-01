"use client"

import { useState } from "react"
import { useActionState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Check, Cloud, MessageSquare, HardDrive, Zap, Shield, BarChart3 } from "lucide-react"
import { submitWaitlistEntry } from "../actions/waitlist"

export default function WaitlistPage() {
  const [state, action, isPending] = useActionState(submitWaitlistEntry, null)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = async (formData: FormData) => {
    const result = await action(formData)
    if (result?.success) {
      setIsSubmitted(true)
    }
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-[#0d1117] text-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-gray-900 border-gray-800">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-[#2dd4bf] rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-black" />
            </div>
            <h2 className="text-2xl font-bold text-[#2dd4bf] mb-2">You're on the list!</h2>
            <p className="text-gray-400 mb-6">
              Thank you for joining our waitlist. We'll notify you when your account is ready.
            </p>
            <Button
              onClick={() => (window.location.href = "/")}
              className="w-full bg-[#6366f1] hover:bg-[#6366f1]/80 text-white"
            >
              Back to Chat
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0d1117] text-white">
      {/* Header */}
      <div className="border-b border-gray-800 p-4">
        <div className="max-w-4xl mx-auto flex items-center">
          <Button
            onClick={() => (window.location.href = "/")}
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white mr-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Chat
          </Button>
          <h1 className="text-2xl font-bold text-[#2dd4bf]">Insights</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column - Features */}
          <div className="space-y-6">
            <div>
              <h2 className="text-3xl font-bold mb-4">Join the Waitlist</h2>
              <p className="text-gray-400 text-lg">
                Get early access to advanced data analytics features and unlock the full potential of your data.
              </p>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-[#2dd4bf] mb-4">Premium Features for Registered Users</h3>

              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Cloud className="w-6 h-6 text-[#2dd4bf] mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold">Cloud Storage</h4>
                    <p className="text-gray-400 text-sm">
                      All your uploaded files are securely stored in the cloud and accessible from anywhere.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <MessageSquare className="w-6 h-6 text-[#2dd4bf] mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold">Conversation History</h4>
                    <p className="text-gray-400 text-sm">
                      All your conversations are saved and searchable. Never lose important insights.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <HardDrive className="w-6 h-6 text-[#2dd4bf] mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold">500MB Free Storage</h4>
                    <p className="text-gray-400 text-sm">
                      Get 500MB of free storage space for your data files and conversation history.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <BarChart3 className="w-6 h-6 text-[#2dd4bf] mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold">Advanced Analytics</h4>
                    <p className="text-gray-400 text-sm">
                      Access to advanced charting, statistical analysis, and data visualization tools.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Zap className="w-6 h-6 text-[#2dd4bf] mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold">Priority Processing</h4>
                    <p className="text-gray-400 text-sm">Faster response times and priority access to our AI models.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Shield className="w-6 h-6 text-[#2dd4bf] mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold">Enhanced Security</h4>
                    <p className="text-gray-400 text-sm">
                      Enterprise-grade security with encryption and secure data handling.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Form */}
          <div>
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-[#2dd4bf]">Join Our Waitlist</CardTitle>
                <CardDescription className="text-gray-400">
                  Be among the first to experience the future of data analytics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form action={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-gray-300">
                      Full Name *
                    </Label>
                    <Input
                      id="name"
                      name="name"
                      type="text"
                      placeholder="Enter your full name"
                      required
                      className="bg-gray-800 border-gray-600 text-white placeholder-gray-400"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-gray-300">
                      Email Address *
                    </Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="Enter your email address"
                      required
                      className="bg-gray-800 border-gray-600 text-white placeholder-gray-400"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="source" className="text-gray-300">
                      How did you hear about us? *
                    </Label>
                    <Select name="source" required>
                      <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
                        <SelectValue placeholder="Select an option" />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-800 border-gray-600">
                        <SelectItem value="search">Search Engine (Google, Bing, etc.)</SelectItem>
                        <SelectItem value="social">Social Media</SelectItem>
                        <SelectItem value="friend">Friend or Colleague</SelectItem>
                        <SelectItem value="blog">Blog or Article</SelectItem>
                        <SelectItem value="newsletter">Newsletter</SelectItem>
                        <SelectItem value="conference">Conference or Event</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message" className="text-gray-300">
                      Tell us about your data analysis needs (Optional)
                    </Label>
                    <Textarea
                      id="message"
                      name="message"
                      placeholder="What kind of data do you work with? What insights are you looking for?"
                      className="bg-gray-800 border-gray-600 text-white placeholder-gray-400 min-h-[100px]"
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={isPending}
                    className="w-full bg-[#2dd4bf] hover:bg-[#2dd4bf]/80 text-black font-semibold"
                  >
                    {isPending ? "Joining Waitlist..." : "Join Waitlist"}
                  </Button>

                  {state?.error && <div className="text-red-400 text-sm text-center mt-2">{state.error}</div>}

                  <p className="text-xs text-gray-500 text-center">
                    By joining, you agree to receive updates about Insights. We respect your privacy and won't spam you.
                  </p>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
