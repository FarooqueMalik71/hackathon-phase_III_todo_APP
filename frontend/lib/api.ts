/**
 * Centralized API client for the frontend application
 */

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    // Use absolute backend URL from environment variable
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async request<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      // Add Authorization if token exists
      ...(localStorage.getItem('auth-token') && { 'Authorization': `Bearer ${localStorage.getItem('auth-token')}` }),
      ...options.headers,
    };

    const config: RequestInit = {
      method: options.method || 'GET',
      headers,
    };

    if (options.body) {
      config.body = typeof options.body === 'string'
        ? options.body
        : JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);

      // Handle different response statuses
      if (!response.ok) {
        const errorData = await response.text();

        // If response is JSON, parse it
        try {
          const jsonError = JSON.parse(errorData);
          throw new Error(jsonError.message || `HTTP error! status: ${response.status}`);
        } catch {
          // If not JSON, throw the raw text
          throw new Error(errorData || `HTTP error! status: ${response.status}`);
        }
      }

      // Handle responses without body (e.g., DELETE requests)
      if (response.status === 204) {
        return {} as T;
      }

      // Parse JSON response
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${options.method} ${url}`, error);
      throw error;
    }
  }

  // Authentication methods
  async login(email: string, password: string) {
    return this.request<{ token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: { email, password },
    });
  }

  async register(name: string, email: string, password: string) {
    return this.request<{ token: string }>('/api/v1/auth/register', {
      method: 'POST',
      body: { name, email, password },
    });
  }

  async logout() {
    // Clear the token from local storage
    localStorage.removeItem('auth-token');
  }

  // Task methods
  async getTasks() {
    return this.request<any[]>('/api/v1/tasks/', {
      method: 'GET'
    });
  }

  async createTask(task: { title: string; description?: string; priority?: string; dueDate?: string }) {
    return this.request<any>('/api/v1/tasks/', {
      method: 'POST',
      body: task,
    });
  }

  async updateTask(id: string, task: Partial<{ title: string; description?: string; completed?: boolean; priority?: string; dueDate?: string }>) {
    return this.request<any>(`/api/v1/tasks/${id}`, {
      method: 'PUT',
      body: task,
    });
  }

  async deleteTask(id: string) {
    return this.request<void>(`/api/v1/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(id: string, completed: boolean) {
    return this.request<any>(`/api/v1/tasks/${id}/toggle`, {
      method: 'PATCH',
      body: { completed },
    });
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth-token');
    return !!token;
  }
}

export const apiClient = new ApiClient();