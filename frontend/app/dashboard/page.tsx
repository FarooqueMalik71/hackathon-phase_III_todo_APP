'use client';

import { HeaderNav } from '@/app/dashboard/components/ui/header-nav';
import { TaskList } from '@/app/dashboard/components/ui/task-list';
import { Button } from '@/app/dashboard/components/ui/button';
import { Input } from '@/app/dashboard/components/ui/input';
import { PlusIcon, SearchIcon, CheckCircleIcon, ClockIcon, AlertTriangleIcon, MessageCircleIcon } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { Task } from '@/types/task';
import { TaskModal } from '@/app/dashboard/components/task-modal';
import LogoutDialog from '@/app/dashboard/components/logout-dialog';
import { apiClient } from '@/lib/api';
import { onTaskChange } from '@/lib/taskSync';

import { ConfirmationDialog } from '@/app/dashboard/components/ui/confirmation-dialog';
import ProtectedRoute from '@/app/dashboard/components/protected-route';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isModalLoading, setIsModalLoading] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [isDeleteConfirmationOpen, setIsDeleteConfirmationOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchTasks = async () => {
    // Only proceed if auth token exists
    const token = localStorage.getItem('auth-token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getTasks();
      setTasks(response || []);
    } catch (error: any) {
      console.error('Failed to fetch tasks:', error);
      setError(error.message || 'Failed to fetch tasks. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Load tasks from API on component mount
  useEffect(() => {
    fetchTasks();

    // Listen for add task event from empty state
    const handleAddTask = () => setIsModalOpen(true);
    window.addEventListener('add-task', handleAddTask);

    // Keyboard shortcut for adding tasks (Ctrl/Cmd + N)
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        setIsModalOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('add-task', handleAddTask);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Live sync: auto-refresh when chatbot modifies tasks
  useEffect(() => {
    const cleanup = onTaskChange(() => {
      fetchTasks();
    });
    return cleanup;
  }, []);

  // Filter and search tasks
  const filteredTasks = useMemo(() => {
    let filtered = tasks;

    // Apply filter
    if (filter === 'active') filtered = filtered.filter(task => !task.completed);
    if (filter === 'completed') filtered = filtered.filter(task => task.completed);

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(query) ||
        task.description?.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [tasks, filter, searchQuery]);

  // Calculate statistics
  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const active = total - completed;
    const overdue = tasks.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && !t.completed).length;

    return { total, completed, active, overdue };
  }, [tasks]);

  const handleTaskToggle = async (id: string) => {
    try {
      // Optimistically update the UI
      setTasks(tasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      ));

      // Update on the server
      await apiClient.toggleTaskCompletion(id, !tasks.find(t => t.id === id)?.completed);
    } catch (error) {
      console.error('Failed to toggle task:', error);
      // Revert optimistic update on error
      setTasks(tasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      ));
    }
  };

  const handleTaskEdit = (id: string) => {
    const taskToEdit = tasks.find(task => task.id === id);
    if (taskToEdit) {
      setEditingTask(taskToEdit);
      setIsModalOpen(true);
    }
  };

  const handleTaskDelete = async (id: string) => {
    setTaskToDelete(id);
    setIsDeleteConfirmationOpen(true);
  };

  const confirmDeleteTask = async () => {
    if (!taskToDelete) return;

    try {
      // Optimistically remove from UI
      setTasks(tasks.filter(task => task.id !== taskToDelete));

      // Delete on the server
      await apiClient.deleteTask(taskToDelete);
    } catch (error: any) {
      console.error('Failed to delete task:', error);
      // Revert optimistic update on error
      const deletedTask = tasks.find(task => task.id === taskToDelete);
      if (deletedTask) {
        setTasks([...tasks, deletedTask]);
      }
      setError(error.message || 'Failed to delete task. Please try again.');
    } finally {
      setIsDeleteConfirmationOpen(false);
      setTaskToDelete(null);
    }
  };

  const handleSaveTask = async (taskData: Partial<Task>) => {
    try {
      setIsModalLoading(true);
      setError(null); // Clear previous errors

      if (editingTask) {
        // Update existing task
        const updatedTask = await apiClient.updateTask(editingTask.id, taskData);
        setTasks(tasks.map(task =>
          task.id === editingTask.id ? updatedTask : task
        ));
      } else {
        // Create new task
        const newTask = await apiClient.createTask({
          title: taskData.title || '',
          description: taskData.description,
          priority: taskData.priority,
          dueDate: taskData.dueDate,
        });
        setTasks([newTask, ...tasks]);
      }

      setIsModalOpen(false);
      setEditingTask(null);
    } catch (error: any) {
      console.error('Failed to save task:', error);
      setError(error.message || 'Failed to save task. Please try again.');
    } finally {
      setIsModalLoading(false);
    }
  };

  const handleLogout = () => {
    setIsLogoutDialogOpen(true);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <HeaderNav
          user={{ id: 'user-1', name: 'John Doe', email: 'john@example.com' }}
          currentPage="dashboard"
          onLogout={handleLogout}
        />

        <main className="container py-8">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-2">Dashboard</h1>
              <p className="text-text-secondary">Manage your tasks and stay productive</p>
            </div>

            <Button onClick={() => setIsModalOpen(true)} size="lg" className="shadow-lg">
              <PlusIcon className="h-5 w-5 mr-2" />
              Add New Task
            </Button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-6 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Tasks</p>
                  <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.total}</p>
                </div>
                <CheckCircleIcon className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl p-6 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600 dark:text-green-400">Completed</p>
                  <p className="text-2xl font-bold text-green-900 dark:text-green-100">{stats.completed}</p>
                </div>
                <CheckCircleIcon className="h-8 w-8 text-green-500" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-xl p-6 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-yellow-600 dark:text-yellow-400">Active</p>
                  <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">{stats.active}</p>
                </div>
                <ClockIcon className="h-8 w-8 text-yellow-500" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-xl p-6 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-red-600 dark:text-red-400">Overdue</p>
                  <p className="text-2xl font-bold text-red-900 dark:text-red-100">{stats.overdue}</p>
                </div>
                <AlertTriangleIcon className="h-8 w-8 text-red-500" />
              </div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-text-secondary" />
              <Input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex border border-border rounded-lg overflow-hidden bg-surface">
              {(['all', 'active', 'completed'] as const).map((option) => (
                <button
                  key={option}
                  className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                    filter === option
                      ? 'bg-primary-500 text-white shadow-sm'
                      : 'text-text-secondary hover:text-primary-500 hover:bg-surface'
                  }`}
                  onClick={() => setFilter(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-border rounded-lg flex items-center gap-3">
              <AlertTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0" />
              <span className="text-red-700">{error}</span>
            </div>
          )}

          <div className="bg-surface rounded-xl shadow-sm border border-border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">
                Tasks ({filteredTasks.length})
              </h2>
            </div>

            <TaskList
              tasks={filteredTasks}
              onTaskToggle={handleTaskToggle}
              onTaskEdit={handleTaskEdit}
              onTaskDelete={handleTaskDelete}
              loading={loading}
            />
          </div>
        </main>

        <TaskModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setEditingTask(null);
          }}
          onSave={handleSaveTask}
          task={editingTask || undefined}
          loading={isModalLoading}
        />

        <LogoutDialog
          isOpen={isLogoutDialogOpen}
          onClose={() => setIsLogoutDialogOpen(false)}
        />

        <ConfirmationDialog
          isOpen={isDeleteConfirmationOpen}
          onClose={() => setIsDeleteConfirmationOpen(false)}
          onConfirm={confirmDeleteTask}
          title="Delete Task"
          message="Are you sure you want to delete this task? This action cannot be undone."
          confirmText="Delete"
          cancelText="Cancel"
          variant="destructive"
        />

        {/* Footer */}
        <footer className="mt-16 py-8 border-t border-border bg-surface">
          <div className="container text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <div className="bg-primary-500 rounded-lg p-1">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <span className="text-sm font-medium text-text-secondary">TaskFlow Pro</span>
            </div>
            <p className="text-xs text-text-secondary">
              Press <kbd className="px-1 py-0.5 bg-surface rounded text-xs">Ctrl+N</kbd> to quickly add a new task
            </p>
          </div>
        </footer>

        {/* Floating AI Chat Button */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5
                     bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700
                     text-white rounded-full shadow-lg hover:shadow-xl
                     transition-all duration-300 hover:scale-105 group"
        >
          <MessageCircleIcon className="h-5 w-5 group-hover:animate-bounce" />
          <span className="font-medium text-sm">AI Assistant</span>
        </Link>
      </div>
    </ProtectedRoute>
  );
}