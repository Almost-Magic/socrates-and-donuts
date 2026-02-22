// Socrates & Donuts API Service
// Uses IndexedDB for offline storage (no backend required)

import { getDB, exportData, importData } from './database';

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
  { id: '6', question: "What do you need right now?", framework: 'socratic', domain: 'body', intensity: 'gentle', tags: [] },
  { id: '7', question: "What's the story you're telling yourself?", framework: 'socratic', domain: 'belief', intensity: 'deep', tags: [] },
  { id: '8', question: "What would happen if you waited?", framework: 'socratic', domain: 'general', intensity: 'reflective', tags: [] },
];

// Generate UUID
function generateId(): string {
  return crypto.randomUUID();
}

// Health check - always returns healthy for offline mode
export async function getHealth(): Promise<HealthResponse> {
  const db = await getDB();
  
  const vaultEntries = await db.count('vaultEntries');
  const letters = await db.count('letters');
  
  return {
    status: 'healthy',
    app: 'Socrates & Donuts',
    version: '1.0.0',
    port: 0,
    vault_entries: vaultEntries + letters,
    llm_connected: false,
    llm_provider: 'none',
    questions_in_bank: DEFAULT_QUESTIONS.length,
    active_arc: null,
  };
}

// Questions
export async function getTodayQuestion(_intensity?: string, _domain?: string): Promise<Question> {
  let questions = [...DEFAULT_QUESTIONS];
  
  // Note: In offline mode, we use all questions regardless of intensity/domain
  // The filtering would require updating DEFAULT_QUESTIONS with the full question bank
  
  // Use date as seed for "today's" question
  const today = new Date();
  const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
  const index = dayOfYear % questions.length;
  
  return questions[index] || DEFAULT_QUESTIONS[0];
}

export async function getRandomQuestion(intensity?: string, domain?: string): Promise<Question> {
  return getTodayQuestion(intensity, domain);
}

// Sessions - stored in IndexedDB conversations store
export async function startSession(questionId: string, questionText: string, _intensity: string): Promise<Session> {
  const db = await getDB();
  
  const session: Session = {
    session_id: generateId(),
    started_at: new Date().toISOString(),
    framework: 'socratic',
    status: 'active',
    silence_duration_seconds: 30,
  };
  
  // Store as a conversation
  await db.put('conversations', {
    id: session.session_id,
    messages: [{ role: 'assistant' as const, content: questionText, timestamp: Date.now() }],
    flowType: questionId,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  });
  
  return session;
}

export async function submitResponse(sessionId: string, content: string, _framework?: string): Promise<SessionResponse> {
  const db = await getDB();
  
  // Get existing conversation
  const conversation = await db.get('conversations', sessionId);
  
  if (conversation) {
    // Add user message
    conversation.messages.push({ role: 'user', content, timestamp: Date.now() });
    conversation.updatedAt = Date.now();
    await db.put('conversations', conversation);
  }
  
  // Generate a simple Socratic response based on the question
  const responses = [
    "A moment of silence before the next question...",
    "What arises when you consider this?",
    "There's wisdom in sitting with that.",
    "Let that settle for a moment.",
    "What do you notice now?",
  ];
  
  const response = responses[Math.floor(Math.random() * responses.length)];
  
  return {
    session_id: sessionId,
    type: 'reflection',
    response,
    contradictions: [],
  };
}

export async function submitFeedback(_sessionId: string, _feedback: 'yes' | 'not_sure' | 'not_today'): Promise<{ status: string; feedback_id: string }> {
  // In offline mode, we just acknowledge the feedback
  // The session is already stored in IndexedDB
  return { status: 'saved', feedback_id: generateId() };
}

// Settings - stored in IndexedDB
export async function getSettings(): Promise<Settings> {
  const db = await getDB();
  
  const settingsRecord = await db.get('settings', 'user-settings');
  
  if (settingsRecord) {
    return settingsRecord.value as Settings;
  }
  
  // Default settings
  return {
    intensity: 'reflective',
    domains_enabled: ['work', 'relationships', 'body', 'belief', 'money', 'grief', 'creativity'],
    theme: 'dark',
    silence_duration: 30,
    notifications_enabled: false,
    llm_provider: 'none',
  };
}

export async function saveSettings(settings: Settings): Promise<{ status: string }> {
  const db = await getDB();
  
  await db.put('settings', {
    key: 'user-settings',
    value: settings,
  });
  
  return { status: 'saved' };
}

// Vault - Insights stored in IndexedDB vaultEntries
export async function getInsights(): Promise<VaultInsight[]> {
  const db = await getDB();
  
  const entries = await db.getAll('vaultEntries');
  
  return entries.map(entry => ({
    id: entry.id,
    title: entry.content.substring(0, 50) || 'Reflection',
    content: entry.content,
    tags: [],
    created_at: new Date(entry.createdAt).toISOString(),
  }));
}

export async function saveInsight(title: string, content: string, _tags: string[] = []): Promise<{ id: string; status: string }> {
  const db = await getDB();
  
  const id = generateId();
  
  await db.put('vaultEntries', {
    id,
    content: `${title}\n\n${content}`,
    createdAt: Date.now(),
    unlocksAt: 0,
    status: 'unlocked',
  });
  
  return { id, status: 'saved' };
}

// Vault - Letters stored in IndexedDB letters store
export async function getLetters(): Promise<VaultLetter[]> {
  const db = await getDB();
  
  const letters = await db.getAll('letters');
  
  return letters.map(letter => ({
    id: letter.id,
    title: letter.content.substring(0, 30) || 'Letter',
    content: letter.content,
    opens_at: undefined,
    created_at: new Date(letter.createdAt).toISOString(),
  }));
}

export async function saveLetter(type: 'unsent' | 'oneyear', title: string, content: string, _tags: string[] = []): Promise<{ id: string; opens_at?: string }> {
  const db = await getDB();
  
  const id = generateId();
  const now = Date.now();
  
  let opensAt: number | undefined;
  if (type === 'oneyear') {
    opensAt = now + (365 * 24 * 60 * 60 * 1000); // 1 year from now
  }
  
  await db.put('letters', {
    id,
    content: `${title}\n\n${content}`,
    createdAt: now,
    burnedAt: undefined,
  });
  
  return { 
    id, 
    opens_at: opensAt ? new Date(opensAt).toISOString() : undefined 
  };
}

export async function getLetter(letterId: string): Promise<VaultLetter & { locked?: boolean; message?: string }> {
  const db = await getDB();
  
  const letter = await db.get('letters', letterId);
  
  if (!letter) {
    return { id: letterId, title: '', created_at: '', locked: false, message: 'Letter not found' };
  }
  
  const isLocked = false; // Letters are always readable in this version
  
  return {
    id: letter.id,
    title: letter.content.substring(0, 30),
    content: letter.content,
    created_at: new Date(letter.createdAt).toISOString(),
    locked: isLocked,
  };
}

// Export/Import - full vault backup
export async function exportVault(): Promise<unknown> {
  const jsonData = await exportData();
  return {
    exported_at: new Date().toISOString(),
    ...JSON.parse(jsonData),
  };
}

export async function importVault(data: unknown): Promise<{ status: string; message: string }> {
  try {
    const jsonData = JSON.stringify(data);
    await importData(jsonData);
    return { status: 'success', message: 'Data imported successfully' };
  } catch (e) {
    console.error('Import error:', e);
    return { status: 'error', message: 'Failed to import data' };
  }
}

// AI - not available in offline mode
export async function testAIConnection(provider: string, _apiKey?: string, _endpoint?: string): Promise<{ connected: boolean; provider: string; error?: string }> {
  if (provider === 'none') {
    return { connected: false, provider, error: 'No AI configured' };
  }
  return { connected: false, provider, error: 'AI not available in offline mode' };
}

// Export for debugging
export const isOfflineMode = true;
