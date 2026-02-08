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
        primary: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
        },
        pending: {
          DEFAULT: '#f59e0b',
          light: '#fef3c7',
        },
        completed: {
          DEFAULT: '#10b981',
          light: '#d1fae5',
        },
        danger: {
          DEFAULT: '#ef4444',
          hover: '#dc2626',
        },
      },
    },
  },
  plugins: [],
}
