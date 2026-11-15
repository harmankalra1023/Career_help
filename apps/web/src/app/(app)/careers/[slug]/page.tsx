export default function CareerDetailPage({ params }: { params: { slug: string } }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold capitalize">{params.slug.replace("-", " ")}</h1>
      <p className="text-sm text-muted-foreground">
        Detailed breakdown of required skills, gap closure priorities, and industry market metrics.
      </p>
    </div>
  );
}
