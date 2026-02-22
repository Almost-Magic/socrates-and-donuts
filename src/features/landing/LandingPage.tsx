import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const stagger = {
  animate: {
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-midnight-900">
      {/* Section 1: THE HOOK */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 py-20">
        <motion.div
          initial="initial"
          animate="animate"
          variants={stagger}
          className="max-w-3xl text-center"
        >
          <motion.p variants={fadeIn} className="text-xl text-gray-400 mb-4">
            It's 11pm.
          </motion.p>
          <motion.p variants={fadeIn} className="text-3xl md:text-5xl font-light text-gray-200 mb-6">
            You're about to send that email.<br />
            <span className="text-gold">You know you shouldn't.</span><br />
            But you're going to anyway.
          </motion.p>
          <motion.p variants={fadeIn} className="text-xl text-gray-400 mb-12">
            Unless.
          </motion.p>
          <motion.button
            variants={fadeIn}
            onClick={() => navigate('/mirror')}
            className="bg-gold hover:bg-gold-hover text-midnight-900 px-8 py-4 rounded-lg text-lg font-semibold transition-all shadow-lg shadow-gold/20"
          >
            Ask the Mirror
          </motion.button>
        </motion.div>
      </section>

      {/* Section 2: THE PROBLEM */}
      <section className="py-20 px-6 bg-midnight-800/30">
        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-2xl mx-auto"
        >
          <motion.h2 variants={fadeIn} className="text-3xl font-light text-gray-200 mb-8">
            You know the feeling.
          </motion.h2>
          <motion.div variants={fadeIn} className="space-y-6 text-gray-400 text-lg leading-relaxed">
            <p>Someone said something. Or did something. Or didn't do something.</p>
            <p>And now you're activated.</p>
            <p>Your chest is tight. Your jaw is clenched.</p>
            <p>You're composing the perfect response in your head.</p>
            <p>You know exactly what to say.</p>
            <p className="text-gray-500 italic mt-8">Here's the thing:</p>
          </motion.div>
          <motion.div variants={fadeIn} className="mt-8 space-y-4 text-gray-300 text-lg leading-relaxed">
            <p>When you're angry, your judgment lies to you.</p>
            <p>When you're sad, everything feels permanent.</p>
            <p>When you're afraid, every option looks dangerous.</p>
          </motion.div>
          <motion.p variants={fadeIn} className="mt-8 text-xl text-gold">
            You can't see clearly. And you know you can't see clearly.<br />
            But you're going to act anyway.
          </motion.p>
          <motion.p variants={fadeIn} className="mt-8 text-2xl font-light text-gray-200">
            That's the problem.
          </motion.p>
        </motion.div>
      </section>

      {/* Section 3: THE GUIDE */}
      <section className="py-20 px-6">
        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-2xl mx-auto text-center"
        >
          <motion.h2 variants={fadeIn} className="text-3xl font-light text-gray-200 mb-8">
            What if you could talk to someone first?
          </motion.h2>
          <motion.div variants={fadeIn} className="space-y-6 text-gray-400 text-lg leading-relaxed">
            <p>Not a therapist. Not a friend with opinions. Not the internet.</p>
            <p>Someone who would just... ask good questions.</p>
          </motion.div>
          <motion.div variants={fadeIn} className="mt-8 space-y-4 text-xl text-gold/80">
            <p>"Where do you feel this in your body?"</p>
            <p>"What would happen if you waited 24 hours?"</p>
            <p>"What are you actually afraid of?"</p>
          </motion.div>
          <motion.p variants={fadeIn} className="mt-8 text-gray-400 text-lg leading-relaxed">
            No advice. No judgment. Just questions.<br />
            The kind that make you see what you already know<br />
            but can't quite admit.
          </motion.p>
          <motion.p variants={fadeIn} className="mt-12 text-2xl font-light text-gray-200">
            That's Socrates & Donuts.<br />
            <span className="text-gold">A wise friend for difficult moments.</span>
          </motion.p>
        </motion.div>
      </section>

      {/* Section 4: HOW IT WORKS */}
      <section className="py-20 px-6 bg-midnight-800/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-light text-gray-200 text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: 'Step 1', title: 'Tell the mirror', desc: "Not a form. Not a quiz. Just talk." },
              { step: 'Step 2', title: 'Answer the questions', desc: "The mirror asks. You answer. The seeing happens in between." },
              { step: 'Step 3', title: 'Decide from clarity', desc: "Act, wait, or let go — but do it clearly." },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="bg-midnight-800 p-6 rounded-lg border border-midnight-700"
              >
                <div className="text-gold text-sm font-medium mb-2">{item.step}</div>
                <h3 className="text-xl text-gray-200 mb-3">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 5: THE TOOLS */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-light text-gray-200 text-center mb-12">The Tools</h2>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { icon: '🪞', name: 'The Mirror', desc: 'A wise conversation that starts with your body' },
              { icon: '🔐', name: 'The Vault', desc: 'Write the angry message. Lock it. Decide tomorrow.' },
              { icon: '🔥', name: 'Letter You\'ll Never Send', desc: 'Write it. Burn it. Watch it dissolve.' },
              { icon: '🌤️', name: 'Emotional Weather Map', desc: 'Your emotions as beautiful weather patterns' },
              { icon: '🧭', name: 'Body Compass', desc: 'Tap where you feel it. Your body knows first.' },
              { icon: '📔', name: 'Decision Journal', desc: 'Log it now. Review with fresh eyes later.' },
              { icon: '✍️', name: 'Message Rewriter', desc: 'Your angry email in Calm, Empathetic, and Assertive' },
              { icon: '📜', name: 'Wisdom Feed', desc: 'The anti-doomscroll. Curated wisdom, not outrage.' },
              { icon: '⚡', name: 'Quick Capture', desc: 'Catch the thought before it\'s gone.' },
              { icon: '🛡️', name: 'Crisis Support', desc: 'When things are serious, real help.' },
            ].map((tool, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="bg-midnight-800/50 p-4 rounded-lg border border-midnight-700 hover:border-gold/50 transition-colors"
              >
                <div className="text-2xl mb-2">{tool.icon}</div>
                <h3 className="text-gray-200 font-medium">{tool.name}</h3>
                <p className="text-gray-500 text-sm">{tool.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 6: FOR PRACTITIONERS */}
      <section className="py-20 px-6 bg-midnight-800/30">
        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-2xl mx-auto text-center"
        >
          <motion.h2 variants={fadeIn} className="text-3xl font-light text-gray-200 mb-6">
            For Practitioners
          </motion.h2>
          <motion.div variants={fadeIn} className="space-y-6 text-gray-400 text-lg leading-relaxed">
            <p>If you sit Vipassana, you know the mirror.</p>
            <p>You sit. You observe. You see.</p>
            <p>But what about the other 22 hours?</p>
          </motion.div>
          <motion.p variants={fadeIn} className="mt-6 text-gray-300">
            Socrates & Donuts extends the work of the cushion<br />
            into the rest of your day.
          </motion.p>
          <motion.p variants={fadeIn} className="mt-6 text-gray-400">
            Every insight traces to a sutta.<br />
            Every question comes from the teaching.<br />
            Nothing is invented.
          </motion.p>
          <motion.button
            variants={fadeIn}
            onClick={() => navigate('/mirror')}
            className="mt-8 text-gold hover:text-gold-hover transition-colors"
          >
            Enter the Practice Space →
          </motion.button>
        </motion.div>
      </section>

      {/* Section 7: WHY IT'S FREE */}
      <section className="py-20 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-light text-gray-200 mb-8">Why It's Free</h2>
          <div className="space-y-6 text-gray-400 text-lg leading-relaxed">
            <p>In the Buddhist tradition, the Dhamma is given freely. Always has been.</p>
            <div className="flex justify-center gap-8 text-gray-300">
              <span>No ads</span>
              <span>•</span>
              <span>No premium tier</span>
              <span>•</span>
              <span>No data collection</span>
            </div>
            <p>Your conversations stay on your device.</p>
            <p>The code is open source.</p>
            <p>Wisdom belongs to everyone.</p>
            <p className="text-gold mt-8">This is dana — the practice of generosity.</p>
          </div>
        </div>
      </section>

      {/* Section 8: SAFETY DISCLAIMER */}
      <section className="py-16 px-6 bg-midnight-800/30">
        <div className="max-w-2xl mx-auto">
          <div className="border border-red-500/30 rounded-lg p-6 bg-red-900/10">
            <h3 className="text-red-400 font-semibold mb-4">IMPORTANT</h3>
            <p className="text-gray-400 mb-4">
              Socrates & Donuts is not a therapist, crisis service, or replacement for professional help.
            </p>
            <p className="text-gray-300 font-medium mb-4">If you are experiencing thoughts of self-harm or a mental health emergency:</p>
            <div className="grid sm:grid-cols-2 gap-4 text-sm">
              <div className="bg-red-900/20 rounded p-3">
                <div className="text-red-300">Lifeline Australia</div>
                <div className="text-gray-300">13 11 14</div>
              </div>
              <div className="bg-red-900/20 rounded p-3">
                <div className="text-red-300">988 Suicide & Crisis Lifeline (US)</div>
                <div className="text-gray-300">988</div>
              </div>
              <div className="bg-red-900/20 rounded p-3">
                <div className="text-red-300">Crisis Text Line</div>
                <div className="text-gray-300">Text HOME to 741741</div>
              </div>
              <div className="bg-red-900/20 rounded p-3">
                <div className="text-red-300">International</div>
                <div className="text-gray-300">findahelpline.com</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 9: FOOTER */}
      <footer className="py-12 px-6 border-t border-midnight-700">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-light text-gray-200 mb-4">
            Socrates & Donuts
          </h2>
          <p className="text-gray-400 mb-4">A wise friend for difficult moments.</p>
          <p className="text-gray-500 text-sm mb-6">
            Open source. Privacy first. Free forever.<br />
            Built by Almost Magic Tech Lab
          </p>
          <p className="text-gold/60 text-sm italic">
            Sabbē sattā sukhī hontu — May all beings be happy.
          </p>
        </div>
      </footer>
    </div>
  );
}
