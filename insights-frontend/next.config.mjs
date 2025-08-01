/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Enable static export
  distDir: 'out',   // Output directly to out directory
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,  // Required for static export
    domains: ['localhost'],
  },
  // Ensure static export works with app directory
  experimental: {
    appDir: true,
  },
}

export default nextConfig
