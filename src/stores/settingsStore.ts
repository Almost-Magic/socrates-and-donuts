import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Settings {
  theme: 'dark' | 'light';
  aiProvider: 'none' | 'claude' | 'openai';
  apiKey?: string;
  hasCompletedOnboarding: boolean;
}

interface SettingsStore extends Settings {
  setTheme: (theme: 'dark' | 'light') => void;
  setAIProvider: (provider: 'none' | 'claude' | 'openai') => void;
  setAPIKey: (key: string) => void;
  completeOnboarding: () => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      theme: 'dark',
      aiProvider: 'none',
      hasCompletedOnboarding: false,
      setTheme: (theme) => set({ theme }),
      setAIProvider: (aiProvider) => set({ aiProvider }),
      setAPIKey: (apiKey) => set({ apiKey }),
      completeOnboarding: () => set({ hasCompletedOnboarding: true }),
    }),
    {
      name: 'snd-settings',
    }
  )
);
