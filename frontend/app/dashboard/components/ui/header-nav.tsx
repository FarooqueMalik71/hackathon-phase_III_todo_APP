'use client';

import { Button } from '@/app/dashboard/components/ui/button';
import { ThemeToggle } from '@/app/dashboard/components/ui/theme-toggle';
import { LogOutIcon, MenuIcon, UserIcon, MessageCircleIcon } from 'lucide-react';
import { useState } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
}

interface HeaderNavProps {
  user?: User;
  currentPage?: string;
  onLogout?: () => void;
}

export function HeaderNav({ user, currentPage, onLogout }: HeaderNavProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-10 bg-background border-b border-border shadow-sm">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl p-2 shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary">TaskFlow</h1>
            <p className="text-xs text-text-secondary hidden sm:block">Manage your tasks efficiently</p>
          </div>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <a href="/" className={`transition-colors duration-200 ${currentPage === 'dashboard' ? 'text-primary-500 font-medium' : 'text-text-secondary hover:text-primary-500'}`}>
            Dashboard
          </a>
          <a href="/chat" className={`flex items-center gap-1.5 transition-colors duration-200 ${currentPage === 'chat' ? 'text-primary-500 font-medium' : 'text-text-secondary hover:text-primary-500'}`}>
            <MessageCircleIcon className="h-4 w-4" />
            AI Assistant
          </a>
          {user && (
            <>
              <a href="/profile" className={`transition-colors duration-200 ${currentPage === 'profile' ? 'text-primary-500 font-medium' : 'text-text-secondary hover:text-primary-500'}`}>
                Profile
              </a>
              <Button onClick={onLogout} className="text-sm" variant="outline">
                <LogOutIcon className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </>
          )}
        </nav>

        {/* Mobile Menu Button */}
        <div className="flex items-center gap-4">
          <ThemeToggle />

          {user ? (
            <div className="relative">
              <Button className="rounded-full p-2">
                <UserIcon className="h-4 w-4" />
              </Button>

              {/* User dropdown would go here */}
            </div>
          ) : (
            <Button asChild>
              <a href="/auth/login">Sign In</a>
            </Button>
          )}

          <button
            className="md:hidden p-2 rounded-md hover:bg-surface"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t border-border bg-background">
          <div className="container py-3">
            <nav className="flex flex-col gap-2">
              <a
                href="/"
                className={`p-2 rounded-md ${currentPage === 'dashboard' ? 'bg-surface text-primary-500' : 'hover:bg-surface'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                Dashboard
              </a>
              <a
                href="/chat"
                className={`p-2 rounded-md flex items-center gap-2 ${currentPage === 'chat' ? 'bg-surface text-primary-500' : 'hover:bg-surface'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <MessageCircleIcon className="h-4 w-4" />
                AI Assistant
              </a>
              {user && (
                <>
                  <a
                    href="/profile"
                    className={`p-2 rounded-md ${currentPage === 'profile' ? 'bg-surface text-primary-500' : 'hover:bg-surface'}`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Profile
                  </a>
                  <Button
                    className="w-full justify-start"
                    onClick={() => {
                      onLogout?.();
                      setIsMenuOpen(false);
                    }}
                  >
                    <LogOutIcon className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </>
              )}
            </nav>
          </div>
        </div>
      )}
    </header>
  );
}