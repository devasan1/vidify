import { useEffect, useState } from "react";
import { Check, KeyRound, ExternalLink, Trash2 } from "lucide-react";
import { api } from "../lib/api";

type TokenStatus = {
  configured: boolean;
  sources: string[];
  masked: string | null;
};

export default function Settings() {
  const [status, setStatus] = useState<TokenStatus | null>(null);
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const reload = () => {
    api.hfTokenStatus().then(setStatus).catch((e) => setErr(String(e)));
  };

  useEffect(reload, []);

  const save = async () => {
    setErr(null);
    setBusy(true);
    try {
      const s = await api.setHfToken(token.trim());
      setStatus(s);
      setToken("");
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  const clear = async () => {
    setErr(null);
    setBusy(true);
    try {
      const s = await api.clearHfToken();
      setStatus(s);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-ink-400 mt-1">
          Credentials and preferences. Stored locally at{" "}
          <code className="text-ink-200">~/.vidify/config.json</code>.
        </p>
      </div>

      <section className="card space-y-5">
        <header className="flex items-center gap-3">
          <div className="rounded-lg bg-accent/15 p-2 text-accent">
            <KeyRound size={20} />
          </div>
          <div>
            <h2 className="text-lg font-semibold">HuggingFace token</h2>
            <p className="text-sm text-ink-400">
              Needed to download gated / restricted model weights automatically
              (HunyuanVideo, SVD, Wan, Hallo2, ...).
            </p>
          </div>
        </header>

        {status?.configured ? (
          <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4 text-sm text-emerald-300 flex items-start gap-3">
            <Check size={18} className="mt-0.5 shrink-0" />
            <div className="flex-1">
              <div className="font-medium">Configured</div>
              <div className="text-emerald-400/80 mt-0.5">
                <code>{status.masked}</code> · source:{" "}
                {status.sources.join(", ")}
              </div>
            </div>
            <button
              className="btn-ghost"
              onClick={clear}
              disabled={busy}
              title="Clear the saved token"
            >
              <Trash2 size={16} />
              Clear
            </button>
          </div>
        ) : (
          <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-300">
            Not configured. Open-access models will still download, but gated
            ones (HunyuanVideo, SVD, Wan, ...) will fail until you paste a
            token.
          </div>
        )}

        <div className="space-y-2">
          <label className="label">Paste token</label>
          <div className="flex gap-2">
            <input
              type="password"
              className="input flex-1"
              placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && token.trim() && save()}
            />
            <button
              className="btn-primary"
              onClick={save}
              disabled={busy || !token.trim()}
            >
              Save
            </button>
          </div>
          <p className="help">
            Create a read-only token at{" "}
            <a
              href="https://huggingface.co/settings/tokens"
              target="_blank"
              rel="noreferrer"
              className="text-accent hover:underline inline-flex items-center gap-1"
            >
              huggingface.co/settings/tokens
              <ExternalLink size={12} />
            </a>
            . Stored locally with <code>chmod 600</code>; never sent anywhere
            other than HuggingFace.
          </p>
        </div>

        {err && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3 text-sm text-red-300">
            {err}
          </div>
        )}
      </section>
    </div>
  );
}
