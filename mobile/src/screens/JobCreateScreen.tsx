import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import api from '../services/api';

type RootStackParamList = {
  Dashboard: undefined;
  CreateJob: undefined;
};

export default function JobCreateScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [productQuery, setProductQuery] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [locationCity, setLocationCity] = useState('');
  const [autoClose, setAutoClose] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!productQuery || !targetPrice || !maxPrice) {
      Alert.alert('Error', 'Please fill in product, target price, and max price');
      return;
    }

    const target = parseFloat(targetPrice);
    const max = parseFloat(maxPrice);

    if (target > max) {
      Alert.alert('Error', 'Target price must be less than or equal to max price');
      return;
    }

    setLoading(true);
    try {
      await api.post('/jobs', {
        product_query: productQuery,
        target_price: target,
        max_price: max,
        currency: 'AED',
        location_city: locationCity || undefined,
        auto_close: autoClose,
      });

      Alert.alert('Success', 'Job created! Redirecting...', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.form}>
          <Text style={styles.title}>What do you want to buy?</Text>
          <Text style={styles.subtitle}>We'll find the best deals and negotiate for you</Text>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Product *</Text>
            <TextInput
              style={styles.input}
              value={productQuery}
              onChangeText={setProductQuery}
              placeholder="e.g., iPhone 15 Pro, MacBook Pro, Canon Camera"
              placeholderTextColor="#999"
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputContainer, { flex: 1 }]}>
              <Text style={styles.label}>Target Price (AED) *</Text>
              <TextInput
                style={styles.input}
                value={targetPrice}
                onChangeText={setTargetPrice}
                placeholder="4000"
                keyboardType="numeric"
                placeholderTextColor="#999"
              />
            </View>

            <View style={[styles.inputContainer, { flex: 1 }]}>
              <Text style={styles.label}>Max Price (AED) *</Text>
              <TextInput
                style={styles.input}
                value={maxPrice}
                onChangeText={setMaxPrice}
                placeholder="5000"
                keyboardType="numeric"
                placeholderTextColor="#999"
              />
            </View>
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Location</Text>
            <View style={styles.locationButtons}>
              {['Dubai', 'Abu Dhabi', 'Sharjah', 'All UAE'].map((city) => (
                <TouchableOpacity
                  key={city}
                  style={[
                    styles.locationBtn,
                    locationCity === city && styles.locationBtnActive
                  ]}
                  onPress={() => setLocationCity(city === 'All UAE' ? '' : city)}
                >
                  <Text style={[
                    styles.locationText,
                    locationCity === city && styles.locationTextActive
                  ]}>
                    {city}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <TouchableOpacity
            style={styles.checkboxRow}
            onPress={() => setAutoClose(!autoClose)}
          >
            <View style={[styles.checkbox, autoClose && styles.checkboxActive]}>
              {autoClose && <Text style={styles.checkmark}>✓</Text>}
            </View>
            <Text style={styles.checkboxLabel}>
              Auto-close when target price is reached
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleCreate}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading ? 'Creating...' : 'Start Negotiation'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  scrollContent: {
    padding: 16,
  },
  form: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1a1a2e',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 24,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f5f7fa',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  locationButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  locationBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f5f7fa',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  locationBtnActive: {
    backgroundColor: '#c9a227',
    borderColor: '#c9a227',
  },
  locationText: {
    color: '#666',
    fontWeight: '500',
  },
  locationTextActive: {
    color: '#fff',
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 16,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#c9a227',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxActive: {
    backgroundColor: '#c9a227',
  },
  checkmark: {
    color: '#fff',
    fontWeight: 'bold',
  },
  checkboxLabel: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  button: {
    backgroundColor: '#c9a227',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});