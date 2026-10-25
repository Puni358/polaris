import colors from "tailwindcss/colors";

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@tremor/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    transparent: "transparent",
    current: "currentColor",
    extend: {
      /* ------------------------------------------------------------------
       * Typography: Geist for UI, Geist Mono for every data value.
       * Fonts are loaded from App.jsx (or move the @import to index.html).
       * ---------------------------------------------------------------- */
      fontFamily: {
        sans: [
          "Geist",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          '"Geist Mono"',
          '"JetBrains Mono"',
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          '"Liberation Mono"',
          "monospace",
        ],
      },

      /* ------------------------------------------------------------------
       * Tremor tokens. Light and dark palettes are intentionally identical
       * so every Tremor component renders dark regardless of the `dark`
       * class, with translucent hairline borders instead of solid slate.
       * ---------------------------------------------------------------- */
      colors: {
        tremor: {
          brand: {
            faint: "#08181f",
            muted: colors.cyan[950],
            subtle: colors.cyan[700],
            DEFAULT: colors.cyan[400],
            emphasis: colors.cyan[300],
            inverted: colors.zinc[950],
          },
          background: {
            muted: "#09090b",
            subtle: "#0f0f12",
            DEFAULT: "#0c0c0f",
            emphasis: colors.zinc[900],
          },
          border: { DEFAULT: "rgba(255,255,255,0.07)" },
          ring: { DEFAULT: "rgba(255,255,255,0.07)" },
          content: {
            subtle: colors.zinc[500],
            DEFAULT: colors.zinc[400],
            emphasis: colors.zinc[200],
            strong: "#ffffff",
            inverted: colors.zinc[950],
          },
        },
        "dark-tremor": {
          brand: {
            faint: "#08181f",
            muted: colors.cyan[950],
            subtle: colors.cyan[700],
            DEFAULT: colors.cyan[400],
            emphasis: colors.cyan[300],
            inverted: colors.zinc[950],
          },
          background: {
            muted: "#09090b",
            subtle: "#0f0f12",
            DEFAULT: "#0c0c0f",
            emphasis: colors.zinc[900],
          },
          border: { DEFAULT: "rgba(255,255,255,0.07)" },
          ring: { DEFAULT: "rgba(255,255,255,0.07)" },
          content: {
            subtle: colors.zinc[500],
            DEFAULT: colors.zinc[400],
            emphasis: colors.zinc[200],
            strong: "#ffffff",
            inverted: colors.zinc[950],
          },
        },
      },

      /* Tremor's own shadows stay off; our glows are explicit utilities. */
      boxShadow: {
        "tremor-input": "none",
        "tremor-card": "none",
        "tremor-dropdown": "0 16px 40px -12px rgba(0,0,0,0.8)",
        "dark-tremor-input": "none",
        "dark-tremor-card": "none",
        "dark-tremor-dropdown": "0 16px 40px -12px rgba(0,0,0,0.8)",

        panel:
          "inset 0 1px 0 0 rgba(255,255,255,0.05), 0 24px 48px -28px rgba(0,0,0,0.9)",
        "glow-cyan": "0 0 24px -4px rgba(34,211,238,0.40)",
        "glow-rose": "0 0 24px -4px rgba(244,63,94,0.45)",
        "glow-emerald": "0 0 24px -6px rgba(52,211,153,0.50)",
        "glow-violet": "0 0 40px -10px rgba(139,92,246,0.55)",
      },

      borderRadius: {
        "tremor-small": "0.5rem",
        "tremor-default": "0.75rem",
        "tremor-full": "9999px",
      },

      fontSize: {
        "tremor-label": ["0.6875rem", { lineHeight: "1rem" }],
        "tremor-default": ["0.8125rem", { lineHeight: "1.25rem" }],
        "tremor-title": ["1rem", { lineHeight: "1.5rem" }],
        "tremor-metric": ["1.875rem", { lineHeight: "2.25rem" }],
      },

      /* Layered page depth: aurora washes + a faint engineering grid. */
      backgroundImage: {
        aurora:
          "radial-gradient(60% 45% at 50% -8%, rgba(34,211,238,0.10), transparent 70%), radial-gradient(38% 38% at 100% 0%, rgba(99,102,241,0.13), transparent 70%), radial-gradient(45% 40% at 0% 100%, rgba(139,92,246,0.08), transparent 70%)",
        "grid-faint":
          "linear-gradient(to right, rgba(255,255,255,0.028) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.028) 1px, transparent 1px)",
      },

      keyframes: {
        breathe: {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        breathe: "breathe 4.5s ease-in-out infinite",
      },
    },
  },

  /* Tremor builds chart colors dynamically (e.g. `fill-indigo-500`), so the
   * palettes used by this dashboard are safelisted. Add a color name here if
   * you introduce a new one in a chart. */
  safelist: [
    {
      pattern:
        /^(bg|text|border|ring|stroke|fill)-(slate|zinc|neutral|cyan|sky|blue|indigo|violet|fuchsia|rose|red|amber|emerald)-(50|100|200|300|400|500|600|700|800|900|950)$/,
      variants: ["hover", "ui-selected", "data-[selected]"],
    },
  ],
  plugins: [],
};
