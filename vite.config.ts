/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  test: {
    // Only pure game-logic modules have tests so far — no DOM needed.
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
  plugins: [
    vue(),

    VitePWA({
      registerType: "autoUpdate",

      // explicitly listing the sprites via includeAssets
      // due to sprites/obstacle.png not loading properly once offline
      includeAssets: [
        "sprites/plane.png",
        "sprites/glowbolt.svg",
        "sprites/obstacle.png",
      ],

      manifest: {
        name: "Lightning Flight",
        short_name: "Lightning Flight",
        description: "Lightning Fibre Event Game",

        theme_color: "#05030b",
        background_color: "#05030b",

        display: "standalone",
        orientation: "portrait",

        icons: [
          {
            src: "/icons/icon-192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "/icons/icon-512.png",
            sizes: "512x512",
            type: "image/png",
          },
        ],
      },

      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,png,webp,jpg,jpeg,woff,woff2}"],
        cleanupOutdatedCaches: true,
      },
    }),
  ],
});
