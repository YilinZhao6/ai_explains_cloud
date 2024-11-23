import React, { useState, useEffect } from 'react';
import { PenTool, CheckCircle, Coffee, BookOpen, ChevronRight, Brain } from 'lucide-react';

const SectionWriterScreen = () => {
  const [currentSection, setCurrentSection] = useState(0);
  const [completedSections, setCompletedSections] = useState([]);
  const [generatingText, setGeneratingText] = useState('');
  const [showWriter, setShowWriter] = useState(false);
  const [outlineSections, setOutlineSections] = useState([]);

  // Fetch all sections from the generated outline
  useEffect(() => {
    const fetchOutline = () => {
      fetch('https://papuros-backend.onrender.com/check_outline')
        .then(response => response.json())
        .then(data => {
          if (data.exists && data.sections) {
            setOutlineSections(data.sections); // Set all fetched sections
          }
        });
    };

    fetchOutline();
  }, []);

  // Simulate section completion
  useEffect(() => {
    if (currentSection < outlineSections.length) {
      const timer = setTimeout(() => {
        setCompletedSections(prev => [...prev, currentSection]);
        setCurrentSection(prev => prev + 1);
      }, 6000); // Adjust the timing as needed
      return () => clearTimeout(timer);
    }
  }, [currentSection, outlineSections]);

  // Typing animation for current section status
  useEffect(() => {
    if (currentSection < outlineSections.length) {
      const text = `Writing... ${outlineSections[currentSection]?.section_title || ''}`;
      let currentIndex = 0;

      const typingInterval = setInterval(() => {
        if (currentIndex <= text.length) {
          setGeneratingText(text.slice(0, currentIndex));
          currentIndex++;
        }
      }, 50);

      return () => clearInterval(typingInterval);
    }
  }, [currentSection, outlineSections]);

  // Initial animation to show writer
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowWriter(true);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative bg-gradient-to-br from-orange-50 to-amber-50 w-full h-full min-h-screen flex items-center justify-center p-8">
      <div className="w-full max-w-3xl">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="text-center mb-4">
            <div className="flex items-center justify-center space-x-2">
              <Brain className="w-5 h-5 text-orange-600 animate-pulse" />
              <span className="text-orange-900 font-mono">
                {generatingText}<span className="animate-pulse">|</span>
              </span>
            </div>
          </div>
          <div className="flex items-center justify-center space-x-2 mt-4">
            <Coffee className="w-5 h-5 text-orange-500" />
            <p className="text-orange-700 text-sm">Writing sections with precision and clarity...</p>
          </div>
        </div>

        {/* Content Box - Generated Sections */}
        <div className="bg-white rounded-lg shadow-lg p-6 border border-orange-100">
          <div className="space-y-6">
            {outlineSections.length > 0 ? (
              outlineSections.map((section, index) => {
                const isCompleted = completedSections.includes(index);
                const isCurrent = currentSection === index;

                return (
                  <div 
                    key={index}
                    className={`transition-all duration-500 ${
                      isCompleted || isCurrent ? 'opacity-100' : 'opacity-50'
                    }`}
                  >
                    <div className="flex items-center space-x-2 text-orange-900 font-semibold mb-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        isCompleted ? 'bg-orange-500' : isCurrent ? 'bg-orange-400 animate-pulse' : 'bg-gray-200'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle className="w-4 h-4 text-white" />
                        ) : (
                          <BookOpen className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <h3 className="text-lg">{section.section_title}</h3>
                    </div>
                    <div className="ml-7 space-y-2">
                      {section.learning_goals?.map((goal, idx) => (
                        <div 
                          key={idx}
                          className={`flex items-start space-x-2 text-orange-600 transition-all duration-300 ${
                            isCompleted ? 'opacity-100' : isCurrent ? 'opacity-80' : 'opacity-50'
                          }`}
                        >
                          <ChevronRight className={`w-4 h-4 text-orange-400 mt-1 flex-shrink-0 ${
                            isCurrent ? 'animate-pulse' : ''
                          }`} />
                          <span className="text-sm">{goal}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SectionWriterScreen;
