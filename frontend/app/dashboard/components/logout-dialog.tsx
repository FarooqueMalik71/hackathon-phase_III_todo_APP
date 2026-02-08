'use client';

import { Modal } from '@/app/dashboard/components/ui/modal';
import { Button } from '@/app/dashboard/components/ui/button';
import { useRouter } from 'next/navigation';

interface LogoutDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function LogoutDialog({ isOpen, onClose }: LogoutDialogProps) {
  const router = useRouter();

  const handleConfirm = () => {
    // In a real app, you would clear the auth token here
    localStorage.removeItem('auth-token');

    // Redirect to login page
    router.push('/auth/login');
    router.refresh(); // Refresh the router to update the UI

    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Confirm Logout">
      <div className="mt-4">
        <p className="text-text-secondary">
          Are you sure you want to logout? You'll need to sign in again to access your account.
        </p>
      </div>

      <div className="mt-6 flex justify-end space-x-3">
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="danger" onClick={handleConfirm}>
          Logout
        </Button>
      </div>
    </Modal>
  );
}