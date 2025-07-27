/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        csu: {
          green: '#1E4D2B',
          gold: '#C8B99C',
          orange: '#C8102E',
        },
      },
    },
  },
  plugins: [],
}
