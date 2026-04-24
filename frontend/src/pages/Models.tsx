import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import ModelCard from "../components/ModelCard";
import { api } from "../lib/api";
import type { InstallState, ModelSpec } from "../lib/types";

export default function Models() {
  const [models, setModels] = useState<ModelSpec[]>([]);
  const [installed, setInstalled] = useState<Record<string, InstallState>>({});
  const [q, setQ] = useState("");

  useEffect(() => {
    api.models().then(setModels).catch(() => {});
    api.installed().then(setInstalled).catch(() => {});
  }, []);

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    if (!ql) return models;
    return models.filter(
      (m) =>
        m.name.toLowerCase().includes(ql) ||
        m.id.toLowerCase().includes(ql) ||
        m.short_description.toLowerCase().includes(ql) ||
        m.tags.some((t) => t.toLowerCase().includes(ql)) ||
        m.category.toLowerCase().includes(ql),
    );
  }, [q, models]);

  return (
    <div className="mx-auto max-w-6xl p-8">
      <header className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">All models</h1>
          <p className="mt-1 text-ink-400">
            {models.length} models across every category.
          </p>
        </div>
        <div className="relative w-80 max-w-full">
          <Search
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-500"
          />
          <input
            className="input pl-9"
            placeholder="Search models, tags, categories…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </header>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((m) => (
          <ModelCard key={m.id} model={m} install={installed[m.id]} />
        ))}
      </div>
    </div>
  );
}
