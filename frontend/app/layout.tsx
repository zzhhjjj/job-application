import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Role Radar — ML Systems Jobs",
  description:
    "前沿 AI 实验室、NVIDIA 与知名量化公司的 training infra、SFT systems 与 ML systems 岗位看板。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
