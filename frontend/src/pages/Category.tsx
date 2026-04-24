import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import ModelCard from "../components/ModelCard";
import { api } from "../lib/api";
import type { CategoryDetail, InstallState } from "../lib/types";

export default function Category() {
  const { catId } = useParams<{ catId: string }>();
  const [detail, setDetail] = useState<CategoryDetail | null>(null);
  const [installed, setInstalled] = useState<Record<string, InstallState>>({});

  useEffect(() => {
    if (!catId) return;
    api.category(catId).then(setDetail).catch(() => setDetail(null));
    api.installed().then(setInstalled).catch(() => {});
  }, [catId]);

  if (!detail) {
    return (
      <div className="mx-auto max-w-5xl p-8 text-ink-400">
        Loading…
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl p-8">
      <Link
        to="/"
        className="btn-ghost mb-4 inline-flex items-center gap-1 text-ink-400"
      >
        <ArrowLeft size={16} /> Back
      </Link>
      <header className="mb-8">
        <h1 className="text-2xl font-bold">{detail.title}</h1>
        <p className="mt-1 text-ink-400">{detail.subtitle}</p>
      </header>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {detail.models.map((m) => (
          <ModelCard key={m.id} model={m} install={installed[m.id]} />
        ))}
      </div>
    </div>
  );
}
