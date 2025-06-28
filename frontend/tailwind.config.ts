import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark Theme Base
        dark: {
          primary: "#0a0a0a",
          secondary: "#1a1a1a", 
          tertiary: "#2a2a2a",
        },
        // Glassmorphism
        glass: {
          bg: "rgba(255, 255, 255, 0.05)",
          border: "rgba(255, 255, 255, 0.1)",
          hover: "rgba(255, 255, 255, 0.08)",
        },
        // Accent Colors
        accent: {
          primary: "#00D4FF",    // Cyan blue - AI/Tech
          secondary: "#7C3AED",  // Purple - Intelligence
          tertiary: "#10B981",   // Green - Success/Data
          warning: "#F59E0B",    // Amber - Warnings
          error: "#EF4444",      // Red - Errors
        },
        // Agent-Specific Colors
        agent: {
          planning: "#8B5CF6",   // Planning Agent - Purple
          data: "#06B6D4",       // Data Agent - Cyan
          query: "#10B981",      // Query Agent - Green
          insight: "#F59E0B",    // Insight Agent - Amber
        },
        // Text Colors
        text: {
          primary: "#FFFFFF",
          secondary: "#A1A1AA",
          muted: "#71717A",
        }
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.13)',
        'glass-lg': '0 12px 40px 0 rgba(31, 38, 135, 0.18)',
        'glass-xl': '0 16px 48px 0 rgba(31, 38, 135, 0.25)',
      },
      backdropBlur: {
        'glass': '16px',
        'glass-lg': '20px',
      },
      borderRadius: {
        'xl': '1.25rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config;
