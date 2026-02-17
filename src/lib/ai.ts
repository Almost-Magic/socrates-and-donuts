export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AIProvider {
  chat(messages: Message[], systemPrompt: string): Promise<string>;
}

const SYSTEM_PROMPT = `You are the mirror in Socrates & Donuts — a wise friend for difficult moments.

You are not a guru, not a therapist, not an authority. You are a mirror.

RULES:
1. QUESTIONS BEFORE ANSWERS — Ask 2-3 questions before any reflection. Never give advice.
2. SENSATION-FIRST — Always begin with the body: "Where do you feel this right now?"
3. THREE ROOTS — Look for: craving (lobha), aversion (dosa), delusion (moha).
4. WAIT WISDOM — Encourage patience. Suggest the Vault for reactive messages.
5. BLIND SPOT DETECTION — Surface: rationalisation disguised as wisdom, avoidance disguised as patience, people-pleasing disguised as compassion.
6. CRISIS CIRCUIT BREAKER — If language suggests self-harm: STOP mirroring. Go directive. Surface resources immediately.

TONE:
- Warm but not effusive
- Direct but gentle
- Patient, never rushing
- "You might consider" not "you should"
- End significant exchanges with a reflection question

THE PURPOSE: The person should feel "I see something I couldn't see before." Not "I got good advice."`;

class ClaudeProvider implements AIProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(messages: Message[], systemPrompt: string): Promise<string> {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        system: systemPrompt,
        messages: messages.map(m => ({
          role: m.role === 'assistant' ? 'assistant' : 'user',
          content: m.content,
        })),
      }),
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.content[0].text;
  }
}

class OpenAIProvider implements AIProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(messages: Message[], systemPrompt: string): Promise<string> {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [{ role: 'system', content: systemPrompt }, ...messages],
        max_tokens: 1024,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }
}

class StaticFlowProvider implements AIProvider {
  async chat(_messages: Message[], _systemPrompt: string): Promise<string> {
    throw new Error('Use StaticFlows module for non-AI conversations');
  }
}

export function createAIProvider(type: 'claude' | 'openai' | 'static', apiKey?: string, _flowType?: string): AIProvider {
  if (type === 'static') {
    return new StaticFlowProvider();
  }
  if (type === 'claude' && apiKey) {
    return new ClaudeProvider(apiKey);
  }
  if (type === 'openai' && apiKey) {
    return new OpenAIProvider(apiKey);
  }
  throw new Error('Invalid AI provider configuration');
}

export { SYSTEM_PROMPT, ClaudeProvider, OpenAIProvider, StaticFlowProvider };
