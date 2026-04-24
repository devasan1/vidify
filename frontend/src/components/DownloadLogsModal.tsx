import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import { api } from "../lib/api";

interface Props {
  modelId: string;
  modelName: string;
  onClose: () => void;
}

type DL = Awaited<ReturnType<typeof api.downloadLogs>>;

export default function DownloadLogsModal({
  modelId,
  modelName,
  onClose,
}: Props) {
  const [state, setState] = useState<DL | null>(null);
  const cursorRef = useRef(0);
  const logsRef = useRef<{ at: number; line: string }[]>([]);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const s = await api.downloadLogs(modelId, cursorRef.current);
        if (cancelled) return;
        if (cursorRef.current === 0) {
          logsRef.current = s.logs;
        } else if (s.logs.length) {
          logsRef.current = [...logsRef.current, ...s.logs];
        }
        cursorRef.current = s.cursor;
        setState({ ...s, logs: logsRef.current });
        // auto-scroll to bottom
        const el = scrollRef.current;
        if (el) el.scrollTop = el.scrollHeight;
      } catch {
        /* ignore */
      }
    };
    tick();
    const i = setInterval(tick, 1000);
    return () => {
      cancelled = true;
      clearInterval(i);
    };
  }, [modelId]);

  const pct = state ? Math.round(state.progress * 100) : 0;
  const statusBadge = (() => {
    if (!state) return null;
    const colors: Record<string, string> = {
      idle: "bg-ink-800 text-ink-400",
      running: "bg-accent/20 text-accent-muted",
      succeeded: "bg-emerald-500/20 text-emerald-300",
      failed: "bg-red-500/20 text-red-300",
    };
    return (
      <span className={`chip ${colors[state.status] || colors.idle}`}>
        {state.status}
      </span>
    );
  })();

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-3xl rounded-xl border border-ink-800 bg-ink-950 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center gap-3 border-b border-ink-800 p-4">
          <div className="flex-1">
            <h2 className="text-lg font-semibold">Download · {modelName}</h2>
            <p className="text-xs text-ink-500">{modelId}</p>
          </div>
          {statusBadge}
          <button
            onClick={onClose}
            className="rounded-md p-1 text-ink-400 hover:bg-ink-800 hover:text-ink-100"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </header>

        <div className="border-b border-ink-800 p-4 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="text-ink-300">{state?.message || "Idle"}</div>
            <div className="font-mono text-ink-400">{pct}%</div>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-ink-800">
            <div
              className={`h-full transition-all ${
                state?.status === "failed" ? "bg-red-500" : "bg-accent"
              }`}
              style={{ width: `${pct}%` }}
            />
          </div>
          {state?.error && (
            <div className="mt-2 rounded-md border border-red-500/30 bg-red-500/5 p-3 text-sm text-red-300">
              {state.error}
            </div>
          )}
        </div>

        <div
          ref={scrollRef}
          className="h-80 overflow-y-auto bg-black/40 p-4 font-mono text-xs leading-relaxed"
        >
          {state?.logs?.length ? (
            state.logs.map((l, i) => (
              <div
                key={`${l.at}-${i}`}
                className="whitespace-pre-wrap text-ink-300"
              >
                <span className="text-ink-600 mr-2">
                  {fmtTime(l.at)}
                </span>
                {l.line}
              </div>
            ))
          ) : (
            <div className="text-ink-600">No logs yet.</div>
          )}
        </div>

        <footer className="flex items-center justify-between border-t border-ink-800 p-3 text-xs text-ink-500">
          <div>Streaming live · updates every second</div>
          <button onClick={onClose} className="btn-ghost">
            Close
          </button>
        </footer>
      </div>
    </div>
  );
}

function fmtTime(ts: number) {
  const d = new Date(ts * 1000);
  const hh = d.getHours().toString().padStart(2, "0");
  const mm = d.getMinutes().toString().padStart(2, "0");
  const ss = d.getSeconds().toString().padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
}
