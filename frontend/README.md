# Hackathon Todo Application - Frontend

This is the frontend implementation of the Hackathon Todo application built with Next.js, TypeScript, and Tailwind CSS.

## Features

- User authentication (Sign up/Sign in)
- Task management (Create, Read, Update, Delete)
- Task filtering and sorting
- Light/Dark mode support
- Responsive design for all device sizes
- Accessible UI components
- Smooth animations and transitions
- Production-ready for deployment to Vercel

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **UI Components**: Custom-built with Tailwind CSS
- **State Management**: React Hooks
- **Theming**: next-themes
- **Deployment**: Optimized for Vercel

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── auth/               # Authentication pages
│   │   ├── login/
│   │   └── signup/
│   ├── dashboard/          # Main dashboard page
│   └── layout.tsx          # Root layout
├── components/             # Reusable UI components
│   ├── ui/                 # Base UI components
│   └── theme-provider.tsx  # Theme provider
├── lib/                    # Utilities and API client
│   ├── api.ts              # API client
│   └── utils.ts            # Utility functions
├── types/                  # TypeScript type definitions
└── styles/                 # Global styles
```

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Production Deployment (Vercel)

### Prerequisites

- Node.js 18+ installed
- A Vercel account

### Environment Variables

For production deployment, set these environment variables in your Vercel project settings:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.hf.space  # Your deployed backend URL
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-frontend-url.vercel.app  # Your deployed frontend URL
BETTER_AUTH_SECRET=your_auth_secret  # Same as used in backend
```

### Deployment Steps

1. Connect your GitHub repository to Vercel
2. Import your project in the Vercel dashboard
3. Set the build command to `npm run build`
4. Set the output directory to `out`
5. Add the environment variables listed above
6. Click "Deploy" and Vercel will automatically build and deploy your application

### Manual Deployment

If deploying manually:

1. Build the application:
```bash
npm run build
```

2. Preview the build locally:
```bash
npm run start
```

3. Deploy using the Vercel CLI:
```bash
npm i -g vercel
vercel --prod
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run linter

## API Integration

The frontend communicates with the backend through the centralized API client located at `lib/api.ts`. All API requests automatically include the JWT token for authentication when available. In production, API requests are proxied through the Next.js rewrites configured in `next.config.js`.

## Theming

The application supports both light and dark modes. The theme is persisted in local storage and respects the user's system preference by default.

## Component Library

Base UI components are located in `components/ui/` and include:
- Button
- Input
- Modal
- TaskCard
- TaskList
- HeaderNav
- ThemeToggle

All components are built with accessibility in mind and support both light and dark themes.

## Production Considerations

- The application is configured to proxy API requests to the backend in production
- Environment variables prefixed with `NEXT_PUBLIC_` are available in the browser
- Proper error handling and loading states are implemented for all async operations
- Images and assets are optimized for production performance