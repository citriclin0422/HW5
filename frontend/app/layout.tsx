import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "十大機器學習演算法互動平台",
  description: "使用 Next.js 與 FastAPI 製作的十大機器學習演算法互動學習平台。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
