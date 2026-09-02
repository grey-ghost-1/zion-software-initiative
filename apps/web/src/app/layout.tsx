import type { Metadata } from "next";
import "@zion/config/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zion Software Initiative",
  description:
    "A foundation-stage social-impact initiative hub and software-engineering portfolio.",
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
