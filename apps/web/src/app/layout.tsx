import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Digital Career Twin",
  description: "Evidence-based career intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
