import Link from "next/link";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/profile", label: "Profile" },
  { href: "/skills", label: "Skills" },
  { href: "/assessments", label: "Assessments" },
  { href: "/dna", label: "Career DNA" },
  { href: "/careers", label: "Careers" },
  { href: "/gaps", label: "Skill Gaps" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/simulator", label: "Simulator" },
  { href: "/mentor", label: "AI Mentor" },
  { href: "/market", label: "Market Intel" },
  { href: "/settings", label: "Settings" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-card/80 backdrop-blur">
        <div className="container mx-auto flex h-14 items-center justify-between px-4">
          <div className="flex items-center space-x-6">
            <Link href="/dashboard" className="text-lg font-bold tracking-tight text-primary">
              Digital Career Twin
            </Link>
            <nav className="hidden md:flex space-x-4 text-sm font-medium">
              {NAV_LINKS.slice(0, 7).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <nav className="hidden lg:flex space-x-4 text-sm font-medium">
              {NAV_LINKS.slice(7).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
              AJ
            </div>
          </div>
        </div>
      </header>
      <main className="flex-1 container mx-auto px-4 py-6">{children}</main>
    </div>
  );
}
