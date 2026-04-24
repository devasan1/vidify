import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Frontend runs on 5173 in dev; proxy API to the FastAPI backend on 7860.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:7860",
      "/outputs": "http://127.0.0.1:7860",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
