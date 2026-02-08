/**
 * Utility functions for theme management
 */

export function getThemeFromStorage(key: string = 'ui-theme'): 'light' | 'dark' | 'system' {
  if (typeof window === 'undefined') {
    return 'system';
  }

  const storedTheme = localStorage.getItem(key);

  if (storedTheme === 'light' || storedTheme === 'dark' || storedTheme === 'system') {
    return storedTheme;
  }

  return 'system'; // default
}

export function setThemeInStorage(theme: 'light' | 'dark' | 'system', key: string = 'ui-theme') {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, theme);
  }
}