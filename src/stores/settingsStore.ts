import { create } from 'zustand';

interface Settings {
  theme: 'dark' | 'light';
  intensity: 'gentle' | 'reflective' | 'deep' | 'confronting';
  domainsEnabled: string[];
  silenceDuration: number;
  notificationsEnabled: boolean;
  llmProvider: 'none' | 'ollama' | 'anthropic' | 'openai' | 'deepseek' | 'custom';
  llmApiKey: string;
  llmEndpoint: string;
  hasCompletedOnboarding: boolean;
}

interface SettingsStore extends Settings {
  setTheme: (theme: 'dark' | 'light') => void;
  setIntensity: (intensity: 'gentle' | 'reflective' | 'deep' | 'confronting') => void;
  setDomainsEnabled: (domains: string[]) => void;
  setSilenceDuration: (duration: number) => void;
  setNotificationsEnabled: (enabled: boolean) => void;
  setLLMProvider: (provider: 'none' | 'ollama' | 'anthropic' | 'openai' | 'deepseek' | 'custom') => void;
  setLLMApiKey: (key: string) => void;
  setLLMEndpoint: (endpoint: string) => void;
  completeOnboarding: () => void;
  loadFromBackend: (settings: Partial<Settings>) => void;
}

const DEFAULT_DOMAINS = ['work', 'relationships', 'body', 'belief', 'money', 'grief', 'creativity'];

export const useSettingsStore = create<SettingsStore>((set) => ({
  theme: 'dark',
  intensity: 'reflective',
  domainsEnabled: DEFAULT_DOMAINS,
  silenceDuration: 300,
  notificationsEnabled: false,
  llmProvider: 'none',
  llmApiKey: '',
  llmEndpoint: '',
  hasCompletedOnboarding: false,
  setTheme: (theme) => set({ theme }),
  setIntensity: (intensity) => set({ intensity }),
  setDomainsEnabled: (domainsEnabled) => set({ domainsEnabled }),
  setSilenceDuration: (silenceDuration) => set({ silenceDuration }),
  setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
  setLLMProvider: (llmProvider) => set({ llmProvider }),
  setLLMApiKey: (llmApiKey) => set({ llmApiKey }),
  setLLMEndpoint: (llmEndpoint) => set({ llmEndpoint }),
  completeOnboarding: () => set({ hasCompletedOnboarding: true }),
  loadFromBackend: (settings) => set((state) => ({
    ...state,
    ...settings,
    domainsEnabled: settings.domainsEnabled || state.domainsEnabled
  })),
}));
