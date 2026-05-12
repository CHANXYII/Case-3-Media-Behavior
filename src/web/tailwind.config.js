module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { 0: "#FAFAF9", 1: "#FFFFFF", 2: "#F5F5F4", 3: "#E7E5E4" },
        ink: { 0: "#0C0A09", 1: "#292524", 2: "#57534E", 3: "#A8A29E" },
        accent: {
          gold: "#C2410C",
          copper: "#9A3412",
          espresso: "#7C2D12",
          cream: "#FFEDD5",
          jade: "#15803D",
          ruby: "#B91C1C",
          violet: "#6D28D9"
        }
      },
      fontFamily: {
        display: ["'Space Grotesk'", "'Inter'", "'IBM Plex Sans Thai'", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["'Inter'", "'IBM Plex Sans Thai'", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"]
      },
      boxShadow: {
        soft: "0 1px 2px 0 rgba(12,10,9,0.04), 0 1px 3px 0 rgba(12,10,9,0.06)",
        card: "0 1px 2px 0 rgba(12,10,9,0.04)"
      }
    }
  },
  plugins: []
};
