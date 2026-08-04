import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SweetGold — 可复现的多智能体 AI 实验室",
  description: "在完全相同的世界中训练、审计和比较蜂群策略；失败实验同样进入记录。",
  alternates: { languages: { en: "/", "zh-CN": "/zh" } },
};

export default function ChineseLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
