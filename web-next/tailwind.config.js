/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { 0: "#0A0907", 1: "#13110D", 2: "#1B1814", 3: "#252019" },
        ink: { 0: "#F4EFE6", 1: "#D9D2C2", 2: "#9A917F", 3: "#5C5547" },
        accent: {
          gold: "#E0A458",
          copper: "#C77B3C",
          espresso: "#7A4520",
          cream: "#F4DBA5",
          jade: "#5BB89A",
          ruby: "#D85A5A",
          violet: "#8B7AD0"
        }
      },
      fontFamily: {
        display: ["'IBM Plex Sans Thai'", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["'IBM Plex Sans Thai'", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"]
      },
      boxShadow: {
        glow: "0 0 60px -15px rgba(224,164,88,0.45)",
        soft: "0 10px 40px -20px rgba(0,0,0,0.6)"
      },
      backgroundImage: {
        grain: "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.04) 1px, transparent 0)"
      }
    }
  },
  plugins: []
};
