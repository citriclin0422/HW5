import { Topic } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchTopics(): Promise<Topic[]> {
  const response = await fetch(`${API_BASE_URL}/api/topics`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load topics");
  }
  return response.json();
}

export async function askAssistant(question: string, topicSlug: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/assistant/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, topic_slug: topicSlug }),
  });

  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail ?? "AI assistant request failed");
  }
  return body.answer;
}
