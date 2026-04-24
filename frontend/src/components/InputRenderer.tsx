import { useCallback, useState } from "react";
import { FileAudio, FileImage, FileVideo, Info, Type, Upload } from "lucide-react";
import type { InputField, InputKind, ParamField } from "../lib/types";

function kindIcon(kind: InputKind) {
  switch (kind) {
    case "image":
      return <FileImage size={18} />;
    case "audio":
      return <FileAudio size={18} />;
    case "video":
      return <FileVideo size={18} />;
    case "text":
      return <Type size={18} />;
    default:
      return <Upload size={18} />;
  }
}

export interface FormState {
  texts: Record<string, string>;
  files: Record<string, File>;
  params: Record<string, string | number | boolean>;
}

interface Props {
  inputs: InputField[];
  params: ParamField[];
  state: FormState;
  onChange: (s: FormState) => void;
}

export default function InputRenderer({ inputs, params, state, onChange }: Props) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const setText = useCallback(
    (id: string, v: string) =>
      onChange({ ...state, texts: { ...state.texts, [id]: v } }),
    [state, onChange],
  );
  const setFile = useCallback(
    (id: string, f: File | null) => {
      const files = { ...state.files };
      if (f) files[id] = f;
      else delete files[id];
      onChange({ ...state, files });
    },
    [state, onChange],
  );
  const setParam = useCallback(
    (id: string, v: string | number | boolean) =>
      onChange({ ...state, params: { ...state.params, [id]: v } }),
    [state, onChange],
  );

  const basicParams = params.filter((p) => !p.advanced);
  const advancedParams = params.filter((p) => p.advanced);

  return (
    <div className="space-y-6">
      <section>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-400">
          Inputs
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          {inputs.map((inp) => (
            <div key={inp.id} className="card p-4">
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <label className="label mb-0.5 flex items-center gap-2 text-ink-100">
                    {kindIcon(inp.kind)}
                    {inp.label}
                    {!inp.required && (
                      <span className="text-xs font-normal text-ink-500">
                        (optional)
                      </span>
                    )}
                  </label>
                  <div className="text-xs text-ink-500">{inp.id}</div>
                </div>
                {inp.kind !== "text" && (
                  <span className="chip">{inp.kind}</span>
                )}
              </div>
              {inp.kind === "text" ? (
                <textarea
                  className="input min-h-[80px] resize-y"
                  placeholder={inp.help ?? "Type here…"}
                  value={state.texts[inp.id] ?? ""}
                  onChange={(e) => setText(inp.id, e.target.value)}
                />
              ) : (
                <FileDrop
                  field={inp}
                  file={state.files[inp.id]}
                  onFile={(f) => setFile(inp.id, f)}
                />
              )}
              {inp.help && (
                <p className="help flex items-start gap-1">
                  <Info size={12} className="mt-0.5 shrink-0" />
                  <span>{inp.help}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      </section>

      {basicParams.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-400">
            Settings
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {basicParams.map((p) => (
              <ParamControl
                key={p.id}
                p={p}
                value={state.params[p.id] ?? (p.default as string)}
                onChange={(v) => setParam(p.id, v)}
              />
            ))}
          </div>
        </section>
      )}

      {advancedParams.length > 0 && (
        <section>
          <button
            type="button"
            className="btn-ghost"
            onClick={() => setShowAdvanced((x) => !x)}
          >
            {showAdvanced ? "Hide" : "Show"} advanced settings
          </button>
          {showAdvanced && (
            <div className="mt-3 grid gap-4 md:grid-cols-2">
              {advancedParams.map((p) => (
                <ParamControl
                  key={p.id}
                  p={p}
                  value={state.params[p.id] ?? (p.default as string)}
                  onChange={(v) => setParam(p.id, v)}
                />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function FileDrop({
  field,
  file,
  onFile,
}: {
  field: InputField;
  file: File | undefined;
  onFile: (f: File | null) => void;
}) {
  const accept = (field.accept ?? []).join(",");

  return (
    <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-ink-700 bg-ink-950 p-4 text-center transition hover:border-accent/60 hover:bg-ink-900">
      {file ? (
        <FilePreview file={file} kind={field.kind} />
      ) : (
        <>
          <Upload size={18} className="text-ink-500" />
          <div className="text-sm text-ink-300">
            Drop a file or click to select
          </div>
          {field.accept && (
            <div className="text-xs text-ink-500">
              {field.accept.join(" · ")}
            </div>
          )}
        </>
      )}
      <input
        type="file"
        accept={accept || undefined}
        className="hidden"
        onChange={(e) => onFile(e.target.files?.[0] ?? null)}
      />
    </label>
  );
}

function FilePreview({ file, kind }: { file: File; kind: InputKind }) {
  const url = URL.createObjectURL(file);
  return (
    <div className="flex w-full flex-col items-center gap-2">
      {kind === "image" && (
        <img
          src={url}
          alt="preview"
          className="max-h-40 rounded-md object-contain"
        />
      )}
      {kind === "video" && (
        <video
          src={url}
          controls
          className="max-h-40 w-full rounded-md"
        />
      )}
      {kind === "audio" && <audio src={url} controls className="w-full" />}
      <div className="text-xs text-ink-400">
        {file.name} · {(file.size / 1024 / 1024).toFixed(1)} MB
      </div>
    </div>
  );
}

function ParamControl({
  p,
  value,
  onChange,
}: {
  p: ParamField;
  value: string | number | boolean;
  onChange: (v: string | number | boolean) => void;
}) {
  return (
    <div>
      <label className="label">
        {p.label}
        {p.min !== null && p.min !== undefined && p.max !== null && p.max !== undefined && (
          <span className="ml-2 text-xs font-normal text-ink-500">
            ({p.min} – {p.max})
          </span>
        )}
      </label>
      {p.kind === "bool" ? (
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
            className="h-4 w-4 rounded border-ink-700 bg-ink-900 text-accent"
          />
          <span className="text-sm text-ink-300">{p.help ?? p.label}</span>
        </div>
      ) : p.kind === "enum" ? (
        <select
          className="input"
          value={String(value)}
          onChange={(e) => onChange(e.target.value)}
        >
          {p.options?.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : p.kind === "int" || p.kind === "float" || p.kind === "seed" ? (
        <div className="flex items-center gap-3">
          {p.min !== null &&
            p.min !== undefined &&
            p.max !== null &&
            p.max !== undefined && (
              <input
                type="range"
                min={p.min}
                max={p.max}
                step={p.step ?? 1}
                value={Number(value ?? 0)}
                onChange={(e) => onChange(Number(e.target.value))}
                className="flex-1 accent-[#8b5cf6]"
              />
            )}
          <input
            type="number"
            className="input w-24"
            value={Number(value ?? 0)}
            step={p.step ?? 1}
            min={p.min ?? undefined}
            max={p.max ?? undefined}
            onChange={(e) => onChange(Number(e.target.value))}
          />
        </div>
      ) : (
        <input
          className="input"
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      )}
      {p.help && p.kind !== "bool" && <div className="help">{p.help}</div>}
    </div>
  );
}
