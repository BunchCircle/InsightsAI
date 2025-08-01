/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Enable static export
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
  // Disable server-side features since we're doing static export
  experimental: {
    appDir: true,
  },
}

export default nextConfig
