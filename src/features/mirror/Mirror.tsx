import { useState } from 'react';
import { detectCrisis } from '../../lib/crisisDetection';
import { getAllFlowTypes, getNextQuestion, type FlowType } from '../../lib/staticFlows';
import CrisisBanner from '../../components/CrisisBanner';

const flowOptions = [
  { id: 'decision' as FlowType, label: 'I need to make a decision', emoji: '⚖️' },
  { id: 'anger' as FlowType, label: "I'm angry and about to do something", emoji: '😤' },
  { id: 'hurt' as FlowType, label: "I'm hurt and want to say something", emoji: '💔' },
  { id: 'grief' as FlowType, label: "I'm sad and thinking of a big change", emoji: '😢' },
  { id: 'anxiety' as FlowType, label: "I'm anxious and stuck in my head", emoji: '😰' },
  { id: 'general' as FlowType, label: 'Something else is bothering me', emoji: '🤔' },
];

export default function Mirror() {
  const [selectedFlow, setSelectedFlow] = useState<FlowType | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [userInput, setUserInput] = useState('');
  const [history, setHistory] = useState<Array<{ question: string; answer: string }>>([]);
  const [isCrisis, setIsCrisis] = useState(false);

  const currentQuestion = selectedFlow ? getNextQuestion(selectedFlow, stepIndex) : null;

  const handleFlowSelect = (flowId: FlowType) => {
    setSelectedFlow(flowId);
    setStepIndex(0);
    setHistory([]);
    setUserInput('');
    setIsCrisis(false);
  };

  const handleSubmit = () => {
    if (!userInput.trim() || !selectedFlow) return;

    // Check for crisis
    if (detectCrisis(userInput)) {
      setIsCrisis(true);
      setUserInput('');
      return;
    }

    if (currentQuestion) {
      setHistory([...history, { question: currentQuestion, answer: userInput }]);
      setUserInput('');
      setStepIndex(stepIndex + 1);
    }
  };

  const handleReset = () => {
    setSelectedFlow(null);
    setStepIndex(0);
    setHistory([]);
    setUserInput('');
    setIsCrisis(false);
  };

  const isComplete = selectedFlow && currentQuestion === null;

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      {isCrisis && <CrisisBanner />}

      {!selectedFlow ? (
        <div>
          <h1 className="text-3xl font-light text-gray-200 mb-4">The Mirror</h1>
          <p className="text-gray-400 mb-8">
            A wise conversation that starts with your body. Choose what's bringing you here today.
          </p>
          <div className="space-y-3">
            {flowOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => handleFlowSelect(option.id)}
                className="w-full text-left p-4 bg-midnight-800 border border-midnight-700 rounded-lg hover:border-gold/50 transition-colors"
              >
                <span className="text-2xl mr-3">{option.emoji}</span>
                <span className="text-gray-200">{option.label}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={handleReset}
              className="text-gray-400 hover:text-gray-200 transition-colors"
            >
              ← Back to choices
            </button>
            {selectedFlow && (
              <span className="text-gold text-sm">
                {stepIndex} / {getAllFlowTypes().reduce((acc, t) => acc + (t === selectedFlow ? 20 : 0), 0)} steps
              </span>
            )}
          </div>

          {isComplete ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">🪞</div>
              <h2 className="text-2xl font-light text-gray-200 mb-4">
                You've come to the end of this reflection.
              </h2>
              <p className="text-gray-400 mb-8">
                What you see now is yours to carry forward.
              </p>
              <div className="space-x-4">
                <button
                  onClick={handleReset}
                  className="bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors"
                >
                  Start a new reflection
                </button>
              </div>
            </div>
          ) : (
            <>
              {history.length > 0 && (
                <div className="mb-8 space-y-4">
                  {history.map((item, i) => (
                    <div key={i} className="space-y-2">
                      <div className="text-gold text-sm">→ {item.question}</div>
                      <div className="text-gray-300 pl-4 border-l-2 border-midnight-700">
                        {item.answer}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="mb-6">
                <div className="text-gold text-sm mb-2">Current question</div>
                <div className="text-xl text-gray-200">{currentQuestion}</div>
              </div>

              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Your answer..."
                className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors resize-none"
                rows={4}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    handleSubmit();
                  }
                }}
              />

              <button
                onClick={handleSubmit}
                disabled={!userInput.trim()}
                className="mt-4 w-full bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue (Cmd+Enter)
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
