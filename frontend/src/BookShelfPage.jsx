import { useState } from 'react';
import { ChevronLeft, ChevronRight, BookOpen, Clock, Type, Hash } from 'lucide-react';

export default function BookshelfPage() {
    const mockBooks = [
        {
          id: 1,
          title: "Quantum Mechanics: A Modern Introduction",
          category: "Quantum Physics",
          createdAt: "2024-03-15",
          readingTime: 8,
          wordCount: 1200,
          characterCount: 6800,
          coverColor: "bg-indigo-500",
          summary: "An introduction to the fundamental principles of quantum mechanics, including wave-particle duality, superposition, and quantum entanglement."
        },
        {
          id: 2,
          title: "String Theory Fundamentals",
          category: "Theoretical Physics",
          createdAt: "2024-03-14",
          readingTime: 6,
          wordCount: 950,
          characterCount: 5200,
          coverColor: "bg-emerald-500",
          summary: "Exploring the basics of string theory and its implications for understanding the universe at its most fundamental level."
        },
        {
          id: 3,
          title: "Introduction to Dark Matter",
          category: "Astrophysics",
          createdAt: "2024-03-13",
          readingTime: 7,
          wordCount: 1050,
          characterCount: 5900,
          coverColor: "bg-purple-500",
          summary: "Understanding the mysterious dark matter, its effects on galaxy formation, and current detection methods."
        },
        {
          id: 4,
          title: "The Physics of Black Holes",
          category: "Astrophysics",
          createdAt: "2024-03-12",
          readingTime: 9,
          wordCount: 1350,
          characterCount: 7400,
          coverColor: "bg-blue-500",
          summary: "Diving into the physics of black holes, from their formation to their effects on spacetime and quantum mechanics."
        },
        {
          id: 5,
          title: "Particle Physics Explained",
          category: "Particle Physics",
          createdAt: "2024-03-11",
          readingTime: 5,
          wordCount: 800,
          characterCount: 4500,
          coverColor: "bg-rose-500",
          summary: "An overview of fundamental particles, their interactions, and the Standard Model of particle physics."
        },
        {
          id: 6,
          title: "Advanced Relativity Concepts",
          category: "Relativity",
          createdAt: "2024-03-10",
          readingTime: 8,
          wordCount: 1150,
          characterCount: 6300,
          coverColor: "bg-amber-500",
          summary: "Exploring advanced concepts in special and general relativity, including spacetime curvature and gravitational waves."
        },
        {
          id: 7,
          title: "Plasma Physics and Applications",
          category: "Plasma Physics",
          createdAt: "2024-03-09",
          readingTime: 6,
          wordCount: 900,
          characterCount: 5100,
          coverColor: "bg-teal-500",
          summary: "Understanding plasma behavior and its applications in fusion energy, space physics, and industrial processes."
        },
        {
          id: 8,
          title: "Cosmology: From Big Bang to Now",
          category: "Cosmology",
          createdAt: "2024-03-08",
          readingTime: 7,
          wordCount: 1100,
          characterCount: 6100,
          coverColor: "bg-cyan-500",
          summary: "A journey through the history of our universe, from the Big Bang to the present day, exploring major cosmological concepts."
        }
      ];

  const [books] = useState(mockBooks);
  const [startIndex, setStartIndex] = useState(0);
  const [selectedBook, setSelectedBook] = useState(null);
  const booksPerPage = 4; // Changed from 4 to 3 to accommodate larger cards

  const handlePrevious = () => {
    setStartIndex(prev => Math.max(0, prev - 1));
  };

  const handleNext = () => {
    setStartIndex(prev => Math.min(books.length - booksPerPage, prev + 1));
  };

  const handleBookClick = (book) => {
    setSelectedBook(book === selectedBook ? null : book);
  };

  return (
    <div className="h-screen overflow-y-auto">
<div className="max-w-[70%] mx-auto p-12">
        <div className="mb-12">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">My Knowledge Archive</h1>
            <div className="flex justify-center gap-6 mt-6">
              <div className="px-6 py-2.5 bg-orange-100 text-orange-600 rounded-full text-lg font-medium">
                {books.length} Papers Available
              </div>
              <div className="px-6 py-2.5 bg-purple-100 text-purple-600 rounded-full text-lg font-medium">
                Quick Reads (&lt;10 min)
              </div>
            </div>
          </div>
        </div>

        <div className="relative mb-16">
          <div className="absolute -top-6 left-0 w-full h-px bg-gradient-to-r from-transparent via-orange-200 to-transparent"></div>
          
          <div className="flex items-center justify-center mb-10">
            <button
              onClick={handlePrevious}
              disabled={startIndex === 0}
              className={`p-3 rounded-full mr-6 ${
                startIndex === 0 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : 'text-orange-500 hover:bg-orange-100'
              }`}
            >
              <ChevronLeft size={32} />
            </button>

            <div className="flex space-x-8 overflow-hidden">
              {books.slice(startIndex, startIndex + booksPerPage).map((book) => (
                <div
                  key={book.id}
                  onClick={() => handleBookClick(book)}
                  className="w-64 cursor-pointer"
                >
                  <div className={`relative h-80 ${book.coverColor} rounded-xl shadow-lg p-6 flex flex-col transition-all duration-300 hover:brightness-110 hover:shadow-xl group`}>
                    <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-black/20 to-transparent rounded-t-xl transition-opacity duration-300 group-hover:opacity-30"></div>
                    <BookOpen className="text-white/80 w-12 h-12 mb-3 relative z-10 transition-colors duration-300 group-hover:text-white" />
                    <h3 className="text-white font-bold text-lg mb-2 line-clamp-2 relative z-10 transition-colors duration-300 group-hover:text-white">{book.title}</h3>
                    <div className="mt-auto space-y-3 relative z-10">
                      <span className="inline-block bg-white/20 rounded-full px-4 py-1.5 text-sm text-white transition-colors duration-300 group-hover:bg-white/30">
                        {book.category}
                      </span>
                      <div className="flex items-center text-white/80 text-sm transition-colors duration-300 group-hover:text-white">
                        <Clock className="w-4 h-4 mr-2" />
                        {book.readingTime} min read
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-3 text-center">
                    Created: {new Date(book.createdAt).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>

            <button
              onClick={handleNext}
              disabled={startIndex >= books.length - booksPerPage}
              className={`p-3 rounded-full ml-6 ${
                startIndex >= books.length - booksPerPage
                  ? 'text-gray-400 cursor-not-allowed' 
                  : 'text-orange-500 hover:bg-orange-100'
              }`}
            >
              <ChevronRight size={32} />
            </button>
          </div>

          {selectedBook && (
            <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200 transform transition-all duration-300 ease-in-out">
              <div className="flex items-start justify-between">
                <div className="space-y-6">
                  <h2 className="text-3xl font-bold text-gray-900">{selectedBook.title}</h2>
                  <div className="flex items-center space-x-8">
                    <div className="flex items-center text-gray-600">
                      <Clock className="w-6 h-6 mr-2" />
                      <span className="text-lg">{selectedBook.readingTime} min read</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Type className="w-6 h-6 mr-2" />
                      <span className="text-lg">{selectedBook.wordCount.toLocaleString()} words</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Hash className="w-6 h-6 mr-2" />
                      <span className="text-lg">{selectedBook.characterCount.toLocaleString()} characters</span>
                    </div>
                  </div>
                  <p className="text-gray-600 text-lg">{selectedBook.summary}</p>
                  <div className="pt-3">
                    <button className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors duration-200 text-lg">
                      Read Paper
                    </button>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedBook(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Scrollable List Section */}
        <div className="mt-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">All Papers</h2>
          <div className="border rounded-xl overflow-hidden">
            <div className="bg-gray-50 px-8 py-4 sticky top-0 z-20">
              <div className="grid grid-cols-12 gap-6 text-xl font-medium text-gray-500">
                <div className="col-span-4">Title & Summary</div>
                <div className="col-span-2">Category</div>
                <div className="col-span-2">Created</div>
                <div className="col-span-4">Details</div>
              </div>
            </div>
            <div>
              {books.map((book) => (
                <div key={book.id} 
                  className="px-8 py-6 border-t hover:bg-gray-50 transition-colors duration-150"
                >
                  <div className="grid grid-cols-12 gap-6">
                    <div className="col-span-4">
                      <h3 className="font-medium text-gray-900 text-xl mb-2">{book.title}</h3>
                      <p className="text-base text-gray-600 line-clamp-2">{book.summary}</p>
                    </div>
                    <div className="col-span-2">
                      <span className={`inline-block px-4 py-1.5 rounded-full text-lg font-medium ${book.coverColor.replace('bg-', 'bg-opacity-20 text-')}`}>
                        {book.category}
                      </span>
                    </div>
                    <div className="col-span-2 text-lg text-gray-600">
                      {new Date(book.createdAt).toLocaleDateString()}
                    </div>
                    <div className="col-span-4">
                      <div className="flex items-center space-x-6 text-lg text-gray-600">
                        <div className="flex items-center">
                          <Clock className="w-5 h-5 mr-2" />
                          {book.readingTime}m
                        </div>
                        <div className="flex items-center">
                          <Type className="w-5 h-5 mr-2" />
                          {book.wordCount}
                        </div>
                        <div className="flex items-center">
                          <Hash className="w-5 h-5 mr-2" />
                          {book.characterCount}
                        </div>
                        <button 
                          onClick={() => handleBookClick(book)}
                          className="px-4 py-1.5 bg-orange-100 text-orange-600 rounded-full text-md font-medium hover:bg-orange-200 transition-colors duration-150"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}