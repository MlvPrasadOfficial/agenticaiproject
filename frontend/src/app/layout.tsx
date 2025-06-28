import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { QueryProvider } from "@/components/providers/query-provider";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Enterprise Insights Copilot",
  description: "AI-powered data analytics platform with multi-agent intelligence for enterprise insights",
  keywords: ["AI", "Analytics", "Data Science", "Enterprise", "Copilot", "Machine Learning"],
  authors: [{ name: "Enterprise Insights Team" }],
  openGraph: {
    title: "Enterprise Insights Copilot",
    description: "AI-powered data analytics platform with multi-agent intelligence",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} antialiased`}
      >
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
