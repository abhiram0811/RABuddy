/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://rabuddy.onrender.com/api',
  },
  // Force cache bust - updated timestamp
  generateBuildId: async () => {
    return 'rabuddy-' + Date.now()
  },
}

module.exports = nextConfig
