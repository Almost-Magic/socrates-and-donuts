import { AlertTriangle } from 'lucide-react';

const CRISIS_RESOURCES = [
  { name: 'Lifeline Australia', contact: '13 11 14', type: 'phone' },
  { name: '988 Suicide & Crisis Lifeline (US)', contact: '988', type: 'phone' },
  { name: 'Crisis Text Line', contact: 'Text HOME to 741741', type: 'text' },
  { name: 'International Directory', contact: 'findahelpline.com', type: 'web' },
];

export default function CrisisBanner() {
  return (
    <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="text-red-500 shrink-0 mt-0.5" size={24} />
        <div>
          <h3 className="font-semibold text-red-400 mb-2">I'm concerned about what you've shared</h3>
          <p className="text-sm text-gray-300 mb-3">
            If you're experiencing thoughts of self-harm or a mental health emergency, please reach out to someone who can help right now.
          </p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {CRISIS_RESOURCES.map((resource) => (
              <div key={resource.name} className="bg-red-900/30 rounded p-2">
                <div className="text-red-300 font-medium">{resource.name}</div>
                <div className="text-gray-300">{resource.contact}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
