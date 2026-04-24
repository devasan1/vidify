import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Download, FileText, Trash2 } from "lucide-react";
import { api } from "../lib/api";
import type { InstallState, ModelSpec } from "../lib/types";
import DownloadLogsModal from "../components/DownloadLogsModal";

export default function Installed() {
  const [models, setModels] = useState<ModelSpec[]>([]);
  const [state, setState] = useState<Record<string, InstallState>>({});
  const [logsFor, setLogsFor] = useState<ModelSpec | null>(null);

  useEffect(() => {
    api.models().then(setModels).catch(() => {});
    const refresh = () => api.installed().then(setState).catch(() => {});
    refresh();
    const t = setInterval(refresh, 1500);
    return () => clearInterval(t);
  }, []);

  const totalInstalledGb = Object.values(state)
    .filter((s) => s.status === "installed")
    .reduce((sum, s) => sum + (s.size_gb ?? 0), 0);

  return (
    <div className="mx-auto max-w-6xl p-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Model manager</h1>
          <p className="mt-1 text-ink-400">
            Download, remove, and see the disk footprint of every model.
          </p>
        </div>
        <div className="text-sm text-ink-400">
          Installed:{" "}
          <span className="font-semibold text-ink-100">
            {totalInstalledGb.toFixed(1)} GB
          </span>
        </div>
      </header>

      <div className="card divide-y divide-ink-800">
        {models.map((m) => {
          const s = state[m.id];
          const installed = s?.status === "installed";
          const dl = s?.download ?? null;
          const running = dl?.status === "running";
          const failed = dl?.status === "failed";
          const pct = Math.round((dl?.progress ?? 0) * 100);
          return (
            <div key={m.id} className="flex items-center justify-between gap-4 p-4">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-ink-100">{m.name}</span>
                  <span className="text-xs text-ink-500">· {m.category}</span>
                  {failed && (
                    <span className="chip bg-red-500/20 text-red-300">
                      <AlertTriangle size={12} /> failed
                    </span>
                  )}
                </div>
                <div className="mt-0.5 truncate text-xs text-ink-500">
                  {m.id} · {m.license}
                </div>
                {(running || failed) && (
                  <div className="mt-2 w-full max-w-md">
                    <div className="h-1.5 overflow-hidden rounded bg-ink-800">
                      <div
                        className={`h-full ${
                          failed ? "bg-red-500" : "bg-accent"
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="mt-0.5 text-xs text-ink-500">
                      {dl?.error ?? dl?.message}
                    </div>
                  </div>
                )}
              </div>
              <div className="text-xs text-ink-400">
                {installed
                  ? `${s?.size_gb?.toFixed(1) ?? "?"} GB`
                  : `~${m.weights
                      .reduce((a, w) => a + (w.approx_size_gb ?? 0), 0)
                      .toFixed(1)} GB`}
              </div>
              {(running || failed || installed) && dl != null && (
                <button
                  className="btn-ghost"
                  onClick={() => setLogsFor(m)}
                  title="View download logs"
                >
                  <FileText size={16} />
                  Logs
                </button>
              )}
              {installed ? (
                <button
                  className="btn-ghost"
                  onClick={() => api.removeModel(m.id)}
                  title="Remove weights"
                >
                  <Trash2 size={16} />
                </button>
              ) : (
                <button
                  className="btn-primary"
                  onClick={() => {
                    api.downloadModel(m.id).catch(() => {});
                    setLogsFor(m);
                  }}
                  disabled={running}
                >
                  <Download size={16} />
                  {running ? "Downloading" : failed ? "Retry" : "Download"}
                </button>
              )}
              {installed && (
                <CheckCircle2 size={18} className="text-emerald-400" />
              )}
            </div>
          );
        })}
      </div>

      {logsFor && (
        <DownloadLogsModal
          modelId={logsFor.id}
          modelName={logsFor.name}
          onClose={() => setLogsFor(null)}
        />
      )}
    </div>
  );
}
