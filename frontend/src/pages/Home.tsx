import { useEffect, useState } from "react";
import CategoryCard from "../components/CategoryCard";
import { api } from "../lib/api";
import type { CategorySummary } from "../lib/types";

export default function Home() {
  const [cats, setCats] = useState<CategorySummary[] | null>(null);
  const [gpu, setGpu] = useState<{ available: boolean; backend: string } | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api.categories().then(setCats).catch((e) => setErr(String(e)));
    api.health().then((h) => setGpu(h.gpu)).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-5xl p-8">
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight">What do you want to make?</h1>
        <p className="mt-2 text-ink-400">
          Pick a category. Each one lists the open-source models we support, with
          the inputs and parameters they expose.
        </p>
        {gpu && (
          <div className="mt-3 text-xs text-ink-500">
            GPU:{" "}
            <span className={gpu.available ? "text-emerald-400" : "text-amber-400"}>
              {gpu.available ? gpu.backend : "not detected — only CPU-capable models will work"}
            </span>
          </div>
        )}
      </header>

      {err && (
        <div className="card mb-6 border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          Backend unreachable: {err}
        </div>
      )}

      {cats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cats.map((c) => (
            <CategoryCard key={c.id} cat={c} />
          ))}
        </div>
      )}
    </div>
  );
}
