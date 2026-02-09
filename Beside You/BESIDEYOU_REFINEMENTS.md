# BESIDEYOU: COMPREHENSIVE REFINEMENTS

## Addendum to Main Specification

**Version:** 2.0  
**Date:** January 2026  
**Purpose:** Incorporate reviewer feedback + define data persistence architecture  
**Status:** Ready for Replit development

---

# EXECUTIVE SUMMARY

This document refines the BesideYou specification based on feedback from 5 independent reviewers and resolves the critical question of data persistence.

**Key Decisions:**

1. **No backend required** — GitHub Pages hosts app code only
2. **Local-first architecture** — All data stored in browser IndexedDB
3. **Optional cloud sync** — User's own Google Drive/Dropbox (encrypted)
4. **Privacy promise preserved** — "We never see your data. We can't."
5. **Full app at launch** — Not MVP; complete feature set

**Reviewer Consensus:** 9.5/10 — "Profoundly compassionate and meticulously planned"

---

# PART 1: DATA PERSISTENCE ARCHITECTURE

## The Challenge

BesideYou stores sensitive, emotional data:
- Good Days Jar (memories over months/years)
- Symptom tracking (ongoing health data)
- Notes and moments (personal reflections)
- Journey timeline (treatment history)

This data must:
- Persist (not lost if browser cleared)
- Sync (accessible from phone AND laptop)
- Be secure (cancer data is deeply sensitive)
- Honour privacy promise (Almost Magic never sees it)

## The Solution: Local-First + User's Own Cloud

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  BESIDEYOU DATA ARCHITECTURE                                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: GITHUB PAGES (Static Hosting)                  │   │
│  │  ─────────────────────────────────────                   │   │
│  │  • App code (HTML/CSS/JS)                                │   │
│  │  • Medical glossary (JSON)                               │   │
│  │  • Resources directory (JSON)                            │   │
│  │  • PWA manifest & service worker                         │   │
│  │  • AI system prompts                                     │   │
│  │  • NO user data ever                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LAYER 2: USER'S BROWSER (IndexedDB)                     │   │
│  │  ───────────────────────────────────                     │   │
│  │  • All user data stored locally                          │   │
│  │  • Good Days Jar entries                                 │   │
│  │  • Symptom logs                                          │   │
│  │  • Medication tracking                                   │   │
│  │  • Notes and memories                                    │   │
│  │  • Journey timeline                                      │   │
│  │  • Settings and preferences                              │   │
│  │  • Works completely offline                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼ (optional)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LAYER 3: USER'S OWN CLOUD (Optional Sync)               │   │
│  │  ─────────────────────────────────────────               │   │
│  │  • Google Drive / Dropbox / iCloud                       │   │
│  │  • Data encrypted ON DEVICE before upload                │   │
│  │  • User's passphrase = encryption key                    │   │
│  │  • Almost Magic CANNOT read this data                    │   │
│  │  • Enables sync across multiple devices                  │   │
│  │  • User controls their own cloud account                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│  RESULT: No Almost Magic backend. No Almost Magic database.    │
│  GitHub Pages + User's Browser + User's Cloud.                 │
│  ═══════════════════════════════════════════════════════════   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Why This Architecture

| Principle | How This Honors It |
|-----------|-------------------|
| **Privacy** | Almost Magic never holds user data |
| **Persistence** | Data survives in user's cloud |
| **Trust** | "Your data, your cloud, your key" — verifiable |
| **Offline** | Local-first means app works without internet |
| **No ongoing costs** | GitHub Pages is free; user pays for their own cloud |
| **No breach liability** | Can't leak what we don't have |
| **Full functionality** | All features work, data persists across devices |

## What This Means

| Question | Answer |
|----------|--------|
| Do we need a backend? | **No** |
| Do we need user accounts? | **No** — passphrase only |
| Where does user data live? | Browser IndexedDB + optionally user's own cloud |
| Can they sync across devices? | **Yes** — via their own Google Drive/Dropbox |
| Do we ever see their data? | **No** — encrypted before it leaves their device |
| Can we host entirely on GitHub Pages? | **Yes** — app code only |

---

# PART 2: DATA STORAGE IMPLEMENTATION

## 2.1 Local Storage (IndexedDB)

### Database Schema

```typescript
// /lib/database.ts

interface BesideYouDatabase {
  // User profile (no PII required)
  profile: {
    id: 'profile';
    role: 'patient' | 'caregiver' | 'supporter';
    patientName?: string; // Optional, for caregiver mode
    createdAt: string;
    lastBackup?: string;
    cloudConnected?: 'google' | 'dropbox' | null;
  };
  
  // Good Days Jar
  goodDays: {
    id: string;
    date: string;
    content: string;
    tags?: string[];
    createdAt: string;
  }[];
  
  // Symptom Tracking
  symptoms: {
    id: string;
    date: string;
    symptom: string;
    severity: 1 | 2 | 3 | 4 | 5;
    notes?: string;
    relatedTo?: 'treatment' | 'medication' | 'other';
    createdAt: string;
  }[];
  
  // Medications
  medications: {
    id: string;
    name: string;
    dosage: string;
    frequency: string;
    startDate: string;
    endDate?: string;
    notes?: string;
    reminders: boolean;
  }[];
  
  // Appointments
  appointments: {
    id: string;
    date: string;
    type: 'oncologist' | 'gp' | 'specialist' | 'treatment' | 'scan' | 'other';
    location?: string;
    questions: string[];
    notes?: string;
    completed: boolean;
  }[];
  
  // Journey Timeline
  timeline: {
    id: string;
    date: string;
    type: 'diagnosis' | 'treatment' | 'scan' | 'milestone' | 'note';
    title: string;
    content?: string;
    createdAt: string;
  }[];
  
  // Notes / Things to Remember
  notes: {
    id: string;
    title?: string;
    content: string;
    category?: 'medical' | 'emotional' | 'practical' | 'other';
    pinned: boolean;
    createdAt: string;
    updatedAt: string;
  }[];
  
  // AI Conversation History (local only, not synced)
  conversations: {
    id: string;
    messages: {
      role: 'user' | 'assistant';
      content: string;
      timestamp: string;
    }[];
    createdAt: string;
  }[];
  
  // Glossary Favorites
  glossaryFavorites: string[]; // Array of term IDs
  
  // Settings
  settings: {
    theme: 'light' | 'dark' | 'auto';
    fontSize: 'normal' | 'large' | 'larger';
    voiceEnabled: boolean;
    notificationsEnabled: boolean;
    groqApiKey?: string; // Stored locally, never transmitted
    encryptionKeyHash?: string; // For verifying passphrase
  };
}
```

### IndexedDB Implementation

```typescript
// /lib/storage.ts

import { openDB, DBSchema, IDBPDatabase } from 'idb';

const DB_NAME = 'besideyou';
const DB_VERSION = 1;

interface BesideYouDB extends DBSchema {
  profile: { key: string; value: Profile };
  goodDays: { key: string; value: GoodDayEntry; indexes: { 'by-date': string } };
  symptoms: { key: string; value: SymptomEntry; indexes: { 'by-date': string } };
  medications: { key: string; value: Medication };
  appointments: { key: string; value: Appointment; indexes: { 'by-date': string } };
  timeline: { key: string; value: TimelineEntry; indexes: { 'by-date': string } };
  notes: { key: string; value: Note; indexes: { 'by-updated': string } };
  conversations: { key: string; value: Conversation };
  glossaryFavorites: { key: string; value: string };
  settings: { key: string; value: Settings };
}

export async function initDatabase(): Promise<IDBPDatabase<BesideYouDB>> {
  return openDB<BesideYouDB>(DB_NAME, DB_VERSION, {
    upgrade(db) {
      // Profile store
      db.createObjectStore('profile', { keyPath: 'id' });
      
      // Good Days store with date index
      const goodDaysStore = db.createObjectStore('goodDays', { keyPath: 'id' });
      goodDaysStore.createIndex('by-date', 'date');
      
      // Symptoms store with date index
      const symptomsStore = db.createObjectStore('symptoms', { keyPath: 'id' });
      symptomsStore.createIndex('by-date', 'date');
      
      // Medications store
      db.createObjectStore('medications', { keyPath: 'id' });
      
      // Appointments store with date index
      const appointmentsStore = db.createObjectStore('appointments', { keyPath: 'id' });
      appointmentsStore.createIndex('by-date', 'date');
      
      // Timeline store with date index
      const timelineStore = db.createObjectStore('timeline', { keyPath: 'id' });
      timelineStore.createIndex('by-date', 'date');
      
      // Notes store with updated index
      const notesStore = db.createObjectStore('notes', { keyPath: 'id' });
      notesStore.createIndex('by-updated', 'updatedAt');
      
      // Conversations store
      db.createObjectStore('conversations', { keyPath: 'id' });
      
      // Glossary favorites store
      db.createObjectStore('glossaryFavorites', { keyPath: 'id' });
      
      // Settings store
      db.createObjectStore('settings', { keyPath: 'id' });
    }
  });
}
```

## 2.2 Encryption (Client-Side)

### Encryption Module

```typescript
// /lib/encryption.ts

const SALT = 'besideyou-encryption-salt-v1';
const ITERATIONS = 100000;

export async function deriveKey(passphrase: string): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  
  // Import passphrase as key material
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(passphrase),
    'PBKDF2',
    false,
    ['deriveBits', 'deriveKey']
  );
  
  // Derive AES-GCM key
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode(SALT),
      iterations: ITERATIONS,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

export async function encrypt(data: object, passphrase: string): Promise<string> {
  const encoder = new TextEncoder();
  const dataString = JSON.stringify(data);
  const dataBuffer = encoder.encode(dataString);
  
  const key = await deriveKey(passphrase);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  
  const encryptedBuffer = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    dataBuffer
  );
  
  // Combine IV + encrypted data
  const combined = new Uint8Array(iv.length + encryptedBuffer.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(encryptedBuffer), iv.length);
  
  // Return as base64
  return btoa(String.fromCharCode(...combined));
}

export async function decrypt(encryptedData: string, passphrase: string): Promise<object> {
  const combined = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
  
  // Extract IV and encrypted data
  const iv = combined.slice(0, 12);
  const data = combined.slice(12);
  
  const key = await deriveKey(passphrase);
  
  const decryptedBuffer = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    key,
    data
  );
  
  const decoder = new TextDecoder();
  const decryptedString = decoder.decode(decryptedBuffer);
  
  return JSON.parse(decryptedString);
}

// Generate a hash of the passphrase for verification
export async function hashPassphrase(passphrase: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(passphrase + SALT);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(hashBuffer)));
}

// Verify passphrase matches stored hash
export async function verifyPassphrase(passphrase: string, storedHash: string): Promise<boolean> {
  const hash = await hashPassphrase(passphrase);
  return hash === storedHash;
}
```

## 2.3 Cloud Sync (User's Own Cloud)

### Google Drive Integration (Client-Side Only)

```typescript
// /lib/cloudSync/googleDrive.ts

const GOOGLE_CLIENT_ID = 'YOUR_CLIENT_ID'; // Public, safe to expose
const SCOPES = 'https://www.googleapis.com/auth/drive.file';
const BACKUP_FILENAME = 'besideyou-backup.encrypted';

// Initialize Google API
export async function initGoogleDrive(): Promise<void> {
  return new Promise((resolve, reject) => {
    gapi.load('client:auth2', async () => {
      try {
        await gapi.client.init({
          clientId: GOOGLE_CLIENT_ID,
          scope: SCOPES,
          discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/drive/v3/rest']
        });
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  });
}

// Sign in to Google
export async function signInGoogle(): Promise<boolean> {
  try {
    const authInstance = gapi.auth2.getAuthInstance();
    await authInstance.signIn();
    return authInstance.isSignedIn.get();
  } catch (error) {
    console.error('Google sign-in failed:', error);
    return false;
  }
}

// Sign out of Google
export function signOutGoogle(): void {
  const authInstance = gapi.auth2.getAuthInstance();
  authInstance.signOut();
}

// Check if signed in
export function isSignedInGoogle(): boolean {
  const authInstance = gapi.auth2.getAuthInstance();
  return authInstance?.isSignedIn.get() ?? false;
}

// Upload encrypted backup to Google Drive
export async function uploadToGoogleDrive(encryptedData: string): Promise<string> {
  // Check if file already exists
  const existingFileId = await findBackupFile();
  
  const file = new Blob([encryptedData], { type: 'application/octet-stream' });
  const metadata = {
    name: BACKUP_FILENAME,
    mimeType: 'application/octet-stream'
  };
  
  const form = new FormData();
  form.append('metadata', new Blob([JSON.stringify(metadata)], { type: 'application/json' }));
  form.append('file', file);
  
  const accessToken = gapi.auth.getToken().access_token;
  
  let url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart';
  let method = 'POST';
  
  // Update existing file instead of creating new one
  if (existingFileId) {
    url = `https://www.googleapis.com/upload/drive/v3/files/${existingFileId}?uploadType=multipart`;
    method = 'PATCH';
  }
  
  const response = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${accessToken}` },
    body: form
  });
  
  const result = await response.json();
  return result.id;
}

// Download encrypted backup from Google Drive
export async function downloadFromGoogleDrive(): Promise<string | null> {
  const fileId = await findBackupFile();
  if (!fileId) return null;
  
  const accessToken = gapi.auth.getToken().access_token;
  
  const response = await fetch(
    `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  
  return response.text();
}

// Find existing backup file
async function findBackupFile(): Promise<string | null> {
  const response = await gapi.client.drive.files.list({
    q: `name='${BACKUP_FILENAME}' and trashed=false`,
    fields: 'files(id, name, modifiedTime)',
    spaces: 'drive'
  });
  
  const files = response.result.files;
  return files && files.length > 0 ? files[0].id : null;
}

// Get last backup time
export async function getLastBackupTime(): Promise<Date | null> {
  const response = await gapi.client.drive.files.list({
    q: `name='${BACKUP_FILENAME}' and trashed=false`,
    fields: 'files(id, modifiedTime)',
    spaces: 'drive'
  });
  
  const files = response.result.files;
  if (files && files.length > 0) {
    return new Date(files[0].modifiedTime);
  }
  return null;
}
```

### Sync Manager

```typescript
// /lib/cloudSync/syncManager.ts

import { encrypt, decrypt, verifyPassphrase } from '../encryption';
import * as googleDrive from './googleDrive';
import { exportAllData, importAllData } from '../storage';

export type CloudProvider = 'google' | 'dropbox' | null;

interface SyncState {
  provider: CloudProvider;
  lastSync: Date | null;
  autoSync: boolean;
}

export async function syncToCloud(passphrase: string): Promise<boolean> {
  try {
    // Export all data from IndexedDB
    const data = await exportAllData();
    
    // Encrypt with user's passphrase
    const encryptedData = await encrypt(data, passphrase);
    
    // Upload to connected cloud provider
    const provider = await getConnectedProvider();
    
    if (provider === 'google') {
      await googleDrive.uploadToGoogleDrive(encryptedData);
    } else if (provider === 'dropbox') {
      // await dropbox.uploadToDropbox(encryptedData);
    }
    
    // Update last sync time
    await updateLastSyncTime();
    
    return true;
  } catch (error) {
    console.error('Sync failed:', error);
    return false;
  }
}

export async function syncFromCloud(passphrase: string): Promise<boolean> {
  try {
    const provider = await getConnectedProvider();
    let encryptedData: string | null = null;
    
    if (provider === 'google') {
      encryptedData = await googleDrive.downloadFromGoogleDrive();
    } else if (provider === 'dropbox') {
      // encryptedData = await dropbox.downloadFromDropbox();
    }
    
    if (!encryptedData) {
      console.log('No backup found in cloud');
      return false;
    }
    
    // Decrypt with user's passphrase
    const data = await decrypt(encryptedData, passphrase);
    
    // Import into IndexedDB
    await importAllData(data);
    
    return true;
  } catch (error) {
    console.error('Sync from cloud failed:', error);
    return false;
  }
}

// Auto-sync on data change (debounced)
let syncTimeout: NodeJS.Timeout | null = null;

export function triggerAutoSync(passphrase: string): void {
  if (syncTimeout) clearTimeout(syncTimeout);
  
  syncTimeout = setTimeout(async () => {
    const state = await getSyncState();
    if (state.provider && state.autoSync) {
      await syncToCloud(passphrase);
    }
  }, 30000); // Sync 30 seconds after last change
}
```

---

# PART 3: ONBOARDING & FIRST-RUN EXPERIENCE

## 3.1 First-Time Welcome Flow

### Screen 1: Welcome

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                          🌿                                     │
│                                                                 │
│                    Welcome to BesideYou                         │
│                                                                 │
│         A companion for the cancer journey.                     │
│         Free, private, and always here.                         │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🔒 Your privacy matters                                        │
│                                                                 │
│  Everything you create here stays on this device.               │
│  We never see your data. We can't.                              │
│                                                                 │
│  Your memories, your symptoms, your notes —                     │
│  they're yours alone.                                           │
│                                                                 │
│                                                                 │
│                       [Continue]                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 2: Who Is This For?

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              Who will be using BesideYou?                       │
│                                                                 │
│         (This helps us personalize your experience)             │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🧡  I am a patient                                      │   │
│  │      I'm navigating my own cancer journey.               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💙  I am a caregiver                                    │   │
│  │      I'm caring for someone with cancer.                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💚  I'm supporting someone                              │   │
│  │      A friend or family member has cancer.               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                                                 │
│                       [Skip for now]                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 3: What You Can Do Here

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                  Here's what BesideYou offers                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  📖  Understand                                                 │
│      Look up medical terms in plain language.                   │
│      1,499 terms explained simply.                              │
│                                                                 │
│  📋  Prepare                                                    │
│      Get ready for appointments with                            │
│      questions to ask your care team.                           │
│                                                                 │
│  📊  Track                                                      │
│      Log symptoms, medications, and                             │
│      how you're feeling over time.                              │
│                                                                 │
│  💛  Remember                                                   │
│      Collect good days, small moments,                          │
│      and things worth holding onto.                             │
│                                                                 │
│  🤝  Talk                                                       │
│      A gentle AI companion to explain                           │
│      things and listen when you need it.                        │
│                                                                 │
│                                                                 │
│                    [Get Started]                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 4: One More Thing (Optional)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     One more thing                              │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  BesideYou includes an AI companion that can:                   │
│  • Explain medical terms in conversation                        │
│  • Help you prepare questions for appointments                  │
│  • Listen when you need to talk                                 │
│                                                                 │
│  To use it, you'll need a free API key from Groq.               │
│  This is optional — the rest of BesideYou works without it.     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Set up AI Companion now]                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    [Skip — I'll do this later]                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ℹ️  You can always set this up later in Settings.              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 "Start Here" Simplification

### The Problem
Users arrive overwhelmed. The full feature set may paralyze someone in crisis.

### The Solution
Add a "Start Here" mode that appears on the home screen.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  You don't need to use everything here.                         │
│                                                                 │
│  Most people start with just one thing:                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📖  Look up a word I heard today                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📋  Prepare for one appointment                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤝  I just need to talk to someone                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  😮‍💨  I need a moment to breathe                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                                                 │
│                  [See all features]                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# PART 4: AI COMPANION REFINEMENTS

## 4.1 AI Offline Mode

### The Problem
The spec says the AI falls back to "local responses" when offline, but doesn't define what those are.

### The Solution
Define explicit offline capabilities.

### Offline Capabilities

```typescript
// /lib/ai/offlineResponses.ts

export const offlineCapabilities = {
  // What AI CAN do offline
  canDo: [
    'Search and explain all 1,499 glossary terms',
    'Provide pre-written emotional support responses',
    'Offer appointment preparation questions',
    'Share grounding exercises and breathing techniques',
    'Display crisis support resources'
  ],
  
  // What AI CANNOT do offline
  cannotDo: [
    'Have free-form conversations',
    'Answer questions not in the glossary',
    'Provide personalized responses',
    'Remember conversation context'
  ]
};

// Pre-written responses for common emotional queries
export const emotionalResponses = {
  scared: {
    triggers: ['scared', 'afraid', 'frightened', 'terrified', 'fear'],
    response: `It's okay to feel scared. Cancer is frightening, and your feelings are completely valid.

Right now, you might try:
• Taking three slow, deep breaths
• Naming five things you can see around you
• Reaching out to someone who cares about you

If you're feeling overwhelmed, the Cancer Council helpline (13 11 20) has trained counselors who understand what you're going through.

You don't have to face this alone.`
  },
  
  alone: {
    triggers: ['alone', 'lonely', 'isolated', 'no one understands'],
    response: `Feeling alone in this is so hard. Even when people around you care, cancer can feel isolating.

You might find connection through:
• Cancer Council support groups (13 11 20)
• Online communities of people who truly understand
• Talking to a counselor who specializes in cancer support

Your feelings matter, and there are people who want to walk this path with you.`
  },
  
  overwhelmed: {
    triggers: ['overwhelmed', 'too much', 'can\'t cope', 'drowning'],
    response: `When everything feels like too much, it's okay to stop and just breathe.

You don't have to figure everything out right now. You just have to get through this moment.

Try this:
• Breathe in for 4 counts
• Hold for 4 counts  
• Breathe out for 4 counts
• Repeat 3 times

What's one tiny thing you could do right now? Just one small thing.`
  },
  
  angry: {
    triggers: ['angry', 'furious', 'unfair', 'why me'],
    response: `Anger is a completely normal response to cancer. It IS unfair. You have every right to feel this way.

Your anger doesn't make you a bad person. It makes you human.

If the anger feels too big to hold:
• Writing it out can help (even if you delete it after)
• Physical movement, if you're able
• Talking to someone who won't try to fix it, just listen

The Cancer Council (13 11 20) has counselors who understand this anger.`
  },
  
  tired: {
    triggers: ['tired', 'exhausted', 'fatigued', 'no energy'],
    response: `Cancer fatigue is real and overwhelming. It's not regular tiredness — it's deeper than that.

Be gentle with yourself. Your body is fighting hard.

What might help:
• Rest without guilt
• Small movements when you can
• Accepting help from others
• Talking to your care team about fatigue management

You're doing more than you know, even when it doesn't feel that way.`
  },
  
  crying: {
    triggers: ['crying', 'tears', 'can\'t stop crying', 'breaking down'],
    response: `Let the tears come. They're not weakness — they're release.

Crying is your body's way of processing something too big for words.

You don't have to be strong right now. You don't have to hold it together.

If you need someone to talk to, the Cancer Council helpline (13 11 20) is available. They won't judge your tears.`
  },
  
  dying: {
    triggers: ['going to die', 'dying', 'death', 'won\'t survive'],
    response: `These thoughts are terrifying to have. I'm so sorry you're carrying this weight.

I can't tell you what will happen. No one can. But I can tell you that you're not alone in these fears.

Please talk to someone who can truly support you:
• Cancer Council: 13 11 20
• Lifeline: 13 11 14
• Your care team — they can discuss your prognosis honestly

You deserve support right now. Please reach out.`
  }
};

// Pre-written practical responses
export const practicalResponses = {
  sideEffects: {
    triggers: ['side effects', 'nausea', 'hair loss', 'fatigue', 'pain'],
    response: `Side effects can be really difficult. Here are some general things that might help:

• Keep a symptom diary to share with your care team
• Don't hesitate to report side effects — many can be managed
• Stay hydrated when possible
• Rest when you need to

For specific side effects, please search our glossary or talk to your care team. They can adjust your treatment plan.

What symptom are you dealing with? I can look it up for you.`
  },
  
  appointment: {
    triggers: ['appointment', 'doctor', 'oncologist', 'what to ask'],
    response: `Preparing for appointments helps you make the most of your time with the care team.

Some questions that often help:
• "What are my treatment options?"
• "What side effects should I watch for?"
• "What symptoms should I report immediately?"
• "Who should I contact if I have questions between visits?"

Would you like me to help you prepare for a specific type of appointment?`
  }
};

// Grounding exercises for offline use
export const groundingExercises = {
  breathing: {
    name: 'Box Breathing',
    duration: '2 minutes',
    steps: [
      'Breathe in slowly for 4 counts',
      'Hold your breath for 4 counts',
      'Breathe out slowly for 4 counts',
      'Hold empty for 4 counts',
      'Repeat 4 times'
    ]
  },
  
  fiveSenses: {
    name: '5-4-3-2-1 Grounding',
    duration: '3 minutes',
    steps: [
      'Name 5 things you can SEE',
      'Name 4 things you can TOUCH',
      'Name 3 things you can HEAR',
      'Name 2 things you can SMELL',
      'Name 1 thing you can TASTE'
    ]
  },
  
  bodyRelaxation: {
    name: 'Progressive Relaxation',
    duration: '5 minutes',
    steps: [
      'Close your eyes if comfortable',
      'Tense your feet for 5 seconds, then release',
      'Tense your calves for 5 seconds, then release',
      'Continue up through your body',
      'End with your face and jaw',
      'Notice the difference between tension and relaxation'
    ]
  }
};
```

### Offline Mode UI

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  📴 Offline Mode                                                │
│                                                                 │
│  You're not connected to the internet right now.                │
│  That's okay — here's what I can still help with:               │
│                                                                 │
│  ✓ Explain any medical term from the glossary                   │
│  ✓ Offer grounding exercises and breathing techniques           │
│  ✓ Share crisis support resources                               │
│  ✓ Provide appointment preparation questions                    │
│                                                                 │
│  When you're back online, I'll be able to have fuller           │
│  conversations again.                                           │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  What would you like help with?                                 │
│                                                                 │
│  [Look up a term]  [Grounding exercise]  [Crisis support]       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 4.2 AI Safety Reinforcement

### Mandatory Acknowledgment (First AI Use)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                Before we begin                                  │
│                                                                 │
│  The AI companion is here to support you — but it has limits.   │
│                                                                 │
│  ✓ I CAN explain medical terms in plain language                │
│  ✓ I CAN help you prepare questions for your care team          │
│  ✓ I CAN listen when you need to talk                           │
│  ✓ I CAN offer comfort and emotional support                    │
│                                                                 │
│  ✗ I CANNOT give medical advice                                 │
│  ✗ I CANNOT diagnose symptoms                                   │
│  ✗ I CANNOT tell you to change medications                      │
│  ✗ I CANNOT replace your doctors or care team                   │
│                                                                 │
│  Please always discuss medical decisions with your care team.   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ☑️  I understand this is not medical advice             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    [Start Conversation]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Persistent Disclaimer (Below Chat Input)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Chat messages...]                                             │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Type a message...                               [Send] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ℹ️  I can explain and support, but I can't give medical        │
│     advice. Always talk to your care team about treatment.      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Hard-Coded Crisis Responses

Certain queries must NEVER go to the AI. They trigger immediate crisis resources.

```typescript
// /lib/ai/crisisDetection.ts

export const crisisPatterns = {
  suicidal: {
    patterns: [
      /want to (die|end it|kill myself)/i,
      /suicid/i,
      /don't want to (live|be here|exist)/i,
      /better off (dead|without me)/i,
      /no point in living/i,
      /end my life/i
    ],
    response: 'suicidal',
    bypassAI: true
  },
  
  selfHarm: {
    patterns: [
      /hurt myself/i,
      /cut myself/i,
      /self.?harm/i
    ],
    response: 'selfHarm',
    bypassAI: true
  },
  
  stopTreatment: {
    patterns: [
      /stop (my )?(treatment|chemo|medication)/i,
      /refuse (treatment|chemo)/i,
      /don't want (treatment|chemo)/i,
      /giving up on treatment/i
    ],
    response: 'stopTreatment',
    bypassAI: true
  },
  
  medicalEmergency: {
    patterns: [
      /can't breathe/i,
      /chest pain/i,
      /severe (pain|bleeding)/i,
      /temperature (over|above) (38|39|40)/i,
      /emergency/i
    ],
    response: 'emergency',
    bypassAI: true
  }
};

export const crisisResponses = {
  suicidal: {
    message: `I can hear that you're in a really dark place right now. These feelings are serious, and you deserve support from someone trained to help.

Please reach out right now:

🆘 Lifeline: 13 11 14 (24/7)
🆘 Suicide Call Back: 1300 659 467
🆘 Beyond Blue: 1300 22 4636

If you're in immediate danger, please call 000.

You matter. Please reach out.`,
    showResources: true,
    logLocally: true
  },
  
  selfHarm: {
    message: `I'm concerned about what you've shared. You deserve support from someone who can really help.

Please talk to:
🆘 Lifeline: 13 11 14 (24/7)
🆘 Kids Helpline: 1800 55 1800
🆘 Your care team

You don't have to go through this alone.`,
    showResources: true,
    logLocally: true
  },
  
  stopTreatment: {
    message: `Treatment decisions are deeply personal, and it's okay to have doubts or feel like you've had enough.

But please — before making any changes to your treatment:

📞 Talk to your oncologist about how you're feeling
📞 Call Cancer Council (13 11 20) to talk through your thoughts
📞 Consider speaking with a counselor who understands cancer

Your feelings matter. Your care team needs to know how you're feeling so they can support you properly.`,
    showResources: true,
    logLocally: false
  },
  
  emergency: {
    message: `This sounds like it might be a medical emergency.

🚨 If you're experiencing severe symptoms, please:

• Call 000 immediately
• Go to your nearest emergency department
• Contact your cancer care team's emergency line

Don't wait to see if it gets better. Please get help now.`,
    showResources: true,
    logLocally: true
  }
};
```

---

# PART 5: BACKUP & SYNC USER EXPERIENCE

## 5.1 Backup Prompt (After Data Accumulates)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                   Your memories matter                          │
│                                                                 │
│  You've been collecting moments for 3 weeks now.                │
│  12 good days. 28 symptom logs. 5 notes.                        │
│                                                                 │
│  Would you like to back them up?                                │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💾  Download Backup File                                │   │
│  │                                                          │   │
│  │  Save an encrypted file to your device.                  │   │
│  │  You can restore it anytime.                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ☁️  Connect Your Cloud                                  │   │
│  │                                                          │   │
│  │  Sync automatically to your own Google Drive.            │   │
│  │  Access from any device. We never see the data.          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    [Remind me later]                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 5.2 Cloud Connection Flow

### Step 1: Choose Provider

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                   Connect Your Cloud                            │
│                                                                 │
│  Your data will be encrypted on this device before it's         │
│  saved to your cloud. We never see it — only you have the key.  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Choose where to save your backup:                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [G]  Google Drive                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [D]  Dropbox                                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                       [Cancel]                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Create Passphrase

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                   Create Your Passphrase                        │
│                                                                 │
│  This passphrase encrypts your data. Without it, no one —       │
│  not even us — can read your backup.                            │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Enter passphrase: ________________________________     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Confirm passphrase: ________________________________   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ⚠️  IMPORTANT: If you forget this passphrase, your backup      │
│     cannot be recovered. We cannot help you — we don't have     │
│     the key. Please write it down somewhere safe.               │
│                                                                 │
│                                                                 │
│                    [Connect & Encrypt]                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Confirmation

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                        ✓ Connected                              │
│                                                                 │
│  Your data is now syncing to your Google Drive.                 │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🔒 How it works:                                               │
│                                                                 │
│  1. Your data is encrypted on this device                       │
│  2. The encrypted file is saved to YOUR Google Drive            │
│  3. We never see it — only you have the passphrase              │
│  4. Access from any device by entering your passphrase          │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Last synced: Just now                                          │
│  Next auto-sync: In 30 seconds after changes                    │
│                                                                 │
│                       [Done]                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# PART 6: GOOD DAYS JAR (Elevated to Core Feature)

## 6.1 Promotion to Core Feature

The Good Days Jar is no longer P2. It's a core feature because:
- High emotional impact
- Low implementation cost
- Differentiates BesideYou from clinical tools
- Provides hope during difficult times

## 6.2 Integration with Other Features

### Automatic Prompts

```typescript
// /lib/goodDaysIntegration.ts

// After logging a good symptom day
export function checkGoodDayPrompt(symptomLog: SymptomEntry): boolean {
  const avgSeverity = symptomLog.severity;
  return avgSeverity <= 2; // Low severity = potential good day
}

export const goodDayPrompt = {
  afterGoodSymptoms: `It sounds like today was a better day. 
    Would you like to add a note to your Good Days Jar?`,
  
  afterMilestone: `You've reached a milestone in your journey. 
    Would you like to capture this moment?`,
  
  randomReminder: `Even small moments of light matter. 
    Is there anything good from today worth remembering?`
};

// After logging difficult symptoms
export function checkComfortPrompt(symptomLog: SymptomEntry): boolean {
  const avgSeverity = symptomLog.severity;
  return avgSeverity >= 4; // High severity = might need comfort
}

export const comfortPrompt = {
  afterDifficultDay: `Today sounds hard. Would you like to look at 
    a memory from your Good Days Jar?`
};
```

### Empty State Design

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                       🫙 Good Days Jar                          │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│                         [Empty jar illustration]                │
│                                                                 │
│  Even on the hardest days, there can be small moments of light. │
│                                                                 │
│  A kind word. A good cup of tea. A moment of sunshine.          │
│  A text from someone who cares. A show that made you smile.     │
│                                                                 │
│  This is a place to collect them.                               │
│                                                                 │
│  On difficult days, you can come back here and remember:        │
│  good moments exist, even in this journey.                      │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  What was good today?                                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Write something...                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    [Add to Jar]                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# PART 7: CAREGIVER MODE

## 7.1 Adaptive Language

Based on role selection during onboarding, adjust language throughout the app.

```typescript
// /lib/caregiverMode.ts

interface ModeConfig {
  symptomPrompt: string;
  goodDayPrompt: string;
  appointmentPrompt: string;
  aiGreeting: string;
}

export const patientMode: ModeConfig = {
  symptomPrompt: "How are you feeling today?",
  goodDayPrompt: "What was good about today?",
  appointmentPrompt: "What questions do you want to ask?",
  aiGreeting: "I'm here to support you through your cancer journey."
};

export const caregiverMode: ModeConfig = {
  symptomPrompt: "How is [Patient Name] feeling today?",
  goodDayPrompt: "What was a good moment with [Patient Name] today?",
  appointmentPrompt: "What questions do you want to ask about [Patient Name]'s care?",
  aiGreeting: "I'm here to support you as you care for someone you love."
};

export const supporterMode: ModeConfig = {
  symptomPrompt: "How is your loved one doing today?",
  goodDayPrompt: "What was a meaningful moment today?",
  appointmentPrompt: "What would you like to understand better?",
  aiGreeting: "I'm here to help you support someone going through cancer."
};
```

## 7.2 Caregiver-Specific Resources

Add a dedicated section in Resources for caregivers:

```typescript
export const caregiverResources = [
  {
    title: "Caring for Yourself While Caring for Others",
    description: "You can't pour from an empty cup. Tips for caregiver wellbeing.",
    type: "article"
  },
  {
    title: "Caregiver Support Groups",
    description: "Connect with others who understand what you're going through.",
    link: "https://www.cancercouncil.com.au/get-support/caregiver-support/",
    type: "service"
  },
  {
    title: "Respite Care Options",
    description: "Taking a break isn't abandonment. It's necessary.",
    type: "service"
  },
  {
    title: "Talking to Children About Cancer",
    description: "Age-appropriate guidance for difficult conversations.",
    type: "guide"
  },
  {
    title: "Managing Work and Caregiving",
    description: "Your rights, options, and practical strategies.",
    type: "guide"
  },
  {
    title: "Carer Gateway",
    description: "Australian Government support for carers.",
    phone: "1800 422 737",
    link: "https://www.carergateway.gov.au/",
    type: "service"
  }
];
```

---

# PART 8: GLOSSARY SCOPE DECISION

## 8.1 The Challenge

1,499 terms is a massive content creation task that could delay launch.

## 8.2 The Decision: Full Glossary at Launch

Per your direction, we will provide the **full app** at launch, not an MVP. This means all 1,499 terms.

## 8.3 Glossary Content Strategy

### Content Sources (Ethical, Verifiable)

```typescript
export const glossarySources = {
  primary: [
    {
      name: "Cancer Council Australia",
      url: "https://www.cancer.org.au/",
      usage: "Definitions, treatment explanations, Australian context"
    },
    {
      name: "Cancer Australia",
      url: "https://www.canceraustralia.gov.au/",
      usage: "Clinical terms, statistics, guidelines"
    },
    {
      name: "Peter MacCallum Cancer Centre",
      url: "https://www.petermac.org/",
      usage: "Treatment terms, research terminology"
    }
  ],
  secondary: [
    {
      name: "National Cancer Institute (US)",
      url: "https://www.cancer.gov/publications/dictionaries/cancer-terms",
      usage: "Comprehensive term list (adapt for Australian context)"
    },
    {
      name: "Macmillan Cancer Support (UK)",
      url: "https://www.macmillan.org.uk/",
      usage: "Plain language explanations (adapt for Australian context)"
    }
  ]
};
```

### Glossary Entry Schema

```typescript
interface GlossaryEntry {
  id: string;
  term: string;
  pronunciation?: string;
  plainExplanation: string; // Max 100 words, 8th grade reading level
  doctorMightSay: string[]; // Phrases a doctor might use
  youCanAsk: string[]; // Questions patient can ask
  relatedTerms: string[];
  category: 'diagnosis' | 'treatment' | 'side-effect' | 'procedure' | 'anatomy' | 'test' | 'general';
  cancerTypes?: string[]; // Which cancers this relates to
  lastReviewed: string; // ISO date
  sources: string[];
}
```

### Example Entry

```json
{
  "id": "chemotherapy",
  "term": "Chemotherapy",
  "pronunciation": "kee-moh-THER-uh-pee",
  "plainExplanation": "Chemotherapy uses medicines to kill cancer cells or stop them from growing. It can be given as tablets, injections, or through a drip into your vein. It travels through your whole body, which is why it can cause side effects in areas that don't have cancer.",
  "doctorMightSay": [
    "We recommend a course of chemo",
    "You'll have six cycles of chemotherapy",
    "This is a systemic treatment"
  ],
  "youCanAsk": [
    "What side effects should I expect?",
    "How long will each treatment take?",
    "Will I be able to work during treatment?",
    "What should I do if I feel unwell between sessions?"
  ],
  "relatedTerms": ["cycle", "infusion", "systemic-treatment", "anti-nausea", "neutropenia"],
  "category": "treatment",
  "cancerTypes": ["all"],
  "lastReviewed": "2026-01-15",
  "sources": ["Cancer Council Australia", "Cancer Australia"]
}
```

---

# PART 9: EMPTY STATE DESIGNS

## 9.1 Symptom Tracker Empty State

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    📊 Symptom Tracker                           │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│                   [Empty chart illustration]                    │
│                                                                 │
│  Tracking your symptoms helps you have clearer conversations    │
│  with your care team.                                           │
│                                                                 │
│  You don't have to track everything — even noting one           │
│  symptom that's bothering you can help.                         │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Common symptoms to track:                                      │
│                                                                 │
│  [Fatigue]  [Nausea]  [Pain]  [Sleep]  [Mood]  [+ Custom]      │
│                                                                 │
│                   [Log First Symptom]                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 9.2 Notes Empty State

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      📝 Notes                                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│                   [Empty notebook illustration]                 │
│                                                                 │
│  This is your space to write down anything you want to          │
│  remember.                                                      │
│                                                                 │
│  Things like:                                                   │
│  • Questions that come to you at 3am                            │
│  • Something your doctor said that you want to look up          │
│  • A resource someone recommended                               │
│  • Thoughts you're not ready to share yet                       │
│                                                                 │
│  These notes are private. Only you can see them.                │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│                    [Write First Note]                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 9.3 Appointments Empty State

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    📋 Appointments                              │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│                   [Calendar illustration]                       │
│                                                                 │
│  Preparing for appointments helps you make the most of          │
│  your time with your care team.                                 │
│                                                                 │
│  We'll help you:                                                │
│  • Prepare questions to ask                                     │
│  • Note what you want to discuss                                │
│  • Remember what was said after                                 │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  What type of appointment do you have coming up?                │
│                                                                 │
│  [Oncologist]  [GP]  [Scan]  [Treatment]  [Other]              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# PART 10: TECHNICAL IMPLEMENTATION FOR REPLIT

## 10.1 File Structure

```
/besideyou
├── index.html                    # Single-file PWA entry
├── manifest.json                 # PWA manifest
├── sw.js                         # Service worker for offline
│
├── /src
│   ├── /components
│   │   ├── /onboarding
│   │   │   ├── Welcome.tsx
│   │   │   ├── RoleSelection.tsx
│   │   │   ├── FeatureIntro.tsx
│   │   │   └── ApiKeySetup.tsx
│   │   │
│   │   ├── /glossary
│   │   │   ├── GlossarySearch.tsx
│   │   │   ├── GlossaryEntry.tsx
│   │   │   └── GlossaryFavorites.tsx
│   │   │
│   │   ├── /tracking
│   │   │   ├── SymptomTracker.tsx
│   │   │   ├── SymptomEntry.tsx
│   │   │   ├── MedicationTracker.tsx
│   │   │   └── SymptomChart.tsx
│   │   │
│   │   ├── /appointments
│   │   │   ├── AppointmentList.tsx
│   │   │   ├── AppointmentPrep.tsx
│   │   │   └── QuestionBuilder.tsx
│   │   │
│   │   ├── /gooddays
│   │   │   ├── GoodDaysJar.tsx
│   │   │   ├── GoodDayEntry.tsx
│   │   │   └── JarVisualization.tsx
│   │   │
│   │   ├── /companion
│   │   │   ├── AICompanion.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── CrisisDetection.tsx
│   │   │   └── OfflineMode.tsx
│   │   │
│   │   ├── /notes
│   │   │   ├── NotesList.tsx
│   │   │   └── NoteEditor.tsx
│   │   │
│   │   ├── /resources
│   │   │   ├── ResourceDirectory.tsx
│   │   │   └── CrisisResources.tsx
│   │   │
│   │   ├── /emotional
│   │   │   ├── GroundingExercises.tsx
│   │   │   ├── BreathingExercise.tsx
│   │   │   └── MomentsOfPeace.tsx
│   │   │
│   │   ├── /settings
│   │   │   ├── Settings.tsx
│   │   │   ├── BackupRestore.tsx
│   │   │   ├── CloudSync.tsx
│   │   │   └── PassphraseSetup.tsx
│   │   │
│   │   └── /common
│   │       ├── Navigation.tsx
│   │       ├── EmptyState.tsx
│   │       ├── LoadingState.tsx
│   │       └── ErrorBoundary.tsx
│   │
│   ├── /lib
│   │   ├── database.ts           # IndexedDB implementation
│   │   ├── storage.ts            # Data access layer
│   │   ├── encryption.ts         # Client-side encryption
│   │   ├── /cloudSync
│   │   │   ├── googleDrive.ts
│   │   │   ├── dropbox.ts
│   │   │   └── syncManager.ts
│   │   ├── /ai
│   │   │   ├── groqClient.ts
│   │   │   ├── systemPrompt.ts
│   │   │   ├── crisisDetection.ts
│   │   │   └── offlineResponses.ts
│   │   └── caregiverMode.ts
│   │
│   ├── /content
│   │   ├── glossary.json         # 1,499 terms
│   │   ├── resources.json        # Australian support resources
│   │   ├── appointmentQuestions.json
│   │   └── groundingExercises.json
│   │
│   └── /styles
│       ├── tokens.css            # Design tokens
│       ├── components.css        # Component styles
│       └── themes.css            # Light/dark themes
│
├── /public
│   ├── icons/                    # PWA icons
│   └── images/                   # Illustrations
│
└── README.md
```

## 10.2 Technology Stack

```typescript
const techStack = {
  framework: 'React 18 + TypeScript',
  styling: 'Tailwind CSS',
  storage: 'IndexedDB via idb library',
  encryption: 'Web Crypto API (native)',
  ai: 'Groq API (user-provided key)',
  pwa: 'Workbox for service worker',
  hosting: 'GitHub Pages (static)',
  build: 'Vite'
};
```

## 10.3 Build Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/*.png'],
      manifest: {
        name: 'BesideYou',
        short_name: 'BesideYou',
        description: 'A companion for the cancer journey',
        theme_color: '#F5E6D3',
        background_color: '#FFFAF5',
        display: 'standalone',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,json,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.groq\.com/,
            handler: 'NetworkOnly'
          }
        ]
      }
    })
  ],
  base: '/besideyou/',
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: {
          glossary: ['./src/content/glossary.json']
        }
      }
    }
  }
});
```

## 10.4 GitHub Pages Deployment

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

---

# PART 11: SUMMARY & CHECKLIST FOR REPLIT

## What Replit Needs to Build

### Core Features (All Required)

- [ ] **Onboarding flow** (4 screens, role selection)
- [ ] **Medical glossary** (search, browse, favorites, 1,499 terms)
- [ ] **AI Companion** (Groq integration, offline fallback, crisis detection)
- [ ] **Symptom tracker** (logging, visualization, export)
- [ ] **Medication tracker** (list, reminders, interactions note)
- [ ] **Appointment prep** (by type, question builder, notes)
- [ ] **Good Days Jar** (entries, visualization, integration prompts)
- [ ] **Notes** (create, edit, categorize, pin)
- [ ] **Journey timeline** (milestones, treatments, events)
- [ ] **Resources directory** (Australian services, crisis lines)
- [ ] **Emotional support** (grounding exercises, breathing, moments of peace)
- [ ] **Settings** (theme, font size, API key, backup)

### Data Layer

- [ ] **IndexedDB storage** (all user data local)
- [ ] **Encryption module** (passphrase-based AES-256-GCM)
- [ ] **Manual backup/restore** (encrypted JSON export)
- [ ] **Cloud sync** (Google Drive integration, client-side only)
- [ ] **Passphrase management** (creation, verification, change)

### Safety Features

- [ ] **AI acknowledgment** (mandatory before first use)
- [ ] **Persistent disclaimer** (below chat input)
- [ ] **Crisis detection** (keyword patterns, immediate resources)
- [ ] **Hard-coded crisis responses** (bypass AI entirely)
- [ ] **Offline mode** (defined capabilities, pre-written responses)

### UX Features

- [ ] **"Start Here" mode** (simplified entry for overwhelmed users)
- [ ] **Empty states** (all major features)
- [ ] **Caregiver mode** (language adaptation)
- [ ] **Backup prompts** (periodic reminders)
- [ ] **Progressive disclosure** (don't overwhelm)

### Technical Requirements

- [ ] **PWA** (offline-capable, installable)
- [ ] **Service worker** (cache glossary, resources)
- [ ] **Responsive design** (mobile-first)
- [ ] **Accessibility** (WCAG 2.1 AA)
- [ ] **GitHub Pages deployment** (static hosting)
- [ ] **No backend** (everything client-side)

---

## Documents for Replit

| Document | Purpose |
|----------|---------|
| **BESIDEYOU_COMPLETE_SPEC.md** | Main specification (original) |
| **BESIDEYOU_REFINEMENTS.md** | This document — refinements + data architecture |

Together, these provide a complete blueprint for development.

---

**Status: Ready for development.**

*Document Version: 2.0*  
*January 2026*  
*Almost Magic Tech Lab*
