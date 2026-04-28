import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface AutoBuyConfig {
  enabled: boolean;
  triggerAtTarget: boolean;
  confirmationSeconds: number;
}

export interface PriceAlert {
  id: string;
  productName: string;
  targetPrice: number;
  currentPrice?: number;
  enabled: boolean;
  triggered: boolean;
}

interface SettingsState {
  autoBuy: AutoBuyConfig;
  priceAlerts: PriceAlert[];
  notificationsEnabled: boolean;
  
  setAutoBuy: (config: Partial<AutoBuyConfig>) => void;
  toggleAutoBuy: () => void;
  
  addPriceAlert: (alert: Omit<PriceAlert, 'id' | 'triggered'>) => void;
  removePriceAlert: (id: string) => void;
  togglePriceAlert: (id: string) => void;
  
  setNotificationsEnabled: (enabled: boolean) => void;
  
  loadFromStorage: () => Promise<void>;
  saveToStorage: () => Promise<void>;
}

const STORAGE_KEY = 'aan_settings';

export const useSettingsStore = create<SettingsState>((set, get) => ({
  autoBuy: {
    enabled: false,
    triggerAtTarget: true,
    confirmationSeconds: 30,
  },
  priceAlerts: [],
  notificationsEnabled: true,

  setAutoBuy: (config) => {
    set((state) => ({
      autoBuy: { ...state.autoBuy, ...config },
    }));
    get().saveToStorage();
  },

  toggleAutoBuy: () => {
    set((state) => ({
      autoBuy: { ...state.autoBuy, enabled: !state.autoBuy.enabled },
    }));
    get().saveToStorage();
  },

  addPriceAlert: (alert) => {
    const newAlert: PriceAlert = {
      ...alert,
      id: Date.now().toString(),
      triggered: false,
    };
    set((state) => ({
      priceAlerts: [...state.priceAlerts, newAlert],
    }));
    get().saveToStorage();
  },

  removePriceAlert: (id) => {
    set((state) => ({
      priceAlerts: state.priceAlerts.filter((a) => a.id !== id),
    }));
    get().saveToStorage();
  },

  togglePriceAlert: (id) => {
    set((state) => ({
      priceAlerts: state.priceAlerts.map((a) =>
        a.id === id ? { ...a, enabled: !a.enabled } : a
      ),
    }));
    get().saveToStorage();
  },

  setNotificationsEnabled: (enabled) => {
    set({ notificationsEnabled: enabled });
    get().saveToStorage();
  },

  loadFromStorage: async () => {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEY);
      if (data) {
        const parsed = JSON.parse(data);
        set({
          autoBuy: parsed.autoBuy || get().autoBuy,
          priceAlerts: parsed.priceAlerts || [],
          notificationsEnabled: parsed.notificationsEnabled ?? true,
        });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  },

  saveToStorage: async () => {
    try {
      const state = get();
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify({
        autoBuy: state.autoBuy,
        priceAlerts: state.priceAlerts,
        notificationsEnabled: state.notificationsEnabled,
      }));
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  },
}));