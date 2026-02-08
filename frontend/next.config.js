/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable typed routes
  typedRoutes: true,
  // Allow external resources
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
    ],
  },
  // Redirect API calls in production
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*` : 'http://localhost:7860/api/:path*',
      },
    ];
  },

};

module.exports = nextConfig;