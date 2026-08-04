import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.includes("localhost") ? "http" : "https");
  const origin = `${protocol}://${host}`;
  return {
    title: "SweetGold — A Reproducible Multi-Agent AI Lab",
    description: "Train, audit and compare bee-colony strategies on identical worlds. SweetGold makes multi-agent AI experiments reproducible—and failures visible.",
    metadataBase: new URL(origin),
    openGraph: {
      title: "SweetGold — Teach a colony to survive the unknown",
      description: "A reproducible multi-agent AI lab with matched-seed arenas, safety gates and honest robustness audits.",
      type: "website",
      images: [{ url: `${origin}/og.png`, width: 1200, height: 630, alt: "SweetGold multi-agent AI lab" }],
    },
    twitter: {
      card: "summary_large_image",
      title: "SweetGold — Teach a colony to survive the unknown",
      description: "Build policies that earn their promotion.",
      images: [`${origin}/og.png`],
    },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
