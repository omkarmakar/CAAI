import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CAAI Dashboard - AI Agent System",
  description: "Professional CA AI Agent System Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
