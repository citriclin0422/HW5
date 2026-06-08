import { fetchTopics } from "./lib/api";
import LearningApp from "./components/LearningApp";

export const dynamic = "force-dynamic";

export default async function Home() {
  const topics = await fetchTopics();
  return <LearningApp topics={topics} />;
}
