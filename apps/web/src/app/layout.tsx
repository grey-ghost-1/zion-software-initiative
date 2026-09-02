import type { Metadata } from "next";
import "@zion/config/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zion Software Initiative",
  description: "A software platform rooted in peace, justice, and human goodwill.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
