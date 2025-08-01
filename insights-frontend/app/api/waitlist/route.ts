import { writeFile, readFile, access } from "fs/promises";
import { join } from "path";
import { NextResponse } from "next/server";

interface WaitlistEntry {
  name: string;
  email: string;
  source: string;
  message: string;
  timestamp: string;
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const name = formData.get("name");
    const email = formData.get("email");
    const source = formData.get("source");
    const message = formData.get("message");

    // Validate required fields
    if (!name || !email || typeof name !== 'string' || typeof email !== 'string') {
      return NextResponse.json(
        { error: "Name and email are required" },
        { status: 400 }
      );
    }

    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "Invalid email format" },
        { status: 400 }
      );
    }

    const entry: WaitlistEntry = {
      name,
      email,
      source: source?.toString() || '',
      message: message?.toString() || '',
      timestamp: new Date().toISOString(),
    };

    const filePath = join(process.cwd(), "waitlist_data.csv");
    let content = "";

    try {
      await access(filePath);
      content = await readFile(filePath, "utf-8");
    } catch {
      content = "Name,Email,Source,Message,Timestamp\n";
    }

    // Escape fields that might contain commas
    const escapeCsvField = (field: string) => {
      if (field.includes(',') || field.includes('"') || field.includes('\n')) {
        return `"${field.replace(/"/g, '""')}"`;
      }
      return field;
    };

    const newRow = `${escapeCsvField(entry.name)},${escapeCsvField(entry.email)},${escapeCsvField(entry.source)},${escapeCsvField(entry.message)},${entry.timestamp}\n`;
    await writeFile(filePath, content + newRow);

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to submit waitlist entry" },
      { status: 500 }
    );
  }
}
