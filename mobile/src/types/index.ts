export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Job {
  id: string;
  user_id: string;
  product_query: string;
  target_price: number;
  max_price: number;
  currency: string;
  location_city?: string;
  location_radius?: number;
  urgency: 'low' | 'normal' | 'high';
  auto_close: boolean;
  status: 'queued' | 'running' | 'completed' | 'cancelled' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface JobStatus {
  id: string;
  status: string;
  listings_found: number;
  active_negotiations: number;
  completed_negotiations: number;
}

export interface Deal {
  id: string;
  job_id: string;
  listing_id: string;
  seller_name?: string;
  seller_contact: string;
  platform: string;
  list_price: number;
  target_price: number;
  max_price: number;
  current_offer?: number;
  agreed_price?: number;
  status: 'active' | 'accepted' | 'rejected' | 'stalled';
  round_count: number;
  deal_score?: number;
  started_at: string;
  closed_at?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CreateJobRequest {
  product_query: string;
  target_price: number;
  max_price: number;
  currency?: string;
  location_city?: string;
  urgency?: string;
  auto_close?: boolean;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}