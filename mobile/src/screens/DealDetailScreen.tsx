import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { useRoute, useFocusEffect } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';

import api from '../services/api';
import { Job, JobStatus } from '../types';

type ParamList = {
  DealDetail: { jobId: string };
};

export default function DealDetailScreen() {
  const route = useRoute<RouteProp<ParamList, 'DealDetail'>>();
  const { jobId } = route.params;
  
  const [job, setJob] = useState<Job | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchJobDetails = async () => {
    try {
      const [jobRes, statusRes] = await Promise.all([
        api.get(`/jobs/${jobId}`),
        api.get(`/jobs/${jobId}/status`),
      ]);
      setJob(jobRes.data);
      setStatus(statusRes.data);
    } catch (error) {
      console.error('Failed to fetch job:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchJobDetails();
    }, [jobId])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchJobDetails();
  };

  if (loading || !job) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued': return '#f59e0b';
      case 'running': return '#3b82f6';
      case 'completed': return '#10b981';
      case 'cancelled': return '#ef4444';
      case 'failed': return '#dc2626';
      default: return '#6b7280';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.productName}>{job.product_query}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(job.status) }]}>
          <Text style={styles.statusText}>{job.status.toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Negotiation Progress</Text>
        
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{status?.listings_found || 0}</Text>
            <Text style={styles.statLabel}>Listings Found</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{status?.active_negotiations || 0}</Text>
            <Text style={styles.statLabel}>Active</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{status?.completed_negotiations || 0}</Text>
            <Text style={styles.statLabel}>Completed</Text>
          </View>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Deal Parameters</Text>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Target Price</Text>
          <Text style={styles.paramValue}>AED {job.target_price.toLocaleString()}</Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Maximum Price</Text>
          <Text style={styles.paramValue}>AED {job.max_price.toLocaleString()}</Text>
        </View>
        
        {job.location_city && (
          <View style={styles.paramRow}>
            <Text style={styles.paramLabel}>Location</Text>
            <Text style={styles.paramValue}>{job.location_city}</Text>
          </View>
        )}
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Auto-Close</Text>
          <Text style={styles.paramValue}>{job.auto_close ? 'Enabled' : 'Disabled'}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Timeline</Text>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Created</Text>
          <Text style={styles.paramValue}>
            {new Date(job.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Last Updated</Text>
          <Text style={styles.paramValue}>
            {new Date(job.updated_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>
      </View>

      {job.status === 'running' && (
        <View style={styles.infoCard}>
          <Text style={styles.infoText}>
            Negotiations are in progress. You'll receive a notification when a deal is accepted.
          </Text>
        </View>
      )}

      {job.status === 'completed' && (
        <View style={[styles.infoCard, styles.successCard]}>
          <Text style={styles.successTitle}>Deal Completed!</Text>
          <Text style={styles.infoText}>
            Your negotiation job has completed. Check your notifications for the results.
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: '#1a1a2e',
    padding: 20,
    paddingTop: 16,
  },
  productName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#fff',
    margin: 16,
    marginBottom: 0,
    borderRadius: 12,
    padding: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a2e',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a1a2e',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  paramRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  paramLabel: {
    fontSize: 14,
    color: '#666',
  },
  paramValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a2e',
  },
  infoCard: {
    backgroundColor: '#e0f2fe',
    margin: 16,
    borderRadius: 12,
    padding: 16,
  },
  successCard: {
    backgroundColor: '#d1fae5',
  },
  infoText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  successTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#065f46',
    marginBottom: 8,
  },
});