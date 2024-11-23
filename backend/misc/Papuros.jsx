import React, { useState, useEffect } from 'react';
import { ScrollArea } from '@radix-ui/react-scroll-area';
import ProjectSidebar from './components/ProjectSidebar';
import {
  ChevronRight, ChevronDown, FolderPlus, Menu,
  History, Star, User, Home, BookmarkPlus,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';  // GitHub flavored markdown
import rehypeHighlight from 'rehype-highlight'; // Syntax highlighting
import rehypeMathjax from 'rehype-mathjax'; // Math rendering with MathJax
import rehypeRaw from 'rehype-raw'; // For raw HTML parsing
import 'highlight.js/styles/github.css'; // Import CSS for code highlighting

// Helper function to parse "##" headers from markdown
const parseMarkdownHeaders = (markdownContent) => {
  const lines = markdownContent.split(/\r?\n/);
  const topics = [];

  lines.forEach((line, index) => {
    const match = line.match(/^##\s+(.*)$/);
    if (match) {
      topics.push({ id: index + 1, title: match[1], sections: [] });
    }
  });

  return topics;
};

const Button = (props) => <button {...props} className={`p-2 rounded ${props.className}`} />;
const Input = (props) => <input {...props} className={`p-2 border rounded ${props.className}`} />;

const LeftNavigationBar = () => (
  <div className="w-16 bg-gray-800 flex flex-col items-center py-4 space-y-4">
    <div className="text-2xl font-bold text-white">P</div>
    <Button className="text-gray-300 hover:text-white">
      <Home className="h-6 w-6" />
    </Button>
    <Button className="text-gray-300 hover:text-white">
      <History className="h-6 w-6" />
    </Button>
    <Button className="text-gray-300 hover:text-white">
      <Star className="h-6 w-6" />
    </Button>
    <div className="flex-grow" />
    <Button className="text-gray-300 hover:text-white">
      <User className="h-6 w-6" />
    </Button>
  </div>
);

const SecondaryNavigation = ({ isNavOpen, topics, searchQuery, setSearchQuery }) => (
  <div className={`w-72 bg-white border-r border-gray-200 flex flex-col ${isNavOpen ? '' : 'hidden'}`}>
    <div className="p-4 border-b">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-bold text-lg">Projects</h2>
        <Button>
          <FolderPlus className="h-4 w-4" />
        </Button>
      </div>
      <Input
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search in project..."
        className="w-full"
      />
    </div>
    <ScrollArea className="flex-grow overflow-auto">
      {topics.length > 0 ? (
        <ProjectSidebar 
          topics={topics}
          onSelectTopic={(topicId) => console.log(`Navigating to topic ${topicId}`)}
        />
      ) : (
        <div className="p-4 text-gray-500">No topics found in the document.</div>
      )}
    </ScrollArea>
  </div>
);

const MainContent = ({ handleTextSelection, markdownContent }) => (
  <div className="flex-1 flex flex-col">
    <div className="h-16 border-b bg-white flex items-center px-6 justify-between">
      <Button className="text-gray-600">
        <Menu className="h-6 w-6" />
      </Button>
      <h1 className="text-xl font-bold text-gray-800">Papuros</h1>
      <Button className="text-gray-600">
        <BookmarkPlus className="h-5 w-5" />
      </Button>
    </div>

    <div className="flex-1 overflow-auto p-4 bg-gray-100">
      <div 
        className="max-w-full mx-auto p-6 bg-white rounded shadow prose prose-lg math"
        onMouseUp={handleTextSelection}
      >
        {/* Render Markdown with raw HTML support */}
        <ReactMarkdown 
          children={markdownContent}
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight, rehypeMathjax, rehypeRaw]} // Add rehypeRaw here
          components={{
            ul({ node, ...props }) {
              return <ul className="key-points" {...props} />;
            }
          }}
        />
      </div>
    </div>

    <div className="border-t bg-white p-4">
      <div className="max-w-3xl mx-auto">
        <Input
          placeholder="What would you like to learn about?"
          className="w-full"
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              console.log('New search:', e.target.value);
            }
          }}
        />
      </div>
    </div>
  </div>
);

const Papuros = () => {
  const [isNavOpen, setIsNavOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [topics, setTopics] = useState([]);
  const [markdownContent, setMarkdownContent] = useState('');

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString()) {
      console.log('Selected text:', selection.toString());
    }
  };

  useEffect(() => {
    fetch('article.md') // Ensure the path to article.md is correct
      .then((response) => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.text();
      })
      .then((text) => {
        setMarkdownContent(text);
        setTopics(parseMarkdownHeaders(text));
      })
      .catch((error) => console.error('Error loading Markdown file:', error));
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      <LeftNavigationBar />
      <SecondaryNavigation 
        isNavOpen={isNavOpen} 
        topics={topics}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />
      <MainContent handleTextSelection={handleTextSelection} markdownContent={markdownContent} />
    </div>
  );
};

export default Papuros;
