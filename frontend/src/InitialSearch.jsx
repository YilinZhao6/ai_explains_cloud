import React, { useState } from 'react';
import { ArrowUpCircle } from 'lucide-react'; // Using an upward arrow icon

const EnhancedSearch = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    if (query.trim() !== '') {
      onSearch(query);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-[var(--bg-color)] space-y-8">
      {/* Main Title */}
      <h1 className="text-5xl font-bold text-gray-800 mb-8">
      Nothing in life is to be feared, it is only to be understood.
      </h1>

      {/* Search Box */}
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-full p-6 flex items-center border border-gray-300">
        <input
          type="text"
          className="flex-grow p-4 text-2xl focus:outline-none text-gray-700 placeholder-gray-400 rounded-full"
          placeholder="Ask anything..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') handleSearch();
          }}
        />
        <button
          className="p-3 bg-orange-500 text-white rounded-full ml-4 hover:bg-green-500 transition duration-300"
          onClick={handleSearch}
        >
          <ArrowUpCircle className="h-8 w-8" />
        </button>
      </div>

      {/* Suggestions */}
      <div className="grid grid-cols-2 gap-6 mt-8 max-w-2xl">
        <button className="flex items-center bg-white border border-gray-300 rounded-lg p-4 hover:shadow-lg transition duration-300">
          <span role="img" aria-label="car" className="mr-2 text-2xl">🚗</span>
          <span className="text-xl text-gray-600">Tell me about Quantum Entanglement</span>
        </button>
        <button className="flex items-center bg-white border border-gray-300 rounded-lg p-4 hover:shadow-lg transition duration-300">
          <span role="img" aria-label="cookbook" className="mr-2 text-2xl">📚</span>
          <span className="text-xl text-gray-600">What are Moore Diagrams</span>
        </button>
        <button className="flex items-center bg-white border border-gray-300 rounded-lg p-4 hover:shadow-lg transition duration-300">
          <span role="img" aria-label="espresso" className="mr-2 text-2xl">☕</span>
          <span className="text-xl text-gray-600">I want to learn more about Orbital Motion</span>
        </button>
        <button className="flex items-center bg-white border border-gray-300 rounded-lg p-4 hover:shadow-lg transition duration-300">
          <span role="img" aria-label="brain" className="mr-2 text-2xl">🧠</span>
          <span className="text-xl text-gray-600">I feel so brainy today!</span>
        </button>
      </div>
    </div>
  );
};

export default EnhancedSearch;