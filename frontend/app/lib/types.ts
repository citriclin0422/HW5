export type Topic = {
  slug: string;
  title: string;
  english: string;
  family: string;
  difficulty: "入門" | "中階" | "進階";
  summary: string;
  why: string;
  steps: string[];
  strengths: string[];
  limits: string[];
  example: string;
  quiz: {
    question: string;
    options: string[];
    answer: string;
  };
};
