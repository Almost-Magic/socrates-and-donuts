import { openDB, DBSchema } from 'idb';

interface SocratesDonutsDB extends DBSchema {
  conversations: {
    key: string;
    value: {
      id: string;
      messages: Array<{ role: 'user' | 'assistant'; content: string; timestamp: number }>;
      flowType?: string;
      createdAt: number;
      updatedAt: number;
    };
    indexes: { 'by-date': number };
  };
  vaultEntries: {
    key: string;
    value: {
      id: string;
      content: string;
      createdAt: number;
      unlocksAt: number;
      status: 'locked' | 'unlocked' | 'sent' | 'edited' | 'discarded';
      recipientContext?: string;
      aiReflection?: string;
    };
    indexes: { 'by-date': number; 'by-status': string };
  };
  letters: {
    key: string;
    value: {
      id: string;
      content: string;
      createdAt: number;
      burnedAt?: number;
    };
    indexes: { 'by-date': number };
  };
  quickCaptures: {
    key: string;
    value: {
      id: string;
      content: string;
      tags: string[];
      timestamp: number;
    };
    indexes: { 'by-date': number; 'by-tag': string };
  };
  decisions: {
    key: string;
    value: {
      id: string;
      question: string;
      reasoning: string;
      emotionalState: string;
      fears: string;
      hopes: string;
      reviewDate: number;
      createdAt: number;
    };
    indexes: { 'by-review-date': number };
  };
  emotionalWeather: {
    key: string;
    value: {
      id: string;
      weather: string;
      intensity?: string;
      notes?: string;
      timestamp: number;
    };
    indexes: { 'by-date': number };
  };
  bodySensations: {
    key: string;
    value: {
      id: string;
      x: number;
      y: number;
      type: string;
      rating: 'pleasant' | 'unpleasant' | 'neutral';
      context?: string;
      timestamp: number;
    };
    indexes: { 'by-date': number };
  };
  wisdomBookmarks: {
    key: string;
    value: {
      id: string;
      passageId: string;
      createdAt: number;
    };
  };
  settings: {
    key: string;
    value: {
      key: string;
      value: unknown;
    };
  };
}

const DB_NAME = 'socrates-and-donuts';
const DB_VERSION = 1;

type StoreNames = 'conversations' | 'vaultEntries' | 'letters' | 'quickCaptures' | 'decisions' | 'emotionalWeather' | 'bodySensations' | 'wisdomBookmarks' | 'settings';

export async function getDB() {
  return openDB<SocratesDonutsDB>(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('conversations')) {
        const convStore = db.createObjectStore('conversations', { keyPath: 'id' });
        convStore.createIndex('by-date', 'createdAt');
      }
      if (!db.objectStoreNames.contains('vaultEntries')) {
        const vaultStore = db.createObjectStore('vaultEntries', { keyPath: 'id' });
        vaultStore.createIndex('by-date', 'createdAt');
        vaultStore.createIndex('by-status', 'status');
      }
      if (!db.objectStoreNames.contains('letters')) {
        const letterStore = db.createObjectStore('letters', { keyPath: 'id' });
        letterStore.createIndex('by-date', 'createdAt');
      }
      if (!db.objectStoreNames.contains('quickCaptures')) {
        const captureStore = db.createObjectStore('quickCaptures', { keyPath: 'id' });
        captureStore.createIndex('by-date', 'timestamp');
        captureStore.createIndex('by-tag', 'tags', { multiEntry: true });
      }
      if (!db.objectStoreNames.contains('decisions')) {
        const decisionStore = db.createObjectStore('decisions', { keyPath: 'id' });
        decisionStore.createIndex('by-review-date', 'reviewDate');
      }
      if (!db.objectStoreNames.contains('emotionalWeather')) {
        const weatherStore = db.createObjectStore('emotionalWeather', { keyPath: 'id' });
        weatherStore.createIndex('by-date', 'timestamp');
      }
      if (!db.objectStoreNames.contains('bodySensations')) {
        const bodyStore = db.createObjectStore('bodySensations', { keyPath: 'id' });
        bodyStore.createIndex('by-date', 'timestamp');
      }
      if (!db.objectStoreNames.contains('wisdomBookmarks')) {
        db.createObjectStore('wisdomBookmarks', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('settings')) {
        db.createObjectStore('settings', { keyPath: 'key' });
      }
    },
  });
}

export async function exportData() {
  const db = await getDB();
  const data: Record<string, unknown[]> = {};

  const storeNames: StoreNames[] = [
    'conversations', 'vaultEntries', 'letters', 'quickCaptures', 'decisions',
    'emotionalWeather', 'bodySensations', 'wisdomBookmarks', 'settings'
  ];

  for (const storeName of storeNames) {
    data[storeName] = await db.getAll(storeName);
  }

  return JSON.stringify(data, null, 2);
}

export async function importData(jsonData: string) {
  const db = await getDB();
  const data = JSON.parse(jsonData);

  const tx = db.transaction(
    ['conversations', 'vaultEntries', 'letters', 'quickCaptures', 'decisions',
     'emotionalWeather', 'bodySensations', 'wisdomBookmarks', 'settings'],
    'readwrite'
  );

  const storeNames: StoreNames[] = [
    'conversations', 'vaultEntries', 'letters', 'quickCaptures', 'decisions',
    'emotionalWeather', 'bodySensations', 'wisdomBookmarks', 'settings'
  ];

  for (const storeName of storeNames) {
    const items = data[storeName] || [];
    for (const item of items) {
      await tx.objectStore(storeName).put(item as SocratesDonutsDB[StoreNames]['value']);
    }
  }

  await tx.done;
}
