/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://rabuddy-backend.onrender.com/api',
  },
}

module.exports = nextConfig
