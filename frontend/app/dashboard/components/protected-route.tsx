'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    // In a real app, this would check for a valid JWT token
    const token = localStorage.getItem('auth-token');

    if (token) {
      // In a real app, you would validate the token here
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
      // Redirect to login page
      router.push('/auth/login');
    }
  }, [router]);

  // Show fallback while checking authentication
  if (isAuthenticated === null) {
    if (fallback) return fallback;
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // If authenticated, render the children
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated, return nothing (router.push will handle redirection)
  return null;
}