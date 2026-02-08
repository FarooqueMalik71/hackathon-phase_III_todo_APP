# Next.js Skill

## Overview
Next.js is a React-based full-stack web development framework that enables functionality such as hybrid static & server rendering, TypeScript support, smart bundling, route pre-fetching, and more. This skill provides expertise in Next.js development practices.

## Key Capabilities
- **Routing**: Understanding of App Router vs Pages Router conventions
- **Server-Side Rendering**: SSR, SSG, ISR implementation
- **TypeScript Integration**: Proper typing for components, props, and API routes
- **Performance Optimization**: Code splitting, image optimization, lazy loading
- **Styling**: CSS Modules, Tailwind CSS, styled-jsx integration
- **Data Fetching**: fetch(), SWR, React Query patterns
- **Deployment**: Vercel, Node.js, and other hosting solutions

## Best Practices
- Use the App Router (`app/` directory) for new projects
- Leverage React Server Components for better performance
- Implement proper error boundaries and loading states
- Use environment variables for configuration
- Follow accessibility guidelines (WCAG)
- Implement proper SEO practices (metadata, structured data)

## File Structure Conventions
- `/app` - Page components using the App Router
- `/components` - Reusable React components
- `/lib` - Utility functions and shared logic
- `/public` - Static assets
- `/styles` - Global stylesheets
- `/types` - TypeScript type definitions

## Common Patterns
- Client components (`'use client'`) for interactivity
- Server components (default) for data fetching and initial render
- Component composition over inheritance
- Hooks for reusable logic
- Proper prop drilling vs context management