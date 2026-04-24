import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  Cpu,
  Download,
  ExternalLink,
  FileText,
  HardDrive,
  Play,
  Scroll,
  Tags,
} from "lucide-react";
import DownloadLogsModal from "../components/DownloadLogsModal";
import InputRenderer, { type FormState } from "../components/InputRenderer";
import { api } from "../lib/api";
import type { InstallState, ModelSpec } from "../lib/types";

export default function Model() {
  const { modelId } = useParams<{ modelId: string }>();
  const navigate = useNavigate();
  const [model, setModel] = useState<ModelSpec | null>(null);
  const [install, setInstall] = useState<InstallState | null>(null);
  const [state, setState] = useState<FormState>({
    texts: {},
    files: {},
    params: {},
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [logsOpen, setLogsOpen] = useState(false);

  useEffect(() => {
    if (!modelId) return;
    api
      .model(modelId)
      .then((m) => {
        setModel(m);
        const params: Record<string, string | number | boolean> = {};
        for (const p of m.params) {
          params[p.id] = (p.default ?? "") as string | number | boolean;
        }
        setState((s) => ({ ...s, params }));
      })
      .catch(() => setModel(null));
  }, [modelId]);

  useEffect(() => {
    if (!modelId) return;
    const refresh = () =>
      api.installed().then((all) => setInstall(all[modelId] ?? null)).catch(() => {});
    refresh();
    const t = setInterval(refresh, 1500);
    return () => clearInterval(t);
  }, [modelId]);

  const totalSize = useMemo(
    () => model?.weights.reduce((s, w) => s + (w.approx_size_gb ?? 0), 0) ?? 0,
    [model],
  );

  if (!model) {
    return <div className="mx-auto max-w-5xl p-8 text-ink-400">Loading…</div>;
  }

  const missingRequiredInputs = model.inputs.filter((i) => {
    if (!i.required) return false;
    return i.kind === "text"
      ? !(state.texts[i.id] ?? "").trim()
      : !state.files[i.id];
  });
  const needsDownload = install?.status !== "installed" && model.weights.length > 0;
  const runnerPlanned = model.status === "planned";

  async function submit() {
    if (!modelId) return;
    setError(null);
    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append("spec_id", modelId);
      fd.append("params", JSON.stringify(state.params));
      fd.append("texts", JSON.stringify(state.texts));
      for (const [id, f] of Object.entries(state.files)) {
        const extMatch = f.name.match(/\.[^.]+$/);
        const ext = extMatch?.[0] ?? "";
        fd.append("files", f, `${id}${ext}`);
      }
      const job = await api.submitJob(fd);
      navigate(`/jobs/${job.id}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  async function startDownload() {
    if (!modelId) return;
    setDownloading(true);
    try {
      await api.downloadModel(modelId);
    } catch (e) {
      setError(String(e));
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl p-8">
      <Link
        to={`/c/${model.category}`}
        className="btn-ghost mb-4 inline-flex items-center gap-1 text-ink-400"
      >
        <ArrowLeft size={16} /> Back to {model.category}
      </Link>

      <header className="card mb-6 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{model.name}</h1>
            <p className="mt-1 text-ink-400">{model.short_description}</p>
            {model.long_description && (
              <p className="mt-3 max-w-3xl text-sm text-ink-400">
                {model.long_description}
              </p>
            )}
          </div>
          <span className="chip capitalize">{model.status}</span>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
          <span className="chip">
            <Cpu size={12} /> {model.vram_gb_recommended} GB VRAM recommended
          </span>
          {totalSize > 0 && (
            <span className="chip">
              <HardDrive size={12} /> {totalSize.toFixed(1)} GB weights
            </span>
          )}
          <span className="chip">
            <Scroll size={12} /> {model.license}
          </span>
          {model.tags.map((t) => (
            <span key={t} className="chip-accent">
              <Tags size={12} /> {t}
            </span>
          ))}
          {model.homepage && (
            <a
              href={model.homepage}
              target="_blank"
              rel="noreferrer"
              className="chip hover:bg-ink-800"
            >
              GitHub <ExternalLink size={12} />
            </a>
          )}
          {model.paper && (
            <a
              href={model.paper}
              target="_blank"
              rel="noreferrer"
              className="chip hover:bg-ink-800"
            >
              Paper <ExternalLink size={12} />
            </a>
          )}
        </div>
      </header>

      {needsDownload && (
        <div className="card mb-6 border-amber-500/30 bg-amber-500/5 p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-sm font-medium text-amber-300">
                <AlertTriangle size={16} />
                Weights not installed
              </div>
              <p className="mt-1 text-sm text-ink-400">
                About {totalSize.toFixed(1)} GB of weights will be downloaded to
                your machine. You can also trigger this from the command line:
                <code className="ml-1 rounded bg-ink-800 px-1 py-0.5 text-xs">
                  python scripts/download_models.py {model.id}
                </code>
              </p>
              {install?.download && install.download.status !== "idle" && (
                <div className="mt-3">
                  <div className="h-2 overflow-hidden rounded bg-ink-800">
                    <div
                      className={`h-full transition-all ${
                        install.download.status === "failed"
                          ? "bg-red-500"
                          : "bg-accent"
                      }`}
                      style={{
                        width: `${Math.round(install.download.progress * 100)}%`,
                      }}
                    />
                  </div>
                  <div className="mt-1 text-xs text-ink-500">
                    {install.download.error ?? install.download.message}
                  </div>
                </div>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <button
                className="btn-primary"
                onClick={() => {
                  startDownload();
                  setLogsOpen(true);
                }}
                disabled={downloading}
              >
                <Download size={16} />
                {downloading ? "Downloading…" : "Download weights"}
              </button>
              {install?.download && install.download.status !== "idle" && (
                <button
                  className="btn-ghost"
                  onClick={() => setLogsOpen(true)}
                  title="View live download logs"
                >
                  <FileText size={14} />
                  View logs
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {logsOpen && model && (
        <DownloadLogsModal
          modelId={model.id}
          modelName={model.name}
          onClose={() => setLogsOpen(false)}
        />
      )}

      {runnerPlanned && (
        <div className="card mb-6 border-blue-500/30 bg-blue-500/5 p-4">
          <div className="flex items-start gap-3 text-sm">
            <AlertTriangle size={16} className="mt-0.5 text-blue-300 shrink-0" />
            <div className="text-ink-300">
              <div className="font-medium text-blue-300">Runner not implemented yet</div>
              <p className="mt-1 text-ink-400">
                Vidify knows the spec for <code>{model.id}</code> — inputs, params, weights, VRAM —
                but the inference runner isn’t wired up yet (spec <code>status={model.status}</code>).
                The downloader works; generation currently only runs for the built-in
                <code className="mx-1">mock-demo</code> model, which produces a sample MP4 via ffmpeg
                so the end-to-end pipeline is testable on any machine (including CPU-only).
                Runners will be added one-by-one behind this same UI.
              </p>
            </div>
          </div>
        </div>
      )}

      <InputRenderer
        inputs={model.inputs}
        params={model.params}
        state={state}
        onChange={setState}
      />

      {error && (
        <div className="card mt-6 border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="sticky bottom-0 mt-8 flex items-center justify-between gap-4 border-t border-ink-800 bg-ink-950/80 py-4 backdrop-blur">
        <div className="text-xs text-ink-500">
          {missingRequiredInputs.length > 0
            ? `Need: ${missingRequiredInputs.map((i) => i.label).join(", ")}`
            : "Ready to run"}
        </div>
        <button
          className="btn-primary"
          disabled={
            missingRequiredInputs.length > 0 ||
            submitting ||
            needsDownload ||
            runnerPlanned
          }
          onClick={submit}
          title={runnerPlanned ? "Runner not implemented yet" : undefined}
        >
          <Play size={16} />{" "}
          {runnerPlanned
            ? "Runner not implemented"
            : submitting
              ? "Submitting…"
              : "Generate"}
        </button>
      </div>
    </div>
  );
}
