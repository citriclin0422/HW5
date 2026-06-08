import { Topic } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchTopics(): Promise<Topic[]> {
  const response = await fetch(`${API_BASE_URL}/api/topics`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load topics");
  }
  return response.json();
}
