export async function submitWaitlistEntry(prevState: any, formData: FormData) {
  try {
    const response = await fetch("/api/waitlist", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to submit");
    }

    return { success: true, message: "Successfully joined the waitlist!" };
  } catch (error) {
    console.error("Error saving waitlist entry:", error);
    return {
      success: false,
      error: "An error occurred while saving your information. Please try again.",
    };
  }
}