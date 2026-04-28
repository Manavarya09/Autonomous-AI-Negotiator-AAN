import { useEffect } from 'react';
import { Stack } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { useAuthStore } from './src/store/authStore';
import { api } from './src/services/api';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import JobCreateScreen from './src/screens/JobCreateScreen';
import DealDetailScreen from './src/screens/DealDetailScreen';

export default function App() {
  const { token, setToken, loadFromStorage } = useAuthStore();

  useEffect(() => {
    loadFromStorage();
  }, []);

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      AsyncStorage.setItem('token', token);
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <Stack.Navigator
          screenOptions={{
            headerStyle: { backgroundColor: '#1a1a2e' },
            headerTintColor: '#fff',
            headerTitleStyle: { fontWeight: '600' },
            contentStyle: { backgroundColor: '#f5f7fa' },
          }}
        >
          {token ? (
            <>
              <Stack.Screen
                name="Dashboard"
                component={DashboardScreen}
                options={{ title: 'AAN Dashboard' }}
              />
              <Stack.Screen
                name="CreateJob"
                component={JobCreateScreen}
                options={{ title: 'New Negotiation' }}
              />
              <Stack.Screen
                name="DealDetail"
                component={DealDetailScreen}
                options={{ title: 'Deal Details' }}
              />
            </>
          ) : (
            <>
              <Stack.Screen
                name="Login"
                component={LoginScreen}
                options={{ headerShown: false }}
              />
              <Stack.Screen
                name="Register"
                component={RegisterScreen}
                options={{ headerShown: false }}
              />
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}