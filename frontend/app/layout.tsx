import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Top10 機器學習互動學習",
  description: "以 Next.js + FastAPI 製作的十大機器學習演算法互動教材"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
