import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 text-center">
      <div className="max-w-3xl space-y-6">
        <div className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
          Digital Career Twin (DCT) v0.1.0
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl">
          Model Your Career. Simulate Your Future.
        </h1>
        <p className="text-lg text-muted-foreground sm:text-xl">
          Calibrate your technical and non-technical proficiencies against real industry demand,
          uncover skill gaps, and execute on dynamic, goal-driven career roadmaps.
        </p>
        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <Link
            href="/dashboard"
            className="rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 transition-colors"
          >
            Open Twin Dashboard
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-input bg-background px-6 py-3 text-sm font-medium hover:bg-accent transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </main>
  );
}
