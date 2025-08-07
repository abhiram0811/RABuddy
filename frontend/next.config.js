/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://6c3861215b0a.ngrok-free.app',
  },
  // Force cache bust - updated timestamp
  generateBuildId: async () => {
    return 'rabuddy-' + Date.now()
  },
}

module.exports = nextConfig
