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
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const source = formData.get("source") as string;
    const message = formData.get("message") as string;

    const entry: WaitlistEntry = {
      name,
      email,
      source,
      message,
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

    const newRow = `${entry.name},${entry.email},${entry.source},${entry.message},${entry.timestamp}\n`;
    await writeFile(filePath, content + newRow);

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to submit waitlist entry" },
      { status: 500 }
    );
  }
}
