'use client';

import { Fragment, ReactNode, useRef } from 'react';
import { Dialog as UIDialog, Transition } from '@headlessui/react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

/* ✅ TS-safe mapping (fixes "never" type bug) */
const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
} as const;

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}: ModalProps) {
  const closeButtonRef = useRef(null);

  return (
    <Transition show={isOpen} as={Fragment}>
      <UIDialog

        className="relative z-50"
        onClose={onClose}
        initialFocus={closeButtonRef}
      >
        {/* BACKDROP */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
        </Transition.Child>

        {/* MODAL WRAPPER */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ type: 'spring', damping: 25, stiffness: 400 }}
                className="w-full"
              >
                <UIDialog.Panel
                  className={cn(
                    'w-full rounded-2xl bg-background p-6 text-left shadow-lg',
                    sizeClasses[size]
                  )}
                >
                  {title && (
                    <UIDialog.Title
               
                      className="text-lg font-semibold mb-3"
                    >
                      {title}
                    </UIDialog.Title>
                  )}

                  <div>{children}</div>

                  {/* hidden focus element for accessibility */}
                  <button ref={closeButtonRef} className="hidden" />
                </UIDialog.Panel>
              </motion.div>
            </Transition.Child>
          </div>
        </div>
      </UIDialog>
    </Transition>
  );
}
