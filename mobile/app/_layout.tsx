import { Stack } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StyleSheet } from 'react-native';

const client = new QueryClient();
export default function Layout() {
  return <QueryClientProvider client={client}><GestureHandlerRootView style={styles.root}><StatusBar style="light" /><Stack screenOptions={{ headerShown: false }} /></GestureHandlerRootView></QueryClientProvider>;
}
const styles = StyleSheet.create({ root: { flex: 1, backgroundColor: '#070A11' } });
