import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Download } from "lucide-react";
import { api } from "../lib/api";
import type { Job } from "../lib/types";

export default function JobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    if (!jobId) return;
    const refresh = () => api.job(jobId).then(setJob).catch(() => {});
    refresh();
    const t = setInterval(refresh, 1000);
    return () => clearInterval(t);
  }, [jobId]);

  if (!job) {
    return <div className="mx-auto max-w-3xl p-8 text-ink-400">Loading…</div>;
  }
  const finished = job.status === "succeeded" || job.status === "failed";
  const outputUrl = job.status === "succeeded" && jobId ? api.jobOutputUrl(jobId) : null;

  return (
    <div className="mx-auto max-w-3xl p-8">
      <Link to="/jobs" className="btn-ghost mb-4 inline-flex items-center gap-1">
        <ArrowLeft size={16} /> All jobs
      </Link>
      <div className="card p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold">{job.spec_id}</h1>
            <div className="mt-1 text-xs text-ink-500">{job.id}</div>
          </div>
          <span className="chip capitalize">{job.status}</span>
        </div>

        {!finished && (
          <div className="mt-4">
            <div className="h-2 overflow-hidden rounded bg-ink-800">
              <div
                className="h-full bg-accent transition-all"
                style={{ width: `${Math.round(job.progress * 100)}%` }}
              />
            </div>
            <div className="mt-1 text-xs text-ink-500">{job.message}</div>
          </div>
        )}

        {outputUrl && (
          <div className="mt-6">
            <video
              src={outputUrl}
              controls
              className="w-full rounded-lg bg-black"
            />
            <a
              href={outputUrl}
              download
              className="btn-outline mt-3 inline-flex"
            >
              <Download size={16} /> Download MP4
            </a>
          </div>
        )}

        {job.error && (
          <div className="mt-4 rounded-md border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
            {job.error}
          </div>
        )}
      </div>
    </div>
  );
}
