import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PropsWithChildren } from 'react';

const client = new QueryClient();
export default function Layout({ children }: PropsWithChildren) {
  return <QueryClientProvider client={client}><StatusBar style="light" />{children}</QueryClientProvider>;
}
