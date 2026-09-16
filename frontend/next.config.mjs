/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Emit a minimal standalone server bundle for the production Docker image.
  output: "standalone",
};

export default nextConfig;
