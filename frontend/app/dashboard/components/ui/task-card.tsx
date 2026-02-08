import { Button } from '@/app/dashboard/components/ui/button';
import { cn } from '@/lib/utils';
import { Task } from '@/types/task';
import { motion } from 'framer-motion';
import { CheckIcon, PencilIcon, TrashIcon, CalendarIcon, ClockIcon } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TaskCard({ task, onToggle, onEdit, onDelete }: TaskCardProps) {
  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && !task.completed;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'bg-surface rounded-xl shadow-sm border border-border p-5 hover:shadow-md transition-shadow duration-200',
        task.completed && 'opacity-75',
        isOverdue && 'border-red-200 bg-red-50/50 dark:border-red-800'
      )}
    >
      <div className="flex items-start gap-4">
        <motion.button
          onClick={() => onToggle(task.id)}
          className={cn(
            'flex h-6 w-6 items-center justify-center rounded-full border-2 mt-1 flex-shrink-0 transition-colors',
            task.completed
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20'
          )}
          aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          {task.completed && <CheckIcon className="h-4 w-4" />}
        </motion.button>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3 mb-2">
            <motion.h3
              animate={{ textDecorationLine: task.completed ? 'line-through' : 'none' }}
              transition={{ duration: 0.2 }}
              className={cn(
                'font-semibold text-lg leading-tight',
                task.completed && 'text-text-secondary',
                isOverdue && 'text-red-700 dark:text-red-300'
              )}
            >
              {task.title}
            </motion.h3>

            {task.priority && (
              <span className={cn(
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium flex-shrink-0',
                task.priority === 'high' && 'bg-red-100 text-red-800 dark:bg-red-900/30 text-text-primary',
                task.priority === 'medium' && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 text-text-primary',
                task.priority === 'low' && 'bg-green-100 text-green-800 dark:bg-green-900/30 text-text-primary',
              )}>
                {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
              </span>
            )}
          </div>

          {task.description && (
            <p className={cn(
              'text-sm text-text-secondary mb-3 leading-relaxed',
              task.completed && 'line-through'
            )}>
              {task.description}
            </p>
          )}

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-text-secondary">
              {task.dueDate && (
                <div className={cn(
                  'flex items-center gap-1',
                  isOverdue && 'text-red-600 dark:text-red-400'
                )}>
                  <CalendarIcon className="h-3 w-3" />
                  <span className="font-medium">
                    {new Date(task.dueDate).toLocaleDateString()}
                  </span>
                  {isOverdue && <ClockIcon className="h-3 w-3 ml-1" />}
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(task.id)}
                aria-label="Edit task"
                className="h-8 w-8 p-0 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                <PencilIcon className="h-4 w-4 text-blue-600" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(task.id)}
                aria-label="Delete task"
                className="h-8 w-8 p-0 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <TrashIcon className="h-4 w-4 text-red-600" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}