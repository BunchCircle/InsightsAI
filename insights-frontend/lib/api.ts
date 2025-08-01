const API = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function uploadCsv(file: File, username = "guest") {
  const form = new FormData();
  form.append("file", file);
  form.append("username", username);

  const res = await fetch(`${API}/api/upload/`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function sendChat(question: string, username = "guest") {
  try {
    const res = await fetch(`${API}/api/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, question }),
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || "Failed to get response from server");
    }
    
    return await res.json();
  } catch (error) {
    console.error("Chat API Error:", error);
    throw error;
  }
}