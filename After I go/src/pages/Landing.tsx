import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()
  
  const features = [
    { title: 'Messages', desc: 'Letters to loved ones, delivered when the time comes', path: '/messages' },
    { title: 'Wishes', desc: 'Your preferences for care, ceremonies, and remembrance', path: '/wishes' },
    { title: 'Vault', desc: 'Important documents, passwords, and digital accounts', path: '/vault' },
    { title: 'Financial Map', desc: 'Assets, accounts, and instructions all in one place', path: '/financial' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-navy-600 text-white font-sans">
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <p className="text-xs tracking-[0.2em] opacity-60 uppercase mb-4">Almost Magic Tech Lab</p>
        
        <h1 className="text-5xl md:text-7xl font-light mb-6 leading-tight">
          After I Go
        </h1>
        
        <p className="text-xl opacity-85 mb-3 font-light">Your Digital Legacy, Protected</p>
        
        <p className="text-base opacity-60 mb-12 max-w-xl mx-auto leading-relaxed">
          A private vault that helps the right people find what they need after you're gone.{' '}
          Organise messages, wishes, finances, and digital accounts — all in your browser.
        </p>
        
        <button
          onClick={() => navigate('/setup')}
          className="px-10 py-4 text-lg bg-sage-500 text-white rounded-full font-medium 
                     tracking-wide hover:bg-sage-400 hover:scale-105 transition-all duration-200 mb-4"
        >
          Start Organising — Free Forever
        </button>
        
        <p className="text-sm opacity-50">No account needed. Works in your browser. Free forever.</p>
        
        <div className="mt-20 grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          {features.map((feature) => (
            <button
              key={feature.title}
              onClick={() => navigate(feature.path)}
              className="bg-white/5 rounded-2xl p-6 border border-white/10 text-left
                         hover:bg-white/10 hover:border-white/20 hover:scale-[1.02] 
                         transition-all duration-200 cursor-pointer w-full"
            >
              <h3 className="text-lg font-medium mb-2">{feature.title}</h3>
              <p className="text-sm opacity-60 leading-relaxed">{feature.desc}</p>
            </button>
          ))}
        </div>
        
        <p className="mt-20 text-xs opacity-30">
          Built with care in Australia by Almost Magic Tech Lab
        </p>
      </div>
    </div>
  )
}
