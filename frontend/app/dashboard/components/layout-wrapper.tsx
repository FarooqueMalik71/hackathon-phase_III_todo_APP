'use client';

import { ReactNode } from 'react';
import { ThemeProvider } from 'next-themes';

interface LayoutWrapperProps {
  children: ReactNode;
}

export default function LayoutWrapper({ children }: LayoutWrapperProps) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <div className="min-h-screen bg-background text-text-primary">
        {children}
      </div>
    </ThemeProvider>
  );
}