# V3 Master Plan: Mobile-First Autonomous Negotiator

## Version: 3.0 — Mobile Native  
**Created:** April 2026  
**Status:** In Progress

---

## Branches

| Branch | Week | Status |
|--------|------|--------|
| `v3-week1-mobile-foundation` | Mobile Foundation | In Progress |
| `v3-week2-core-features` | Core Features | Pending |
| `v3-week3-advanced` | Advanced Features | Pending |

---

# Week 1: Mobile Foundation

## Tasks

### P1.1 Initialize React Native Project (Expo)
- [x] Set up Expo project
- [ ] Configure app.json
- [ ] Set up navigation

### P1.2 Authentication Screens
- [ ] LoginScreen.tsx
- [ ] RegisterScreen.tsx
- [ ] Auth context/hooks

### P1.3 API Client
- [ ] services/api.ts - Axios base client
- [ ] services/auth.ts - Auth endpoints

### P1.4 Job Creation
- [ ] JobCreateScreen.tsx
- [ ] Job form with validation

---

# Week 2: Core Mobile Features

## Tasks

### P2.1 Dashboard
- [ ] DashboardScreen.tsx
- [ ] Job cards with status

### P2.2 Push Notifications
- [ ] Expo notifications setup
- [ ] Device token registration
- [ ] Notification handling

### P2.3 Real-time Updates
- [ ] WebSocket client
- [ ] Live job status

### P2.4 Deal Views
- [ ] DealDetailScreen.tsx
- [ ] Negotiation timeline

---

# Week 3: Advanced Features

## Tasks

### P3.1 Auto-Buy
- [ ] Auto-buy toggle
- [ ] Instant purchase trigger

### P3.2 Price Alerts
- [ ] Price drop monitoring
- [ ] Alert preferences

### P3.3 Settings
- [ ] SettingsScreen.tsx
- [ ] Notification preferences

### P3.4 App Store Prep
- [ ] Icons/splash
- [ ] Build configurations

---

# Technical Stack

| Component | Technology |
|-----------|------------|
| Framework | React Native (Expo) |
| Navigation | React Navigation v7 |
| State | Zustand |
| HTTP | Axios |
| Push | Expo Notifications |
| Real-time | WebSocket |

---

# Architecture

```
mobile/
├── App.tsx
├── app.json
├── src/
│   ├── screens/
│   │   ├── AuthScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   ├── JobCreateScreen.tsx
│   │   ├── DealDetailScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/
│   │   ├── JobCard.tsx
│   │   ├── DealCard.tsx
│   │   └── Button.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── notifications.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useJobs.ts
│   │   └── useNotifications.ts
│   ├── store/
│   │   └── authStore.ts
│   └── types/
│       └── index.ts
```