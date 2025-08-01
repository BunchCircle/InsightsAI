"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { UploadCloud, Send, FileText } from "lucide-react"
import { uploadCsv } from "@/lib/api"
import { sendChat } from "@/lib/api"

interface Message {
  id: string
  type: "user" | "ai"
  content: string
  charts?: string[]
  timestamp: Date
  preview?: any[]
  columns?: string[]
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes"
  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

// Helper to generate unique IDs on the client
const generateUniqueId = () => `${Date.now()}-${Math.random()}`;

export default function DataChatApp() {
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; size: number; id: string }>>([])
  const [isUploaded, setIsUploaded] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isChatting, setIsChatting] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")

  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const dropZoneRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleFileUpload = async (files: FileList | File[]) => {
    const fileArray = Array.from(files)
    const maxSize = 50 * 1024 * 1024 // 50MB in bytes

    // Validate files
    const invalidFiles = fileArray.filter((file) => !file.name.endsWith(".csv") || file.size > maxSize)

    if (invalidFiles.length > 0) {
      const oversizedFiles = invalidFiles.filter((f) => f.size > maxSize)
      const nonCsvFiles = invalidFiles.filter((f) => !f.name.endsWith(".csv"))

      let errorMessage = ""
      if (nonCsvFiles.length > 0) {
        errorMessage += `Please upload only CSV files. Invalid: ${nonCsvFiles.map((f) => f.name).join(", ")}\n`
      }
      if (oversizedFiles.length > 0) {
        errorMessage += `File size must be under 50MB. Too large: ${oversizedFiles.map((f) => f.name).join(", ")}`
      }

      alert(errorMessage)
      return
    }

    setIsUploading(true)

    try {
      const data = await uploadCsv(fileArray[0], "guest");
      const fileNames = fileArray.map((f) => f.name).join(", ");
      
      if (data.status === "error") {
        // Show validation issues but don't set as uploaded
        setMessages((prev) => [
          ...prev,
          {
            id: generateUniqueId(),
            type: "ai",
            content: `⚠️ The uploaded file needs cleaning:\n\n${data.issues.join('\n')}\n\nPlease fix these issues and upload again. Preview of your data:`,
            timestamp: new Date(),
            preview: data.preview,
            columns: data.columns,
          },
        ]);
        return;
      }

      const newFiles = fileArray.map((file) => ({
        name: file.name,
        size: file.size,
        id: generateUniqueId(),
      }))

      setUploadedFiles((prev) => [...prev, ...newFiles])
      setIsUploaded(true)

      // Add a message with the preview table
      setMessages((prev) => [
        ...prev,
        {
          id: generateUniqueId(),
          type: "ai",
          content: `${fileArray.length} file(s) uploaded successfully: ${fileNames}. Here are the first 5 rows:`,
          timestamp: new Date(),
          preview: data.preview,
          columns: data.columns,
        },
      ])
    } catch (error) {
      console.error("Upload error:", error)
      alert("Upload failed. Please check your connection.")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files)
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim() || !isUploaded || isChatting) return

    const userMessage: Message = {
      id: generateUniqueId(),
      type: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsChatting(true)

    try {
      const data = await sendChat(userMessage.content, "guest");
      console.log("Frontend: Received data from backend:", data);
      console.log("Frontend: Charts data:", data.charts);
      const aiMessage: Message = {
        id: generateUniqueId(),
        type: "ai",
        content: data.answer,
        charts: data.charts,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error: any) {
      console.error("Chat error:", error);
      let errorMessage: Message;
      
      if (error?.response?.status === 400 && error?.response?.data?.suggestions) {
        errorMessage = {
          id: generateUniqueId(),
          type: "ai",
          content: error.response.data.suggestions,
          timestamp: new Date(),
        };
      } else {
        // Try to get a more detailed error message
        const errorDetail = error.message || error.toString();
        errorMessage = {
          id: generateUniqueId(),
          type: "ai",
          content: `Sorry, I encountered an error: ${errorDetail}. Please try again.`,
          timestamp: new Date(),
        };
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsChatting(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex h-screen bg-[#0d1117] text-white">
      {/* Sidebar */}
      <div className="w-[250px] bg-[#0d1117] border-r border-gray-800 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-2xl font-bold text-[#2dd4bf]">Insights</h1>
        </div>

        {/* Upload Section */}
        <div className="flex-1 p-4">
          <div
            ref={dropZoneRef}
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              isDragOver ? "border-[#2dd4bf] bg-[#2dd4bf]/10" : "border-gray-600 hover:border-[#2dd4bf]/50"
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />

            {uploadedFiles.length > 0 ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-[#2dd4bf]">Uploaded Files ({uploadedFiles.length})</h3>
                </div>
                <div className="max-h-40 overflow-y-auto space-y-2">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="flex items-center justify-between p-2 bg-gray-800 rounded text-xs">
                      <div className="flex items-center space-x-2 flex-1 min-w-0">
                        <FileText className="w-4 h-4 text-[#2dd4bf] flex-shrink-0" />
                        <div className="min-w-0 flex-1">
                          <p className="text-gray-300 truncate">{file.name}</p>
                          <p className="text-gray-500">{(file.size / (1024 * 1024)).toFixed(1)} MB</p>
                        </div>
                      </div>
                      <Button
                        onClick={() => {
                          setUploadedFiles((prev) => prev.filter((f) => f.id !== file.id))
                          if (uploadedFiles.length === 1) {
                            setIsUploaded(false)
                            setMessages([])
                          }
                        }}
                        variant="ghost"
                        size="sm"
                        className="text-red-400 hover:text-red-300 hover:bg-red-900/20 p-1 h-auto"
                      >
                        ×
                      </Button>
                    </div>
                  ))}
                </div>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  size="sm"
                  className="w-full border-gray-600 text-gray-300 hover:bg-gray-800"
                >
                  Add More Files
                </Button>
                <Button
                  onClick={() => {
                    setUploadedFiles([])
                    setIsUploaded(false)
                    setMessages([])
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ""
                    }
                  }}
                  variant="outline"
                  size="sm"
                  className="w-full border-red-600 text-red-400 hover:bg-red-900/20"
                >
                  Clear All Files
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <UploadCloud className="w-8 h-8 text-gray-400 mx-auto" />
                <div>
                  <p className="text-sm text-gray-300">{isUploading ? "Uploading..." : "Drop CSV files here"}</p>
                  <p className="text-xs text-gray-500 mt-1">Multiple files supported (max 50MB each)</p>
                </div>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="bg-[#2dd4bf] hover:bg-[#2dd4bf]/80 text-black"
                >
                  {isUploading ? "Uploading..." : "Choose Files"}
                </Button>
              </div>
            )}
          </div>

          {/* Disclaimer Section */}
          <div className="mt-6 p-4 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-semibold text-[#2dd4bf] mb-2">Disclaimer</h3>
            <p className="text-sm text-gray-300">
              Use cleaned data to ask questions and be specific about your queries.
              <br />
              Add 'visualize' word before your query to see the result as a chart.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800 space-y-3">
          <p className="text-sm text-gray-400">Guest (session-only)</p>
          <Button
            onClick={() => (window.location.href = "/waitlist")}
            className="w-full bg-[#2dd4bf] hover:bg-[#2dd4bf]/80 text-black text-sm"
            size="sm"
          >
            Sign Up / Login
          </Button>
          <Button
            onClick={() => window.open("https://forms.gle/iu5UUAbmcEyCfAxh9", "_blank")}
            className="w-full border border-[#2dd4bf] text-[#2dd4bf] hover:bg-[#2dd4bf]/10 text-sm"
            size="sm"
            variant="outline"
          >
            Give Feedback
          </Button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col w-full max-w-4xl mx-auto">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-xl font-semibold">Conversation</h2>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ minWidth: 0 }}>
          {messages.length === 0 && (
            <div className="text-center space-y-8 mt-8 transition-opacity duration-500">
              <h1 className="text-5xl font-bold mb-6">
                <span className="text-white">Meet </span>
                <span className="text-[#27AD9E]">Insights</span>
                <span className="text-white"> 👋</span>
              </h1>
              
              <p className="text-xl text-gray-300 mb-8">
                Analyse & Visualize your CSV data like never before.
              </p>
              
              <div className="max-w-2xl mx-auto text-lg text-gray-300 mb-12"> 
                Discover insights that data professionals might miss. <br />
                No more data overwhelm. Just ask questions like you're talking to a friend.
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <h3 className="text-[#27AD9E] text-xl font-semibold mb-3">Built for Data</h3>
                  <p className="text-gray-300">Designed specifically for data analysis—no copy-pasting or technical setup needed.</p>
                </div>
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <h3 className="text-[#27AD9E] text-xl font-semibold mb-3">Context-Aware</h3>
                  <p className="text-gray-300">Remembers your data and full chat history for smarter conversations.</p>
                </div>
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <h3 className="text-[#27AD9E] text-xl font-semibold mb-3">Visual First</h3>
                  <p className="text-gray-300">Delivers beautiful, interactive charts instead of plain text answers.</p>
                </div>
              </div>

              <div className="max-w-2xl mx-auto">
                <h2 className="text-2xl font-semibold text-[#27AD9E] mb-6">How It Works</h2>
                <div className="space-y-4 text-lg text-gray-300">
                  <p>1. Drop your data: Just drag and drop your CSV files</p>
                  <p>2. Chat naturally: Talk to me like you would to a colleague</p>
                  <p>3. Get instant insights: I'll show you beautiful visualizations</p>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-full rounded-lg p-3 ${
                  message.type === "user" ? "bg-[#6366f1] text-white" : "bg-gray-800 text-gray-100"
                }`}
                style={{ width: '100%', boxSizing: 'border-box', overflowX: 'auto' }}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.preview && message.columns?.length && (
                  <div className="overflow-x-auto mt-2" style={{ maxWidth: '100%', minWidth: 0 }}>
                    <table className="min-w-max text-xs border border-gray-300 rounded bg-white" style={{ color: '#111', minWidth: '600px', maxWidth: '100%' }}>
                      <thead>
                        <tr>
                          {message.columns?.map((col) => (
                            <th
                              key={col}
                              className="px-2 py-1 border border-gray-300 text-left"
                              style={{ color: '#2CD1BD', background: '#fff', fontWeight: 600 }}
                            >
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {message.preview.map((row, idx) => (
                          <tr key={idx}>
                            {message.columns?.map((col) => (
                              <td
                                key={col}
                                className="px-2 py-1 border border-gray-300"
                                style={{ background: '#fff', color: '#111', fontWeight: 400 }}
                              >
                                {row[col]}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                {message.charts && message.charts.length > 0 && (
                  <div className="mt-3 space-y-4">
                    {message.charts.map((chartPath, index) => {
                      const fullUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/${chartPath}`;
                      return (
                        <iframe
                          key={index}
                          src={fullUrl}
                          title={`Generated chart ${index + 1}`}
                          className="max-w-full h-[500px] w-full rounded border border-gray-600"
                          style={{ minHeight: 400 }}
                        />
                      );
                    })}
                  </div>
                )}
                <p className="text-xs opacity-70 mt-2">{message.timestamp.toLocaleTimeString()}</p>
              </div>
            </div>
          ))}

          {isChatting && (
            <div className="flex justify-start">
              <div className="bg-gray-800 text-gray-100 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-[#2dd4bf] rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-[#2dd4bf] rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-[#2dd4bf] rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-800">
          <div className="flex space-x-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isUploaded ? "Ask a question about your data..." : "Upload a CSV file to start chatting..."}
              disabled={!isUploaded || isChatting}
              className="flex-1 bg-gray-800 border-gray-600 text-white placeholder-gray-400 resize-none min-h-[60px] max-h-[120px]"
              rows={2}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!isUploaded || !input.trim() || isChatting}
              className="bg-[#2dd4bf] hover:bg-[#2dd4bf]/80 text-black self-end"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
