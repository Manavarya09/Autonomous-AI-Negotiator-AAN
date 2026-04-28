import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

import api from './api';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('Push notifications require a physical device');
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Push notification permission not granted');
    return null;
  }

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'AAN Notifications',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#c9a227',
    });

    await Notifications.setNotificationChannelAsync('deals', {
      name: 'Deal Alerts',
      importance: Notifications.AndroidImportance.HIGH,
      description: 'Notifications when deals are found',
    });
  }

  const expoPushToken = await Notifications.getExpoPushTokenAsync();
  
  try {
    await api.post('/notifications/register', {
      token: expoPushToken.data,
      platform: Platform.OS,
    });
  } catch (error) {
    console.log('Failed to register push token:', error);
  }

  return expoPushToken.data;
}

export function setupNotificationHandlers() {
  Notifications.addNotificationReceivedListener((notification) => {
    console.log('Notification received:', notification);
  });

  Notifications.addNotificationResponseReceivedListener((response) => {
    console.log('Notification response:', response);
    const data = response.notification.request.content.data;
    if (data?.screen) {
      // Handle navigation based on notification data
    }
  });
}

export async function scheduleLocalNotification(
  title: string,
  body: string,
  data?: object
) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      data: data || {},
    },
    trigger: null,
  });
}

export async function cancelAllNotifications() {
  await Notifications.cancelAllScheduledNotificationsAsync();
}