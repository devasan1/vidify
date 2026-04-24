import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import type { Job } from "../lib/types";

const STATUS_TONE: Record<Job["status"], string> = {
  queued: "text-ink-400",
  running: "text-sky-400",
  succeeded: "text-emerald-400",
  failed: "text-red-400",
  cancelled: "text-amber-400",
};

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  useEffect(() => {
    const refresh = () => api.jobs().then(setJobs).catch(() => {});
    refresh();
    const t = setInterval(refresh, 1500);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="mx-auto max-w-5xl p-8">
      <h1 className="text-2xl font-bold">Jobs</h1>
      <p className="mt-1 text-ink-400">Every generation you've kicked off.</p>
      <div className="mt-6 space-y-2">
        {jobs.length === 0 && (
          <div className="card p-8 text-center text-ink-500">
            No jobs yet. Pick a model on the home page to start generating.
          </div>
        )}
        {jobs.map((j) => (
          <Link
            key={j.id}
            to={`/jobs/${j.id}`}
            className="card flex items-center justify-between p-4 hover:border-accent/60"
          >
            <div>
              <div className="text-sm font-medium">{j.spec_id}</div>
              <div className="mt-0.5 text-xs text-ink-500">{j.id}</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-40">
                <div className="h-1.5 overflow-hidden rounded bg-ink-800">
                  <div
                    className="h-full bg-accent"
                    style={{ width: `${Math.round(j.progress * 100)}%` }}
                  />
                </div>
                <div className="mt-0.5 truncate text-xs text-ink-500">
                  {j.message}
                </div>
              </div>
              <div className={`text-sm ${STATUS_TONE[j.status]}`}>{j.status}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
