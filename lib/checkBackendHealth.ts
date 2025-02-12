import { toast } from '@/components/ui/use-toast';

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/health`);
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Backend health check failed:', error);
    toast({
      title: "Backend Connection Error",
      description: "Unable to connect to backend services. Some features may be unavailable.",
      variant: "destructive"
    });
    return false;
  }
}
