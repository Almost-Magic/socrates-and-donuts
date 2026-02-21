import { useState, useEffect } from 'react';
import { getSettings, saveSettings, testAIConnection } from '../../lib/api';
import { useSettingsStore } from '../../stores/settingsStore';

type Intensity = 'gentle' | 'reflective' | 'deep' | 'confronting';

const INTENSITY_OPTIONS: { value: Intensity; label: string; description: string }[] = [
  { value: 'gentle', label: 'Gentle', description: 'Soft questions, plenty of space' },
  { value: 'reflective', label: 'Reflective', description: 'A balanced conversation' },
  { value: 'deep', label: 'Deep', description: 'Going beneath the surface' },
  { value: 'confronting', label: 'Confronting', description: 'Direct questions that challenge' },
];

const DOMAIN_OPTIONS = [
  { id: 'work', label: 'Work & Career' },
  { id: 'relationships', label: 'Relationships' },
  { id: 'body', label: 'Body & Health' },
  { id: 'belief', label: 'Beliefs & Values' },
  { id: 'money', label: 'Money & Life' },
  { id: 'grief', label: 'Loss & Grief' },
  { id: 'creativity', label: 'Creativity' },
];

const LLM_PROVIDERS = [
  { id: 'none', label: 'No AI (Socratic only)' },
  { id: 'ollama', label: 'Ollama (local)' },
  { id: 'anthropic', label: 'Anthropic (Claude)' },
  { id: 'openai', label: 'OpenAI' },
  { id: 'deepseek', label: 'DeepSeek' },
  { id: 'custom', label: 'Custom endpoint' },
];

export default function Settings() {
  const store = useSettingsStore();
  
  const [intensity, setIntensity] = useState<Intensity>(store.intensity);
  const [domainsEnabled, setDomainsEnabled] = useState<string[]>(store.domainsEnabled);
  const [silenceDuration, setSilenceDuration] = useState(store.silenceDuration);
  const [llmProvider, setLlmProvider] = useState(store.llmProvider);
  const [llmApiKey, setLlmApiKey] = useState(store.llmApiKey);
  const [llmEndpoint, setLlmEndpoint] = useState(store.llmEndpoint);
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [isTestingAI, setIsTestingAI] = useState(false);
  const [aiTestResult, setAiTestResult] = useState<{ connected: boolean; error?: string } | null>(null);

  // Load settings on mount
  useEffect(() => {
    getSettings()
      .then(settings => {
        if (settings.intensity) setIntensity(settings.intensity as Intensity);
        if (settings.domains_enabled) setDomainsEnabled(settings.domains_enabled);
        if (settings.silence_duration) setSilenceDuration(settings.silence_duration);
        if (settings.llm_provider) setLlmProvider(settings.llm_provider as typeof store.llmProvider);
        
        // Update store
        store.loadFromBackend({
          intensity: settings.intensity as Intensity,
          domainsEnabled: settings.domains_enabled,
          silenceDuration: settings.silence_duration,
          llmProvider: settings.llm_provider as typeof store.llmProvider,
        });
      })
      .catch(console.error);
  }, []);

  const handleDomainToggle = (domainId: string) => {
    if (domainsEnabled.includes(domainId)) {
      setDomainsEnabled(domainsEnabled.filter(d => d !== domainId));
    } else {
      setDomainsEnabled([...domainsEnabled, domainId]);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage('');
    
    try {
      await saveSettings({
        intensity,
        domains_enabled: domainsEnabled,
        silence_duration: silenceDuration,
        llm_provider: llmProvider,
        llm_api_key: llmApiKey,
        llm_endpoint: llmEndpoint,
      });
      
      // Update local store
      store.setIntensity(intensity);
      store.setDomainsEnabled(domainsEnabled);
      store.setSilenceDuration(silenceDuration);
      store.setLLMProvider(llmProvider);
      store.setLLMApiKey(llmApiKey);
      store.setLLMEndpoint(llmEndpoint);
      
      setSaveMessage('Settings saved.');
    } catch (err) {
      setSaveMessage('Failed to save settings.');
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  const handleTestAI = async () => {
    setIsTestingAI(true);
    setAiTestResult(null);
    
    try {
      const result = await testAIConnection(llmProvider, llmApiKey, llmEndpoint);
      setAiTestResult(result);
    } catch (err) {
      setAiTestResult({ connected: false, error: 'Connection failed' });
    } finally {
      setIsTestingAI(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-light text-gray-200 mb-8">Settings</h1>
      
      {/* Intensity Dial */}
      <section className="mb-10">
        <h2 className="text-xl text-gray-200 mb-4">How deep shall we go?</h2>
        <p className="text-gray-400 mb-6 text-sm">
          This determines the tone of the questions. You can change this anytime.
        </p>
        
        <div className="space-y-3">
          {INTENSITY_OPTIONS.map((option) => (
            <label
              key={option.value}
              className={`flex items-start p-4 rounded-lg border cursor-pointer transition-colors ${
                intensity === option.value
                  ? 'bg-midnight-800 border-gold'
                  : 'bg-midnight-800/50 border-midnight-700 hover:border-gold/50'
              }`}
            >
              <input
                type="radio"
                name="intensity"
                value={option.value}
                checked={intensity === option.value}
                onChange={(e) => setIntensity(e.target.value as Intensity)}
                className="mt-1 mr-3"
              />
              <div>
                <div className="text-gray-200 font-medium">{option.label}</div>
                <div className="text-gray-500 text-sm">{option.description}</div>
              </div>
            </label>
          ))}
        </div>
      </section>

      {/* Domain Toggles */}
      <section className="mb-10">
        <h2 className="text-xl text-gray-200 mb-4">Topics you'd like to explore</h2>
        <p className="text-gray-400 mb-6 text-sm">
          Select the areas you want questions to draw from. Leave some unchecked to narrow the focus.
        </p>
        
        <div className="grid grid-cols-2 gap-3">
          {DOMAIN_OPTIONS.map((domain) => (
            <label
              key={domain.id}
              className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
                domainsEnabled.includes(domain.id)
                  ? 'bg-midnight-800 border-gold/50'
                  : 'bg-midnight-800/30 border-midnight-700'
              }`}
            >
              <input
                type="checkbox"
                checked={domainsEnabled.includes(domain.id)}
                onChange={() => handleDomainToggle(domain.id)}
                className="mr-3"
              />
              <span className="text-gray-300">{domain.label}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Silence Duration */}
      <section className="mb-10">
        <h2 className="text-xl text-gray-200 mb-4">Silence between questions</h2>
        <p className="text-gray-400 mb-4 text-sm">
          After you answer, there's a moment of quiet before the next question appears.
        </p>
        
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="10"
            max="120"
            step="10"
            value={silenceDuration}
            onChange={(e) => setSilenceDuration(Number(e.target.value))}
            className="flex-1"
          />
          <span className="text-gold w-20 text-center">{silenceDuration}s</span>
        </div>
      </section>

      {/* LLM Settings */}
      <section className="mb-10">
        <h2 className="text-xl text-gray-200 mb-4">AI companion (optional)</h2>
        <p className="text-gray-400 mb-6 text-sm">
          Socrates & Donuts works without AI — just you and the questions. Add an AI if you'd like reflections mirrored back to you.
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-gray-400 text-sm mb-2">Provider</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value as typeof store.llmProvider)}
              className="w-full p-3 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200"
            >
              {LLM_PROVIDERS.map((p) => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
          </div>
          
          {llmProvider !== 'none' && (
            <>
              <div>
                <label className="block text-gray-400 text-sm mb-2">API Key</label>
                <input
                  type="password"
                  value={llmApiKey}
                  onChange={(e) => setLlmApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full p-3 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-600"
                />
              </div>
              
              {llmProvider === 'custom' && (
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Endpoint</label>
                  <input
                    type="text"
                    value={llmEndpoint}
                    onChange={(e) => setLlmEndpoint(e.target.value)}
                    placeholder="https://api.example.com/v1/chat"
                    className="w-full p-3 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-600"
                  />
                </div>
              )}
              
              <button
                onClick={handleTestAI}
                disabled={isTestingAI}
                className="px-4 py-2 bg-midnight-700 text-gray-300 rounded-lg hover:bg-midnight-600 transition-colors disabled:opacity-50"
              >
                {isTestingAI ? 'Testing...' : 'Test connection'}
              </button>
              
              {aiTestResult && (
                <div className={`p-3 rounded-lg ${aiTestResult.connected ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                  {aiTestResult.connected ? 'Connected successfully.' : aiTestResult.error || 'Connection failed.'}
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* Save Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="bg-gold text-midnight-900 px-8 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save settings'}
        </button>
        {saveMessage && (
          <span className="text-gray-400">{saveMessage}</span>
        )}
      </div>
    </div>
  );
}
