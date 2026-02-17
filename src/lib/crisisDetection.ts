const CRISIS_KEYWORDS = [
  'kill myself',
  'suicide',
  'suicidal',
  'end my life',
  'want to die',
  'no reason to live',
  'better off dead',
  'self-harm',
  'cut myself',
  'overdose',
  'jump off',
  'hang myself',
  'not worth living',
  'hurt myself',
  'kill me',
];

const CRISIS_RESOURCES = [
  { name: 'Lifeline Australia', contact: '13 11 14', type: 'phone', region: 'Australia' },
  { name: '988 Suicide & Crisis Lifeline (US)', contact: '988', type: 'phone', region: 'United States' },
  { name: 'Crisis Text Line', contact: 'Text HOME to 741741', type: 'text', region: 'United States' },
  { name: 'International Directory', contact: 'findahelpline.com', type: 'web', region: 'International' },
  { name: 'Samaritans', contact: '116 123', type: 'phone', region: 'UK' },
  { name: 'Befrienders Worldwide', contact: 'befrienders.org', type: 'web', region: 'International' },
];

export function detectCrisis(text: string): boolean {
  const lower = text.toLowerCase();
  // Remove common false positives like "I almost killed time" or "I'm dying laughing"
  const cleaned = lower
    .replace(/i('m| am|ight|ight've|'ve)? almost/gi, '')
    .replace(/dying (of|laughing|from)/gi, '')
    .replace(/kill(ing|ed)? (time|bugs|mosquitoes)/gi, '');

  return CRISIS_KEYWORDS.some(keyword => cleaned.includes(keyword));
}

export { CRISIS_RESOURCES };
