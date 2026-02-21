// Socrates & Donuts API Service
// Supports both Flask backend (localhost) and localStorage (GitHub Pages)

const isGitHubPages = typeof window !== 'undefined' && 
  window.location.hostname.includes('github.io');

const API_BASE = isGitHubPages ? '' : 'http://localhost:5010/api';

// localStorage keys
const STORAGE_KEYS = {
  settings: 'snd_settings',
  insights: 'snd_insights',
  letters: 'snd_letters',
  sessions: 'snd_sessions',
};

interface HealthResponse {
  status: string;
  app: string;
  version: string;
  port: number;
  vault_entries: number;
  llm_connected: boolean;
  llm_provider: string;
  questions_in_bank: number;
  active_arc: unknown;
}

interface Question {
  id: string;
  question: string;
  framework: string;
  domain: string;
  intensity: string;
  tags: string[];
}

interface Session {
  session_id: string;
  started_at: string;
  framework: string;
  status: string;
  silence_duration_seconds?: number;
}

interface SessionResponse {
  session_id: string;
  response?: string;
  type: string;
  contradictions?: Array<{
    type: string;
    observation: string;
    prompt: string;
  }>;
  resources?: unknown;
}

interface VaultInsight {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
}

interface VaultLetter {
  id: string;
  title: string;
  content?: string;
  opens_at?: string;
  created_at: string;
}

interface Settings {
  intensity?: string;
  domains_enabled?: string[];
  theme?: string;
  silence_duration?: number;
  notifications_enabled?: boolean;
  llm_provider?: string;
  llm_api_key?: string;
  llm_endpoint?: string;
}

// Default questions for offline mode
const DEFAULT_QUESTIONS: Question[] = [
  { id: '1', question: "What's been weighing on you?", framework: 'socratic', domain: 'general', intensity: 'reflective', tags: [] },
  { id: '2', question: "What feels true about this situation?", framework: 'socratic', domain: 'belief', intensity: 'reflective', tags: [] },
  { id: '3', question: "What are you most afraid of?", framework: 'socratic', domain: 'grief', intensity: 'deep', tags: [] },
  { id: '4', question: "What would you tell a friend in this situation?", framework: 'socratic', domain: 'relationships', intensity: 'gentle', tags: [] },
  { id: '5', question: "What's the simplest version of this choice?", framework: 'socratic', domain: 'work', intensity: 'reflective', tags: [] },
];

// Helper for fetch
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}

// localStorage helpers
function getFromStorage<T>(key: string, defaultValue: T): T {
  try {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : defaultValue;
  } catch {
    return defaultValue;
  }
}

function saveToStorage<T>(key: string, data: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (e) {
    console.error('Failed to save to localStorage:', e);
  }
}

// Health check
export async function getHealth(): Promise<HealthResponse> {
  if (isGitHubPages) {
    return {
      status: 'healthy',
      app: 'Socrates & Donuts',
      version: '1.0.0',
      port: 0,
      vault_entries: getFromStorage(STORAGE_KEYS.insights, []).length + getFromStorage(STORAGE_KEYS.letters, []).length,
      llm_connected: false,
      llm_provider: 'none',
      questions_in_bank: DEFAULT_QUESTIONS.length,
      active_arc: null,
    };
  }
  return apiFetch<HealthResponse>('/health');
}

// Questions
export async function getTodayQuestion(intensity?: string, domain?: string): Promise<Question> {
  if (isGitHubPages) {
    let questions = DEFAULT_QUESTIONS;
    if (intensity) {
      questions = questions.filter(q => q.intensity === intensity);
    }
    if (domain) {
      questions = questions.filter(q => q.domain === domain);
    }
    return questions[Math.floor(Math.random() * questions.length)] || DEFAULT_QUESTIONS[0];
  }
  const params = new URLSearchParams();
  if (intensity) params.set('intensity', intensity);
  if (domain) params.set('domain', domain);
  const query = params.toString();
  return apiFetch<Question>(`/question/today${query ? `?${query}` : ''}`);
}

export async function getRandomQuestion(intensity?: string, domain?: string): Promise<Question> {
  if (isGitHubPages) {
    return getTodayQuestion(intensity, domain);
  }
  const params = new URLSearchParams();
  if (intensity) params.set('intensity', intensity);
  if (domain) params.set('domain', domain);
  const query = params.toString();
  return apiFetch<Question>(`/question/random${query ? `?${query}` : ''}`);
}

// Sessions (mock for offline)
export async function startSession(questionId: string, questionText: string, intensity: string): Promise<Session> {
  if (isGitHubPages) {
    const session: Session = {
      session_id: crypto.randomUUID(),
      started_at: new Date().toISOString(),
      framework: 'socratic',
      status: 'active',
      silence_duration_seconds: 30,
    };
    const sessions = getFromStorage<Session[]>(STORAGE_KEYS.sessions, []);
    sessions.push(session);
    saveToStorage(STORAGE_KEYS.sessions, sessions);
    return session;
  }
  return apiFetch<Session>('/session/start', {
    method: 'POST',
    body: JSON.stringify({
      question_id: questionId,
      question_text: questionText,
      intensity,
    }),
  });
}

export async function submitResponse(sessionId: string, content: string, framework?: string): Promise<SessionResponse> {
  if (isGitHubPages) {
    return {
      session_id: sessionId,
      type: 'reflection',
      response: 'A moment of silence before the next question...',
      contradictions: [],
    };
  }
  return apiFetch<SessionResponse>(`/session/${sessionId}/respond`, {
    method: 'POST',
    body: JSON.stringify({
      content,
      framework: framework || 'socratic',
    }),
  });
}

export async function submitFeedback(sessionId: string, feedback: 'yes' | 'not_sure' | 'not_today'): Promise<{ status: string; feedback_id: string }> {
  if (isGitHubPages) {
    return { status: 'saved', feedback_id: crypto.randomUUID() };
  }
  return apiFetch(`/session/${sessionId}/feedback`, {
    method: 'POST',
    body: JSON.stringify({ feedback }),
  });
}

// Settings
export async function getSettings(): Promise<Settings> {
  if (isGitHubPages) {
    return getFromStorage<Settings>(STORAGE_KEYS.settings, {
      intensity: 'reflective',
      domains_enabled: ['work', 'relationships', 'body', 'belief', 'money', 'grief', 'creativity'],
      theme: 'dark',
      silence_duration: 30,
      notifications_enabled: false,
      llm_provider: 'none',
    });
  }
  return apiFetch<Settings>('/settings');
}

export async function saveSettings(settings: Settings): Promise<{ status: string }> {
  if (isGitHubPages) {
    saveToStorage(STORAGE_KEYS.settings, settings);
    return { status: 'saved' };
  }
  return apiFetch('/settings', {
    method: 'POST',
    body: JSON.stringify(settings),
  });
}

// Vault - Insights
export async function getInsights(): Promise<VaultInsight[]> {
  if (isGitHubPages) {
    return getFromStorage<VaultInsight[]>(STORAGE_KEYS.insights, []);
  }
  return apiFetch<VaultInsight[]>('/vault/insights');
}

export async function saveInsight(title: string, content: string, tags: string[] = []): Promise<{ id: string; status: string }> {
  if (isGitHubPages) {
    const insights = getFromStorage<VaultInsight[]>(STORAGE_KEYS.insights, []);
    const newInsight: VaultInsight = {
      id: crypto.randomUUID(),
      title,
      content,
      tags,
      created_at: new Date().toISOString(),
    };
    insights.unshift(newInsight);
    saveToStorage(STORAGE_KEYS.insights, insights);
    return { id: newInsight.id, status: 'saved' };
  }
  return apiFetch('/vault/insights', {
    method: 'POST',
    body: JSON.stringify({ title, content, tags }),
  });
}

// Vault - Letters
export async function getLetters(): Promise<VaultLetter[]> {
  if (isGitHubPages) {
    return getFromStorage<VaultLetter[]>(STORAGE_KEYS.letters, []);
  }
  return apiFetch<VaultLetter[]>('/vault/letters');
}

export async function saveLetter(type: 'unsent' | 'oneyear', title: string, content: string, tags: string[] = []): Promise<{ id: string; opens_at?: string }> {
  if (isGitHubPages) {
    const letters = getFromStorage<VaultLetter[]>(STORAGE_KEYS.letters, []);
    const opensAt = type === 'oneyear' 
      ? new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString()
      : new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
    
    const newLetter: VaultLetter = {
      id: crypto.randomUUID(),
      title,
      content,
      opens_at: opensAt,
      created_at: new Date().toISOString(),
    };
    letters.unshift(newLetter);
    saveToStorage(STORAGE_KEYS.letters, letters);
    return { id: newLetter.id, opens_at: opensAt };
  }
  return apiFetch('/vault/letters', {
    method: 'POST',
    body: JSON.stringify({ type, title, content, tags }),
  });
}

export async function getLetter(letterId: string): Promise<VaultLetter & { locked?: boolean; message?: string }> {
  if (isGitHubPages) {
    const letters = getFromStorage<VaultLetter[]>(STORAGE_KEYS.letters, []);
    const letter = letters.find(l => l.id === letterId);
    if (!letter) {
      return { id: letterId, title: '', created_at: '', locked: false, message: 'Letter not found' };
    }
    const isLocked = !!(letter.opens_at && new Date(letter.opens_at) > new Date());
    return { ...letter, locked: isLocked };
  }
  return apiFetch<VaultLetter & { locked?: boolean; message?: string }>(`/vault/letters/${letterId}`);
}

// Export/Import
export async function exportVault(): Promise<unknown> {
  if (isGitHubPages) {
    return {
      insights: getFromStorage(STORAGE_KEYS.insights, []),
      letters: getFromStorage(STORAGE_KEYS.letters, []),
      settings: getFromStorage(STORAGE_KEYS.settings, {}),
      exported_at: new Date().toISOString(),
    };
  }
  return apiFetch('/vault/export');
}

export async function importVault(data: unknown): Promise<{ status: string; message: string }> {
  if (isGitHubPages) {
    try {
      const { insights, letters, settings } = data as { insights?: VaultInsight[]; letters?: VaultLetter[]; settings?: Settings };
      if (insights) saveToStorage(STORAGE_KEYS.insights, insights);
      if (letters) saveToStorage(STORAGE_KEYS.letters, letters);
      if (settings) saveToStorage(STORAGE_KEYS.settings, settings);
      return { status: 'success', message: 'Data imported successfully' };
    } catch {
      return { status: 'error', message: 'Failed to import data' };
    }
  }
  return apiFetch('/vault/import', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// AI
export async function testAIConnection(provider: string, apiKey?: string, endpoint?: string): Promise<{ connected: boolean; provider: string; error?: string }> {
  if (isGitHubPages || provider === 'none') {
    return { connected: false, provider, error: 'AI not available in offline mode' };
  }
  return apiFetch('/ai/test-connection', {
    method: 'POST',
    body: JSON.stringify({ provider, api_key: apiKey, endpoint }),
  });
}

// Export mode detection for debugging
export const isOfflineMode = isGitHubPages;
