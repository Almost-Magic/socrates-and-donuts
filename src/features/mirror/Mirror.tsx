import { useState, useEffect } from 'react';
import CrisisBanner from '../../components/CrisisBanner';
import BreathingDonut from '../../components/BreathingDonut';
import { detectCrisis } from '../../lib/crisisDetection';
import { 
  startSession, 
  submitResponse, 
  submitFeedback, 
  saveInsight,
  getSettings 
} from '../../lib/api';
import { useSettingsStore } from '../../stores/settingsStore';

type Feedback = 'yes' | 'not_sure' | 'not_today';

interface Contradiction {
  type: string;
  observation: string;
  prompt: string;
}

export default function Mirror() {
  const { intensity } = useSettingsStore();
  
  const [step, setStep] = useState<'flow-select' | 'question' | 'silence' | 'response' | 'complete'>('flow-select');
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [userInput, setUserInput] = useState('');
  const [history, setHistory] = useState<Array<{ question: string; answer: string }>>([]);
  const [isCrisis, setIsCrisis] = useState(false);
  
  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInSilence, setIsInSilence] = useState(false);
  const [silenceDurationSeconds, setSilenceDurationSeconds] = useState(30);
  
  // Contradiction & Feedback
  const [contradictions, setContradictions] = useState<Contradiction[]>([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<Feedback | null>(null);

  // Load settings on mount
  useEffect(() => {
    getSettings().then(settings => {
      if (settings.silence_duration) {
        setSilenceDurationSeconds(settings.silence_duration);
      }
    }).catch(console.error);
  }, []);

  const handleFlowSelect = async (flowId: string) => {
    setSelectedFlow(flowId);
    setStep('question');
    setHistory([]);
    setUserInput('');
    setIsCrisis(false);
    setShowFeedback(false);
    setFeedbackGiven(null);
    setContradictions([]);
    
    // Generate a question based on flow
    const question = getQuestionForFlow(flowId, 0);
    setCurrentQuestion(question);
    
    // Start session on backend
    try {
      const session = await startSession(flowId, question, intensity);
      setSessionId(session.session_id);
      setSilenceDurationSeconds(session.silence_duration_seconds || 30);
    } catch (err) {
      console.error('Failed to start session:', err);
    }
  };

  const handleSubmit = async () => {
    if (!userInput.trim()) return;

    // Check for crisis
    if (detectCrisis(userInput)) {
      setIsCrisis(true);
      setUserInput('');
      return;
    }

    // Add to history
    setHistory([...history, { question: currentQuestion, answer: userInput }]);
    
    // Submit to backend and check for contradictions
    if (sessionId) {
      try {
        const response = await submitResponse(sessionId, userInput);
        if (response.contradictions && response.contradictions.length > 0) {
          setContradictions(response.contradictions);
        }
      } catch (err) {
        console.error('Failed to submit response:', err);
      }
    }

    // Start forced silence
    setStep('silence');
    setIsInSilence(true);
    setUserInput('');
  };

  const handleSilenceComplete = () => {
    setIsInSilence(false);
    setStep('response');
    
    // Move to next question
    const nextStep = history.length + 1;
    const nextQuestion = getQuestionForFlow(selectedFlow!, nextStep);
    
    if (nextQuestion) {
      setCurrentQuestion(nextQuestion);
    } else {
      setShowFeedback(true);
    }
  };

  const handleFeedback = async (feedback: Feedback) => {
    if (sessionId) {
      try {
        await submitFeedback(sessionId, feedback);
        setFeedbackGiven(feedback);
      } catch (err) {
        console.error('Failed to submit feedback:', err);
      }
    }
    
    // Show completion after feedback
    setTimeout(() => {
      setStep('complete');
    }, 1000);
  };

  const handleSaveInsight = async () => {
    const title = `Reflection: ${selectedFlow}`;
    const content = history.map(h => `Q: ${h.question}\nA: ${h.answer}`).join('\n\n');
    
    try {
      await saveInsight(title, content, [selectedFlow!]);
      alert('Saved to your vault.');
    } catch (err) {
      console.error('Failed to save insight:', err);
    }
  };

  const handleReset = () => {
    setStep('flow-select');
    setSelectedFlow(null);
    setSessionId(null);
    setHistory([]);
    setUserInput('');
    setIsCrisis(false);
    setShowFeedback(false);
    setFeedbackGiven(null);
    setContradictions([]);
  };

  const flowOptions = [
    { id: 'decision', label: "I need to make a decision", emoji: '⚖️' },
    { id: 'anger', label: "I'm angry and about to do something", emoji: '😤' },
    { id: 'hurt', label: "I'm hurt and want to say something", emoji: '💔' },
    { id: 'grief', label: "I'm sad and thinking of a big change", emoji: '😢' },
    { id: 'anxiety', label: "I'm anxious and stuck in my head", emoji: '😰' },
    { id: 'general', label: "Something else is bothering me", emoji: '🤔' },
  ];

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <BreathingDonut 
        isActive={isInSilence} 
        durationSeconds={silenceDurationSeconds}
        onComplete={handleSilenceComplete}
      />

      {isCrisis && <CrisisBanner />}

      {step === 'flow-select' && (
        <div>
          <h1 className="text-3xl font-light text-gray-200 mb-4">The Mirror</h1>
          <p className="text-gray-400 mb-8">
            A quiet conversation that starts with your body. What's bringing you here today?
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
      )}

      {step === 'question' && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={handleReset}
              className="text-gray-400 hover:text-gray-200 transition-colors"
            >
              ← Start again
            </button>
          </div>

          {history.length > 0 && (
            <div className="mb-8 space-y-4">
              {history.map((item, i) => (
                <div key={i} className="space-y-2">
                  <div className="text-gold text-sm">→ {item.question}</div>
                  <div className="text-gray-300 pl-4 border-l-2 border-midnight-700 font-serif">
                    {item.answer}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mb-6">
            <div className="text-gold text-sm mb-2">Current question</div>
            <div className="text-xl text-gray-200 font-serif">{currentQuestion}</div>
          </div>

          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Take your time..."
            className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors resize-none font-sans"
            rows={4}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleSubmit();
              }
            }}
            autoFocus
          />

          <button
            onClick={handleSubmit}
            disabled={!userInput.trim()}
            className="mt-4 w-full bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue (Cmd+Enter)
          </button>
        </div>
      )}

      {step === 'response' && (
        <div>
          <div className="mb-8">
            <div className="text-gold text-sm mb-2">What arose</div>
            <div className="text-gray-300 font-serif text-lg">
              {history[history.length - 1]?.answer}
            </div>
          </div>

          {/* Contradiction display */}
          {contradictions.length > 0 && (
            <div className="mb-8 p-4 bg-midnight-800 rounded-lg border border-gold/30">
              <div className="text-gold/80 text-sm mb-2">Something noticed, if it's useful:</div>
              {contradictions.map((c, i) => (
                <div key={i} className="text-gray-400 text-sm">
                  {c.observation}
                </div>
              ))}
            </div>
          )}

          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="What else wants to be said?"
            className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors resize-none font-sans"
            rows={4}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleSubmit();
              }
            }}
            autoFocus
          />

          <button
            onClick={handleSubmit}
            disabled={!userInput.trim()}
            className="mt-4 w-full bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue (Cmd+Enter)
          </button>
        </div>
      )}

      {showFeedback && !feedbackGiven && (
        <div className="fixed inset-0 bg-midnight-900/95 flex items-center justify-center z-40">
          <div className="text-center max-w-md px-6">
            <h2 className="text-2xl font-light text-gray-200 mb-8">
              Did that land?
            </h2>
            <div className="space-y-3">
              <button
                onClick={() => handleFeedback('yes')}
                className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg hover:border-gold/50 transition-colors text-gray-200"
              >
                Yes
              </button>
              <button
                onClick={() => handleFeedback('not_sure')}
                className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg hover:border-gold/50 transition-colors text-gray-200"
              >
                Not sure
              </button>
              <button
                onClick={() => handleFeedback('not_today')}
                className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg hover:border-gold/50 transition-colors text-gray-200"
              >
                Not today
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 'complete' && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🪞</div>
          <h2 className="text-2xl font-light text-gray-200 mb-4">
            You've come to the end of this reflection.
          </h2>
          <p className="text-gray-400 mb-8">
            What you see now is yours to carry forward.
          </p>
          
          {history.length > 0 && (
            <button
              onClick={handleSaveInsight}
              className="mb-4 w-full bg-midnight-800 border border-midnight-700 text-gray-200 px-6 py-3 rounded-lg hover:border-gold/50 transition-colors"
            >
              Save to vault
            </button>
          )}
          
          <button
            onClick={handleReset}
            className="bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors"
          >
            Start a new reflection
          </button>
        </div>
      )}
    </div>
  );
}

function getQuestionForFlow(flow: string, step: number): string {
  const questions: Record<string, string[]> = {
    decision: [
      "What's the decision you're facing?",
      "What feels true about each option?",
      "What are you most afraid of?",
      "What would you tell a friend in this situation?",
      "What's the simplest version of this choice?",
    ],
    anger: [
      "What's happening that's making you angry?",
      "What need isn't being met?",
      "What would you want to happen?",
      "Who's really on your mind right now?",
      "What would make you feel heard?",
    ],
    hurt: [
      "What's happened that's left you hurt?",
      "What did you need that didn't happen?",
      "What are you most upset about?",
      "What would you like to say to them?",
      "What do you need right now?",
    ],
    grief: [
      "What's changing or what's been lost?",
      "What does this loss mean to you?",
      "What are you most sad about?",
      "What do you miss the most?",
      "What do you need to let go of?",
    ],
    anxiety: [
      "What's been on your mind?",
      "What's the worst case you're imagining?",
      "What's one thing you can actually control?",
      "What would calm you right now?",
      "What have you gotten through before?",
    ],
    general: [
      "What's been weighing on you?",
      "What's really going on underneath?",
      "What emotion is closest to the surface?",
      "What do you keep avoiding?",
      "What would you say if no one was judging?",
    ],
  };
  
  const flowQuestions = questions[flow] || questions.general;
  return step < flowQuestions.length ? flowQuestions[step] : '';
}
