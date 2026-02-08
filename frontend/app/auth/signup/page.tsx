'use client';

import { Button } from '@/app/dashboard/components/ui/button';
import { Input } from '@/app/dashboard/components/ui/input';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function SignUpPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsLoading(true);

    try {
      const res = await apiClient.register(
        formData.name,
        formData.email,
        formData.password
      );

      if (res.token) localStorage.setItem('auth-token', res.token);

      router.push('/dashboard');
    } catch (error: any) {
      setErrors({ form: error.message || 'Signup failed' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted/40 p-4 sm:p-6">
      <div className="w-full max-w-sm sm:max-w-md lg:max-w-lg rounded-2xl border bg-background p-6 sm:p-8 lg:p-10 shadow-xl">

        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight">
            Create your account
          </h1>
          <p className="text-sm text-text-secondary mt-2">
            Start your journey today
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">

          <Input name="name" placeholder="Full Name" onChange={handleChange} />
          <Input name="email" placeholder="Email" onChange={handleChange} />
          <Input name="password" type="password" placeholder="Password" onChange={handleChange} />

          {errors.form && (
            <p className="text-sm text-red-500">{errors.form}</p>
          )}

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-12 sm:h-11 rounded-lg shadow-md"
          >
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </Button>
        </form>

        <p className="text-center text-sm text-text-secondary mt-8">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-primary-500 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
