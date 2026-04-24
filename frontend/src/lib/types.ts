// Mirrors the Pydantic types in backend/vidify/specs/schema.py

export type Category =
  | "talking-head"
  | "text-to-video"
  | "image-to-video"
  | "character-animation"
  | "motion-transfer"
  | "video-to-video"
  | "enhance";

export type InputKind = "image" | "audio" | "video" | "text";
export type ParamKind = "int" | "float" | "bool" | "string" | "enum" | "seed";

export interface InputField {
  id: string;
  kind: InputKind;
  label: string;
  required: boolean;
  help?: string | null;
  example_url?: string | null;
  accept?: string[] | null;
  max_size_mb?: number | null;
}

export interface ParamField {
  id: string;
  kind: ParamKind;
  label: string;
  help?: string | null;
  default: unknown;
  min?: number | null;
  max?: number | null;
  step?: number | null;
  options?: string[] | null;
  advanced: boolean;
}

export interface WeightSource {
  repo_id: string;
  files?: string[] | null;
  revision?: string | null;
  target_subdir?: string | null;
  approx_size_gb?: number | null;
}

export interface ModelSpec {
  id: string;
  name: string;
  category: Category;
  short_description: string;
  long_description?: string | null;
  license: string;
  homepage?: string | null;
  paper?: string | null;
  inputs: InputField[];
  params: ParamField[];
  output_kind: InputKind;
  weights: WeightSource[];
  vram_gb_min: number;
  vram_gb_recommended: number;
  runner: string;
  status: "stable" | "beta" | "experimental" | "planned";
  tags: string[];
}

export interface CategorySummary {
  id: Category;
  title: string;
  subtitle: string;
  icon?: string | null;
  model_count: number;
}

export interface CategoryDetail extends CategorySummary {
  models: ModelSpec[];
}

export type JobStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled";

export interface Job {
  id: string;
  spec_id: string;
  status: JobStatus;
  progress: number;
  message: string;
  output_path?: string | null;
  created_at: number;
  started_at?: number | null;
  finished_at?: number | null;
  error?: string | null;
}

export interface InstallState {
  status: "not_installed" | "downloading" | "installed" | "failed";
  size_gb?: number | null;
  path?: string | null;
  message?: string | null;
  progress?: number | null;
  progress_message?: string | null;
}
