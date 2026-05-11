/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  experimental: { optimizePackageImports: ["recharts", "lucide-react"] }
};
module.exports = nextConfig;
