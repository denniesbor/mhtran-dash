/*
 * Role: Vite build and dev server configuration.
 * Author: Dennies Bor
 * Description: React + Tailwind v4 plugins. Dev server proxies /api to the
 *   local backend so the frontend never hardcodes ports. Production builds
 *   read the API base from VITE_API_BASE_URL.
 */

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  base: "/",
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8035",
        changeOrigin: true,
      },
    },
  },
});
