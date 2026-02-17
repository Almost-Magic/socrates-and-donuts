import { useState } from 'react';

export default function DecisionJournal() {
  const [decisions] = useState<Array<{ id: string; question: string; createdAt: string; reviewDate: string }>>([]);

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Decision Journal</h1>
        <p className="text-gray-400 mt-1">Log it now. Review with fresh eyes later.</p>
      </div>

      <div className="mb-8 p-6 bg-midnight-800 border border-midnight-700 rounded-lg">
        <h2 className="text-gold text-sm font-medium mb-4">New Decision</h2>
        <input
          type="text"
          placeholder="What decision are you facing?"
          className="w-full p-3 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none mb-4"
        />
        <textarea
          placeholder="What's your reasoning? What are you afraid of? What do you hope for?"
          className="w-full p-3 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none resize-none mb-4"
          rows={4}
        />
        <div className="flex gap-3">
          <select className="p-3 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200">
            <option>Review in 1 week</option>
            <option>Review in 1 month</option>
            <option>Review in 3 months</option>
            <option>Review in 1 year</option>
          </select>
          <button className="flex-1 bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover">
            Save Decision
          </button>
        </div>
      </div>

      {decisions.length > 0 ? (
        <div className="space-y-4">
          {decisions.map((d) => (
            <div key={d.id} className="p-4 bg-midnight-800/50 border border-midnight-700 rounded-lg">
              <div className="text-gray-200 font-medium">{d.question}</div>
              <div className="text-gray-500 text-sm mt-1">Review: {d.reviewDate}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <p>No decisions logged yet.</p>
        </div>
      )}
    </div>
  );
}
