"use server";

import { writeFile, readFile, access } from "fs/promises";
import { join } from "path";

interface WaitlistEntry {
  name: string;
  email: string;
  source: string;
  message: string;
  timestamp: string;
}

export async function submitWaitlistEntry(prevState: any, formData: FormData) {
  try {
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const source = formData.get("source") as string;
    const message = formData.get("message") as string;

    // Validate required fields
    if (!name || !email || !source) {
      return { success: false, error: "Please fill in all required fields." };
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return { success: false, error: "Please enter a valid email address." };
    }

    const entry: WaitlistEntry = {
      name: name.trim(),
      email: email.trim().toLowerCase(),
      source,
      message: message?.trim() || "",
      timestamp: new Date().toISOString(),
    };

    const csvFilePath = join(process.cwd(), "waitlist_data.csv");

    let fileExists = false;
    try {
      await access(csvFilePath);
      fileExists = true;
    } catch {
      fileExists = false;
    }

    let csvContent = "";
    if (!fileExists) {
      csvContent = "Name,Email,Source,Message,Timestamp\n";
    } else {
      csvContent = await readFile(csvFilePath, "utf-8");
    }

    const escapeCsvValue = (value: string): string => {
      if (value.includes(",") || value.includes('"') || value.includes("\n") || value.includes("\r")) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value;
    };

    // Duplicate check
    const lines = csvContent.split("\n");
    const existingEmails = lines
      .slice(1)
      .map((line) => {
        const columns = line.split(",");
        return columns[1]?.replace(/"/g, "").toLowerCase();
      })
      .filter(Boolean);

    if (existingEmails.includes(entry.email)) {
      return { success: false, error: "This email address is already on our waitlist." };
    }

    const newRow = [
      escapeCsvValue(entry.name),
      escapeCsvValue(entry.email),
      escapeCsvValue(entry.source),
      escapeCsvValue(entry.message),
      escapeCsvValue(entry.timestamp),
    ].join(",");

    csvContent += newRow + "\n";
    await writeFile(csvFilePath, csvContent, "utf-8");

    return { success: true, message: "Successfully joined the waitlist!" };
  } catch (error) {
    console.error("Error saving waitlist entry:", error);
    return {
      success: false,
      error: "An error occurred while saving your information. Please try again.",
    };
  }
}