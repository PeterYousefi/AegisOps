import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AegisOps",
  description:
    "Human-Governed AI Incident Response for Cloud Operations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
