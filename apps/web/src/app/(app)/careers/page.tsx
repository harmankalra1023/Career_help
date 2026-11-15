import Link from "next/link";

export default function CareersPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Career Pathways & Roles</h1>
      <p className="text-sm text-muted-foreground">
        Explore matched career pathways ranked by overall fit, market demand, and transferable skills.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/careers/backend-engineer"
          className="rounded-lg border border-border p-4 hover:border-primary transition-colors"
        >
          <div className="flex justify-between items-center">
            <h3 className="font-semibold">Backend Engineer</h3>
            <span className="text-xs font-bold text-primary">76.4% Match</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">High demand in Global & North America</p>
        </Link>
      </div>
    </div>
  );
}
