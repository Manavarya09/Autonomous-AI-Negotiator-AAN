<template>
  <div class="dashboard">
    <nav class="nav">
      <div class="nav-container">
        <a href="/" class="nav-logo">
          <div class="logo-mark">A</div>
          <span>AAN</span>
        </a>
        <div class="nav-links">
          <a href="#listings">Listings</a>
          <a href="#jobs">Jobs</a>
          <a href="#negotiations">Negotiations</a>
        </div>
        <div class="nav-actions">
          <span class="user-email">{{ user?.email }}</span>
          <button @click="logout" class="btn btn-secondary">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container">
      <div class="dashboard-header">
        <h1>Dashboard</h1>
        <button @click="showJobForm = true" class="btn btn-primary">New Job</button>
      </div>

      <div class="stats">
        <div class="stat-card">
          <div class="stat-label">Total Jobs</div>
          <div class="stat-value">{{ jobs.length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Active</div>
          <div class="stat-value">{{ activeJobs }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Listings Found</div>
          <div class="stat-value">{{ totalListings }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Deals Closed</div>
          <div class="stat-value">{{ dealsClosed }}</div>
        </div>
      </div>

      <div class="section">
        <h2>Your Jobs</h2>
        <div v-if="jobs.length === 0" class="empty">
          <p>No jobs yet. Create your first negotiation job.</p>
        </div>
        <div v-else class="jobs-list">
          <div v-for="job in jobs" :key="job.id" class="job-card">
            <div class="job-header">
              <h3>{{ job.product_query }}</h3>
              <span class="badge" :class="'status-' + job.status">{{ job.status }}</span>
            </div>
            <div class="job-details">
              <span>Target: AED {{ job.target_price }}</span>
              <span>Max: AED {{ job.max_price }}</span>
              <span>{{ job.location_city || 'UAE' }}</span>
            </div>
            <div class="job-actions">
              <button @click="viewJob(job.id)" class="btn btn-small">View</button>
              <button @click="deleteJob(job.id)" class="btn btn-small btn-danger">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showJobForm" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create New Job</h2>
            <button @click="showJobForm = false" class="close">&times;</button>
          </div>
          <form @submit.prevent="createJob" class="form">
            <div class="form-group">
              <label>What do you want to buy?</label>
              <input v-model="newJob.product_query" type="text" placeholder="e.g., iPhone 15 Pro, MacBook Pro" required />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Target Price (AED)</label>
                <input v-model.number="newJob.target_price" type="number" min="1" required />
              </div>
              <div class="form-group">
                <label>Max Price (AED)</label>
                <input v-model.number="newJob.max_price" type="number" :min="newJob.target_price" required />
              </div>
            </div>
            <div class="form-group">
              <label>Location</label>
              <select v-model="newJob.location_city">
                <option value="">All UAE</option>
                <option value="Dubai">Dubai</option>
                <option value="Abu Dhabi">Abu Dhabi</option>
                <option value="Sharjah">Sharjah</option>
              </select>
            </div>
            <div class="form-group">
              <label>
                <input v-model="newJob.auto_close" type="checkbox" />
                Auto-close when target price is reached
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="showJobForm = false" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="creating">
                {{ creating ? 'Creating...' : 'Create Job' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="selectedJob" class="modal">
        <div class="modal-content modal-large">
          <div class="modal-header">
            <h2>Job: {{ selectedJob.product_query }}</h2>
            <button @click="selectedJob = null" class="close">&times;</button>
          </div>
          <div class="job-detail">
            <div class="detail-stats">
              <div class="stat">
                <span class="label">Status</span>
                <span class="value">{{ selectedJob.status }}</span>
              </div>
              <div class="stat">
                <span class="label">Listings</span>
                <span class="value">{{ jobStatus?.listings_found || 0 }}</span>
              </div>
              <div class="stat">
                <span class="label">Active Negotiations</span>
                <span class="value">{{ jobStatus?.active_negotiations || 0 }}</span>
              </div>
              <div class="stat">
                <span class="label">Completed</span>
                <span class="value">{{ jobStatus?.completed_negotiations || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showLogin" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ isRegister ? 'Register' : 'Login' }}</h2>
            <button @click="showLogin = false" class="close">&times;</button>
          </div>
          <form @submit.prevent="handleAuth" class="form">
            <div class="form-group">
              <label>Email</label>
              <input v-model="authForm.email" type="email" required />
            </div>
            <div class="form-group">
              <label>Password</label>
              <input v-model="authForm.password" type="password" minlength="8" required />
            </div>
            <div v-if="isRegister" class="form-group">
              <label>Username</label>
              <input v-model="authForm.username" type="text" minlength="3" required />
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="authenticating">
                {{ authenticating ? 'Please wait...' : (isRegister ? 'Register' : 'Login') }}
              </button>
            </div>
            <p class="switch-auth">
              <a href="#" @click.prevent="isRegister = !isRegister">
                {{ isRegister ? 'Already have an account? Login' : 'Need an account? Register' }}
              </a>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

client.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const user = ref(null)
const token = ref(localStorage.getItem('token'))
const jobs = ref([])
const listings = ref([])
const showLogin = ref(!token.value)
const isRegister = ref(false)
const authenticating = ref(false)
const showJobForm = ref(false)
const creating = ref(false)
const selectedJob = ref(null)
const jobStatus = ref(null)

const newJob = reactive({
  product_query: '',
  target_price: null,
  max_price: null,
  currency: 'AED',
  location_city: '',
  urgency: 'normal',
  auto_close: false
})

const authForm = reactive({
  email: '',
  password: '',
  username: ''
})

const activeJobs = computed(() => jobs.value.filter(j => j.status === 'running' || j.status === 'queued').length)
const totalListings = computed(() => listings.value.length)
const dealsClosed = computed(() => 0)

async function handleAuth() {
  authenticating.value = true
  try {
    if (isRegister.value) {
      await client.post('/api/v1/auth/register', {
        email: authForm.email,
        password: authForm.password,
        username: authForm.username
      })
      isRegister.value = false
      authForm.password = ''
    }
    
    const res = await client.post('/api/v1/auth/login', 
      new URLSearchParams({
        username: authForm.email,
        password: authForm.password
      })
    )
    token.value = res.data.access_token
    localStorage.setItem('token', res.data.access_token)
    showLogin.value = false
    await fetchUser()
  } catch (err) {
    alert(err.response?.data?.detail || 'Authentication failed')
  } finally {
    authenticating.value = false
  }
}

async function logout() {
  localStorage.removeItem('token')
  token.value = null
  user.value = null
  showLogin.value = true
}

async function fetchUser() {
  try {
    const res = await client.get('/api/v1/auth/me')
    user.value = res.data
    showLogin.value = false
  } catch {
    logout()
  }
}

async function fetchJobs() {
  try {
    const res = await client.get('/api/v1/jobs')
    jobs.value = res.data
  } catch (err) {
    console.error('Failed to fetch jobs:', err)
  }
}

async function createJob() {
  creating.value = true
  try {
    await client.post('/api/v1/jobs', newJob)
    showJobForm.value = false
    newJob.product_query = ''
    newJob.target_price = null
    newJob.max_price = null
    newJob.location_city = ''
    newJob.auto_close = false
    await fetchJobs()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to create job')
  } finally {
    creating.value = false
  }
}

async function viewJob(jobId) {
  try {
    const res = await client.get(`/api/v1/jobs/${jobId}`)
    selectedJob.value = res.data
    const statusRes = await client.get(`/api/v1/jobs/${jobId}/status`)
    jobStatus.value = statusRes.data
  } catch (err) {
    console.error('Failed to fetch job:', err)
  }
}

async function deleteJob(jobId) {
  if (!confirm('Cancel this job?')) return
  try {
    await client.delete(`/api/v1/jobs/${jobId}`)
    await fetchJobs()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to cancel job')
  }
}

onMounted(async () => {
  if (token.value) {
    await fetchUser()
    await fetchJobs()
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  color: #1a1a2e;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-label {
  color: #666;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a2e;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.section h2 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: #1a1a2e;
}

.jobs-list {
  display: grid;
  gap: 1rem;
}

.job-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.job-header h3 {
  font-size: 1rem;
  color: #1a1a2e;
}

.job-details {
  display: flex gap: 1rem;
  color: #666;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.job-actions {
  display: flex gap: 0.5rem;
}

.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-danger {
  background: #dc2626;
}

.btn-danger:hover {
  background: #b91c1c;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4f46e5;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.switch-auth {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.switch-auth a {
  color: #4f46e5;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat {
  padding: 1rem;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat .label {
  display: block;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.stat .value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-queued {
  background: #fef3c7;
  color: #92400e;
}

.status-running {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.nav-links a {
  color: white;
  opacity: 0.8;
}

.user-email {
  color: white;
  opacity: 0.8;
  margin-right: 1rem;
}
</style>