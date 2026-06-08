"use client";

import Image from "next/image";
import { useMemo, useState } from "react";
import {
  BarChart3,
  BookOpen,
  Bot,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  FlaskConical,
  LoaderCircle,
  ListChecks,
  Search,
  Send,
  SlidersHorizontal,
  Sparkles,
  Target,
} from "lucide-react";
import { askAssistant } from "../lib/api";
import { AssistantMessage, Topic } from "../lib/types";

type Props = {
  topics: Topic[];
};

type ChartPoint = {
  x: number;
  y: number;
  group: "A" | "B";
};

const difficultyOptions = ["all", "簡單", "中等", "進階"];

export default function LearningApp({ topics }: Props) {
  const [activeSlug, setActiveSlug] = useState(topics[0]?.slug ?? "");
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");
  const [difficulty, setDifficulty] = useState("all");
  const [completed, setCompleted] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [assistantQuestion, setAssistantQuestion] = useState("");
  const [assistantMessages, setAssistantMessages] = useState<AssistantMessage[]>([]);
  const [assistantError, setAssistantError] = useState("");
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [complexity, setComplexity] = useState(55);
  const [regularization, setRegularization] = useState(35);
  const [trainingRatio, setTrainingRatio] = useState(70);

  const families = useMemo(
    () => ["all", ...Array.from(new Set(topics.map((topic) => topic.family)))],
    [topics],
  );

  const filteredTopics = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return topics.filter((topic) => {
      const matchesQuery =
        !needle ||
        topic.title.toLowerCase().includes(needle) ||
        topic.english.toLowerCase().includes(needle) ||
        topic.summary.toLowerCase().includes(needle);
      const matchesFamily = family === "all" || topic.family === family;
      const matchesDifficulty =
        difficulty === "all" || normalizeDifficulty(topic.difficulty) === difficulty;
      return matchesQuery && matchesFamily && matchesDifficulty;
    });
  }, [difficulty, family, query, topics]);

  const activeTopic =
    topics.find((topic) => topic.slug === activeSlug) ?? filteredTopics[0] ?? topics[0];
  const activeIndex = topics.findIndex((topic) => topic.slug === activeTopic.slug);
  const progress = Math.round((completed.length / topics.length) * 100);
  const selectedAnswer = answers[activeTopic.slug];
  const isCorrect = selectedAnswer === activeTopic.quiz.answer;

  const chartPoints = useMemo(
    () => buildChartPoints(activeIndex, complexity, regularization, trainingRatio),
    [activeIndex, complexity, regularization, trainingRatio],
  );
  const boundaryPath = buildBoundaryPath(complexity, regularization);
  const metrics = buildMetrics(complexity, regularization, trainingRatio);

  function toggleComplete(slug: string) {
    setCompleted((current) =>
      current.includes(slug) ? current.filter((item) => item !== slug) : [...current, slug],
    );
  }

  function move(offset: number) {
    const nextIndex = (activeIndex + offset + topics.length) % topics.length;
    setActiveSlug(topics[nextIndex].slug);
  }

  async function submitAssistantQuestion(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = assistantQuestion.trim();
    if (!question || assistantLoading) {
      return;
    }

    setAssistantQuestion("");
    setAssistantError("");
    setAssistantMessages((current) => [...current, { role: "user", content: question }]);
    setAssistantLoading(true);

    try {
      const answer = await askAssistant(question, activeTopic.slug);
      setAssistantMessages((current) => [...current, { role: "assistant", content: answer }]);
    } catch (error) {
      setAssistantError(error instanceof Error ? error.message : "AI 助理目前無法回答，請稍後再試。");
    } finally {
      setAssistantLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <div className="heroText">
          <p className="eyebrow">
            <Sparkles size={16} /> Dynamic ML Studio
          </p>
          <h1>十大機器學習演算法互動平台</h1>
          <p>
            用互動課程、參數視覺化、AI 問答與小測驗，快速理解十大經典機器學習演算法的使用情境、優缺點與核心概念。
          </p>
          <div className="heroStats">
            <span><strong>{topics.length}</strong> 個演算法</span>
            <span><strong>{completed.length}</strong> 個已完成</span>
            <span><strong>{progress}%</strong> 學習進度</span>
          </div>
        </div>
        <div className="heroImage">
          <Image
            src="/assets/top10-infographic.png"
            alt="十大機器學習演算法資訊圖表"
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
              placeholder="搜尋演算法或關鍵字"
            />
          </div>

          <div className="filters">
            <select value={family} onChange={(event) => setFamily(event.target.value)}>
              {families.map((option) => (
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
              <span className="tag muted">{normalizeDifficulty(activeTopic.difficulty)}</span>
              <h2>{activeTopic.title}</h2>
              <p>{activeTopic.english}</p>
            </div>
            <div className="lessonNav">
              <button aria-label="上一個演算法" onClick={() => move(-1)}>
                <ChevronLeft size={20} />
              </button>
              <button aria-label="下一個演算法" onClick={() => move(1)}>
                <ChevronRight size={20} />
              </button>
            </div>
          </div>

          <div className="summaryBand">
            <BookOpen size={22} />
            <p>{activeTopic.summary}</p>
          </div>

          <section className="simulator">
            <div className="parameterPanel">
              <h3><SlidersHorizontal size={20} /> 參數調整</h3>
              <ParameterSlider
                label="模型複雜度"
                value={complexity}
                min={10}
                max={100}
                unit="%"
                help="越高代表模型越容易貼近訓練資料，也越可能過度擬合。"
                onChange={setComplexity}
              />
              <ParameterSlider
                label="正則化強度"
                value={regularization}
                min={0}
                max={100}
                unit="%"
                help="越高代表限制越強，模型會更平滑但可能欠擬合。"
                onChange={setRegularization}
              />
              <ParameterSlider
                label="訓練資料比例"
                value={trainingRatio}
                min={40}
                max={90}
                unit="%"
                help="調整訓練資料量，觀察泛化分數與資料點分布。"
                onChange={setTrainingRatio}
              />
            </div>

            <div className="chartPanel">
              <div className="chartHeader">
                <h3><BarChart3 size={20} /> 演算法圖表</h3>
                <span>{activeTopic.english}</span>
              </div>
              <svg className="algorithmChart" viewBox="0 0 520 300" role="img">
                <title>{activeTopic.english} 參數互動圖表</title>
                <rect x="38" y="22" width="330" height="238" rx="10" />
                <line x1="58" y1="240" x2="348" y2="240" />
                <line x1="58" y1="48" x2="58" y2="240" />
                <path d={boundaryPath} className="decisionBoundary" />
                {chartPoints.map((point, index) => (
                  <circle
                    key={`${point.group}-${index}`}
                    className={point.group === "A" ? "pointA" : "pointB"}
                    cx={point.x}
                    cy={point.y}
                    r={point.group === "A" ? 6 : 5}
                  />
                ))}
                {metrics.map((metric, index) => (
                  <g key={metric.label}>
                    <text x="392" y={72 + index * 58}>{metric.label}</text>
                    <rect className="metricTrack" x="392" y={82 + index * 58} width="92" height="12" rx="6" />
                    <rect
                      className="metricFill"
                      x="392"
                      y={82 + index * 58}
                      width={Math.round(metric.value * 0.92)}
                      height="12"
                      rx="6"
                    />
                    <text className="metricValue" x="488" y={93 + index * 58}>{metric.value}%</text>
                  </g>
                ))}
              </svg>
              <p>
                這個圖表用合成資料模擬模型邊界與表現指標，幫你觀察參數改變時可能出現的過度擬合、欠擬合與泛化效果。
              </p>
            </div>
          </section>

          <div className="learningGrid">
            <InfoPanel icon={<Target size={20} />} title="為什麼重要">
              <p>{activeTopic.why}</p>
              <p className="example">例子：{activeTopic.example}</p>
            </InfoPanel>

            <InfoPanel icon={<ListChecks size={20} />} title="學習步驟">
              <ol>
                {activeTopic.steps.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </InfoPanel>

            <InfoPanel icon={<BarChart3 size={20} />} title="優點">
              <ul>
                {activeTopic.strengths.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </InfoPanel>

            <InfoPanel icon={<FlaskConical size={20} />} title="限制">
              <ul>
                {activeTopic.limits.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </InfoPanel>
          </div>

          <section className="quiz">
            <div>
              <h3>課後小測驗</h3>
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
                {isCorrect ? "答對了，觀念很穩。" : `再想想看，正確答案是：${activeTopic.quiz.answer}`}
              </p>
            )}
          </section>

          <section className="assistant">
            <div className="assistantHeader">
              <div>
                <h3><Bot size={20} /> AI 學習助理</h3>
                <p>針對目前的 {activeTopic.english} 課程提問，助理會用繁體中文協助你理解。</p>
              </div>
              <span className="assistantTopic">{activeTopic.english}</span>
            </div>

            <div className="suggestionRow">
              {["請用生活例子解釋", "它適合什麼資料？", "它和其他方法有何差異？"].map(
                (suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => setAssistantQuestion(suggestion)}
                  >
                    {suggestion}
                  </button>
                ),
              )}
            </div>

            <div className="assistantMessages" aria-live="polite">
              {assistantMessages.length === 0 && (
                <p className="assistantEmpty">輸入問題開始對話，例如：「可以用國中生聽得懂的方式解釋嗎？」</p>
              )}
              {assistantMessages.map((message, index) => (
                <div key={`${message.role}-${index}`} className={`assistantMessage ${message.role}`}>
                  <strong>{message.role === "user" ? "你" : "AI 助理"}</strong>
                  <p>{message.content}</p>
                </div>
              ))}
              {assistantLoading && (
                <div className="assistantMessage assistant loading">
                  <LoaderCircle size={18} className="spin" />
                  <p>正在思考...</p>
                </div>
              )}
            </div>

            {assistantError && <p className="assistantError">{assistantError}</p>}

            <form className="assistantForm" onSubmit={submitAssistantQuestion}>
              <textarea
                value={assistantQuestion}
                onChange={(event) => setAssistantQuestion(event.target.value)}
                placeholder="輸入你想問的機器學習問題..."
                maxLength={1000}
                rows={3}
              />
              <button type="submit" disabled={!assistantQuestion.trim() || assistantLoading}>
                <Send size={18} />
                送出問題
              </button>
            </form>
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

function ParameterSlider({
  label,
  value,
  min,
  max,
  unit,
  help,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  unit: string;
  help: string;
  onChange: (value: number) => void;
}) {
  return (
    <label className="parameterControl">
      <span>
        <strong>{label}</strong>
        <b>{value}{unit}</b>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <small>{help}</small>
    </label>
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

function normalizeDifficulty(value: string) {
  if (value.includes("進") || value.includes("難")) {
    return "進階";
  }
  if (value.includes("中")) {
    return "中等";
  }
  return "簡單";
}

function buildChartPoints(
  activeIndex: number,
  complexity: number,
  regularization: number,
  trainingRatio: number,
): ChartPoint[] {
  return Array.from({ length: 24 }, (_, index) => {
    const angle = index * 0.72 + activeIndex * 0.41;
    const spread = 42 + complexity * 0.65 - regularization * 0.18;
    const centerX = index % 2 === 0 ? 132 : 258;
    const centerY = index % 2 === 0 ? 106 : 178;
    const trainingShift = (trainingRatio - 65) * (index % 3 === 0 ? 0.9 : -0.35);
    return {
      x: clamp(centerX + Math.cos(angle) * spread + trainingShift, 70, 340),
      y: clamp(centerY + Math.sin(angle * 1.15) * spread * 0.68, 58, 232),
      group: index % 2 === 0 ? "A" : "B",
    };
  });
}

function buildBoundaryPath(complexity: number, regularization: number) {
  const wiggle = Math.max(4, complexity * 0.32 - regularization * 0.16);
  const midpoint = 148 + (regularization - 40) * 0.25;
  const points = Array.from({ length: 9 }, (_, index) => {
    const x = 72 + index * 33;
    const y = midpoint + Math.sin(index * 1.18) * wiggle + (index - 4) * 7;
    return `${index === 0 ? "M" : "L"} ${x} ${clamp(y, 62, 230)}`;
  });
  return points.join(" ");
}

function buildMetrics(complexity: number, regularization: number, trainingRatio: number) {
  const fit = clamp(Math.round(48 + complexity * 0.48 - regularization * 0.12), 25, 98);
  const generalization = clamp(
    Math.round(62 + trainingRatio * 0.18 + regularization * 0.16 - Math.abs(complexity - 58) * 0.28),
    25,
    98,
  );
  const stability = clamp(Math.round(38 + regularization * 0.42 + trainingRatio * 0.08), 25, 98);
  return [
    { label: "擬合度", value: fit },
    { label: "泛化", value: generalization },
    { label: "穩定度", value: stability },
  ];
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}
