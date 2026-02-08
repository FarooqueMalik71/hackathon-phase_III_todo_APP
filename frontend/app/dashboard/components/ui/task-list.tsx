import { TaskCard } from '@/app/dashboard/components/ui/task-card';
import { Task } from '@/types/task';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Button } from '@/app/dashboard/components/ui/button';
import { PlusIcon } from 'lucide-react';

interface TaskListProps {
  tasks: Task[];
  onTaskToggle: (id: string) => void;
  onTaskEdit: (id: string) => void;
  onTaskDelete: (id: string) => void;
  loading?: boolean;
}

export function TaskList({ tasks, onTaskToggle, onTaskEdit, onTaskDelete, loading }: TaskListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
            className="bg-surface rounded-lg shadow-sm p-4 border border-border animate-pulse"
          >
            <div className="flex items-center space-x-4">
              <div className="h-6 w-6 rounded-full bg-border"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-border rounded w-3/4"></div>
                <div className="h-3 bg-border rounded w-1/2"></div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 rounded-xl border-2 border-dashed border-blue-200 dark:border-blue-800 p-12 text-center"
      >
        <div className="mx-auto w-20 h-20 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-text-primary mb-2">No tasks found</h3>
        <p className="text-text-secondary mb-6 max-w-sm mx-auto">
          {tasks.length === 0 ? "Get started by creating your first task. Stay organized and boost your productivity!" : "Try adjusting your search or filters to find what you're looking for."}
        </p>
        {tasks.length === 0 && (
          <Button onClick={() => window.dispatchEvent(new CustomEvent('add-task'))} className="shadow-lg">
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Your First Task
          </Button>
        )}
      </motion.div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggle={onTaskToggle}
          onEdit={onTaskEdit}
          onDelete={onTaskDelete}
        />
      ))}
    </div>
  );
}