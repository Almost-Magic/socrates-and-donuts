import { useEffect, useState } from 'react';
import { X, Keyboard } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface HelpContent {
  title: string;
  quickActions: string[];
  howItWorks: string[];
  tips: string[];
  shortcuts?: Record<string, string>;
}

interface ContextHelpProps {
  content: HelpContent;
}

export default function ContextHelp({ content }: ContextHelpProps) {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '?' && !isOpen) {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 hover:bg-midnight-700 rounded-lg transition-colors"
        aria-label="Open help"
      >
        <Keyboard size={20} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-midnight-800 border-l border-midnight-700 z-50 overflow-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gold">{content.title}</h2>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 hover:bg-midnight-700 rounded-lg transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <h3 className="font-medium text-gray-300 mb-2">Quick Actions</h3>
                    <ul className="list-disc list-inside text-gray-400 space-y-1">
                      {content.quickActions.map((action, i) => (
                        <li key={i}>{action}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-medium text-gray-300 mb-2">How It Works</h3>
                    <p className="text-gray-400">{content.howItWorks.join(' ')}</p>
                  </div>

                  <div>
                    <h3 className="font-medium text-gray-300 mb-2">Tips</h3>
                    <ul className="list-disc list-inside text-gray-400 space-y-1">
                      {content.tips.map((tip, i) => (
                        <li key={i}>{tip}</li>
                      ))}
                    </ul>
                  </div>

                  {content.shortcuts && (
                    <div>
                      <h3 className="font-medium text-gray-300 mb-2">Keyboard Shortcuts</h3>
                      <div className="space-y-1 text-sm">
                        {Object.entries(content.shortcuts).map(([key, action]) => (
                          <div key={key} className="flex justify-between">
                            <kbd className="px-2 py-1 bg-midnight-700 rounded text-gray-300">{key}</kbd>
                            <span className="text-gray-400">{action}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
