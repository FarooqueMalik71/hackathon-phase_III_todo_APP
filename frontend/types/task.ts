export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
  userId: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}