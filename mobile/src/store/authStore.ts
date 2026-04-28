import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface AuthState {
  token: string | null;
  user: { id: string; email: string; username: string } | null;
  isLoading: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: { id: string; email: string; username: string } | null) => void;
  logout: () => void;
  loadFromStorage: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isLoading: true,

  setToken: (token) => {
    set({ token });
    if (token) {
      AsyncStorage.setItem('token', token);
    } else {
      AsyncStorage.removeItem('token');
    }
  },

  setUser: (user) => {
    set({ user });
    if (user) {
      AsyncStorage.setItem('user', JSON.stringify(user));
    } else {
      AsyncStorage.removeItem('user');
    }
  },

  logout: () => {
    set({ token: null, user: null });
    AsyncStorage.removeItem('token');
    AsyncStorage.removeItem('user');
  },

  loadFromStorage: async () => {
    try {
      const [token, userStr] = await AsyncStorage.multiGet(['token', 'user']);
      const tokenValue = token[1];
      const userValue = userStr[1] ? JSON.parse(userStr[1]) : null;
      
      set({
        token: tokenValue,
        user: userValue,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
    }
  },
}));