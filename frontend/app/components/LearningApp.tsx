"use client";

import Image from "next/image";
import { useMemo, useState } from "react";
import {
  BarChart3,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  FlaskConical,
  ListChecks,
  Search,
  Sparkles,
  Target,
} from "lucide-react";
import { Topic } from "../lib/types";

type Props = {
  topics: Topic[];
};

const familyOptions = ["all", "監督式學習", "非監督式學習", "集成學習", "深度學習"];
const difficultyOptions = ["all", "入門", "中階", "進階"];

export default function LearningApp({ topics }: Props) {
  const [activeSlug, setActiveSlug] = useState(topics[0]?.slug ?? "");
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");
  const [difficulty, setDifficulty] = useState("all");
  const [completed, setCompleted] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const filteredTopics = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return topics.filter((topic) => {
      const matchesQuery =
        !needle ||
        topic.title.toLowerCase().includes(needle) ||
        topic.english.toLowerCase().includes(needle) ||
        topic.summary.toLowerCase().includes(needle);
      const matchesFamily = family === "all" || topic.family === family;
      const matchesDifficulty = difficulty === "all" || topic.difficulty === difficulty;
      return matchesQuery && matchesFamily && matchesDifficulty;
    });
  }, [difficulty, family, query, topics]);

  const activeTopic =
    topics.find((topic) => topic.slug === activeSlug) ?? filteredTopics[0] ?? topics[0];
  const activeIndex = topics.findIndex((topic) => topic.slug === activeTopic.slug);
  const progress = Math.round((completed.length / topics.length) * 100);
  const selectedAnswer = answers[activeTopic.slug];
  const isCorrect = selectedAnswer === activeTopic.quiz.answer;

  function toggleComplete(slug: string) {
    setCompleted((current) =>
      current.includes(slug) ? current.filter((item) => item !== slug) : [...current, slug],
    );
  }

  function move(offset: number) {
    const nextIndex = (activeIndex + offset + topics.length) % topics.length;
    setActiveSlug(topics[nextIndex].slug);
  }

  return (
    <main className="shell">
      <section className="hero">
        <div className="heroText">
          <p className="eyebrow">
            <Sparkles size={16} /> Dynamic ML Studio
          </p>
          <h1>Top10 機器學習互動學習</h1>
          <p>
            從原本的研讀報告與資訊圖出發，把十大演算法整理成可搜尋、可測驗、可追蹤進度的動態教材。
          </p>
          <div className="heroStats">
            <span><strong>{topics.length}</strong> 主題</span>
            <span><strong>{completed.length}</strong> 已完成</span>
            <span><strong>{progress}%</strong> 進度</span>
          </div>
        </div>
        <div className="heroImage">
          <Image
            src="/assets/top10-infographic.png"
            alt="Top10 機器學習資訊圖表"
            width={900}
            height={1200}
            priority
          />
        </div>
      </section>

      <section className="workspace">
        <aside className="sidebar">
          <div className="searchBox">
            <Search size={18} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜尋演算法或概念"
            />
          </div>

          <div className="filters">
            <select value={family} onChange={(event) => setFamily(event.target.value)}>
              {familyOptions.map((option) => (
                <option key={option} value={option}>
                  {option === "all" ? "全部類型" : option}
                </option>
              ))}
            </select>
            <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
              {difficultyOptions.map((option) => (
                <option key={option} value={option}>
                  {option === "all" ? "全部難度" : option}
                </option>
              ))}
            </select>
          </div>

          <div className="topicList">
            {filteredTopics.map((topic, index) => (
              <button
                key={topic.slug}
                className={topic.slug === activeTopic.slug ? "topicButton active" : "topicButton"}
                onClick={() => setActiveSlug(topic.slug)}
              >
                <span className="topicNumber">{index + 1}</span>
                <span>
                  <strong>{topic.title}</strong>
                  <small>{topic.english}</small>
                </span>
                {completed.includes(topic.slug) && <CheckCircle2 size={17} />}
              </button>
            ))}
          </div>
        </aside>

        <section className="lesson">
          <div className="lessonHeader">
            <div>
              <span className="tag">{activeTopic.family}</span>
              <span className="tag muted">{activeTopic.difficulty}</span>
              <h2>{activeTopic.title}</h2>
              <p>{activeTopic.english}</p>
            </div>
            <div className="lessonNav">
              <button aria-label="上一個主題" onClick={() => move(-1)}>
                <ChevronLeft size={20} />
              </button>
              <button aria-label="下一個主題" onClick={() => move(1)}>
                <ChevronRight size={20} />
              </button>
            </div>
          </div>

          <div className="summaryBand">
            <BookOpen size={22} />
            <p>{activeTopic.summary}</p>
          </div>

          <div className="learningGrid">
            <InfoPanel icon={<Target size={20} />} title="適合什麼情境">
              <p>{activeTopic.why}</p>
              <p className="example">範例：{activeTopic.example}</p>
            </InfoPanel>

            <InfoPanel icon={<ListChecks size={20} />} title="學習流程">
              <ol>
                {activeTopic.steps.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </InfoPanel>

            <InfoPanel icon={<BarChart3 size={20} />} title="優勢">
              <ul>
                {activeTopic.strengths.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </InfoPanel>

            <InfoPanel icon={<FlaskConical size={20} />} title="限制與注意">
              <ul>
                {activeTopic.limits.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </InfoPanel>
          </div>

          <section className="quiz">
            <div>
              <h3>快速檢核</h3>
              <p>{activeTopic.quiz.question}</p>
            </div>
            <div className="answerGrid">
              {activeTopic.quiz.options.map((option) => (
                <button
                  key={option}
                  className={selectedAnswer === option ? "answer selected" : "answer"}
                  onClick={() =>
                    setAnswers((current) => ({ ...current, [activeTopic.slug]: option }))
                  }
                >
                  {option}
                </button>
              ))}
            </div>
            {selectedAnswer && (
              <p className={isCorrect ? "feedback ok" : "feedback"}>
                {isCorrect ? "答對了，這個概念已經抓住。" : `再想一下，正確答案是「${activeTopic.quiz.answer}」。`}
              </p>
            )}
          </section>

          <div className="completionRow">
            <div className="progressTrack">
              <span style={{ width: `${progress}%` }} />
            </div>
            <button className="completeButton" onClick={() => toggleComplete(activeTopic.slug)}>
              <CheckCircle2 size={18} />
              {completed.includes(activeTopic.slug) ? "取消完成" : "標記完成"}
            </button>
          </div>
        </section>
      </section>
    </main>
  );
}

function InfoPanel({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <article className="panel">
      <h3>
        {icon}
        {title}
      </h3>
      {children}
    </article>
  );
}
