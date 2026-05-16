/** @type {import('tailwindcss').Config} */
// Tokens mirror frontend/Design.md. Keep them in sync.
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Surfaces
        'app-start':     '#FBF7F3',
        'app-end':       '#F4F2FD',
        surface:         '#FFFFFF',
        'surface-muted': '#F7F7FB',
        subtle:          '#EAEAF1',
        strong:          '#D8D8E3',

        // Text
        'text-strong':   '#0F1024',
        'text-default':  '#1F2330',
        'text-muted':    '#6B7080',
        'text-subtle':   '#9CA0AE',

        // Brand
        primary: {
          400: '#818CF8',
          500: '#6366F1',
          600: '#5457E5',
          soft: '#EEF1FF',
        },

        // Pastel accents for chip icons (Design.md §2)
        accent: {
          mint:  '#A7E0C6',
          peach: '#F6C9B0',
          rose:  '#F4B7C3',
          sky:   '#B7D6F6',
          amber: '#F2D097',
          lilac: '#CFC3F4',
          coral: '#F0A89A',
        },
      },
      boxShadow: {
        card:  '0 1px 2px rgba(15,16,36,0.04), 0 4px 12px rgba(15,16,36,0.05)',
        pop:   '0 8px 24px rgba(99,102,241,0.18)',
        focus: '0 0 0 3px rgba(99,102,241,0.18)',
      },
      borderRadius: {
        'xl-soft': '22px',
      },
      backgroundImage: {
        'app-gradient':    'linear-gradient(135deg, #FBF7F3 0%, #F4F2FD 100%)',
        'primary-gradient':'linear-gradient(135deg, #7C7BFF 0%, #6366F1 100%)',
      },
    },
  },
  plugins: [],
}
