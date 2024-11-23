import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import 'katex/dist/katex.min.css'; // Import KaTeX CSS
import 'highlight.js/styles/github.css';
import { Toolbar, HIGHLIGHT_COLORS } from './MarkdownToolbar';
import { useContextMenu } from './MarkdownContextMenu';
import html2pdf from 'html2pdf.js';

const MarkdownViewer = ({ markdownContent }) => {
  const [zoom, setZoom] = useState(100);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isHighlightMode, setIsHighlightMode] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [highlightColor, setHighlightColor] = useState(HIGHLIGHT_COLORS[0].class);
  const contentRef = useRef(null);
  const { contextMenu, handleContextMenu, ContextMenuComponent } = useContextMenu();
  
  // Calculate stats
  const wordCount = markdownContent.trim().split(/\s+/).length;
  const charCount = markdownContent.length;
  const readingTimeMinutes = Math.ceil(wordCount / 200); // Assuming average reading speed of 200 wpm
  const estimatedPages = Math.ceil(markdownContent.length / 3000); // Rough estimation

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 10, 200));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 10, 50));
  
  const handlePrint = () => {
    window.print();
  };
  
  const handleSaveAsPDF = async () => {
    if (contentRef.current) {
      const element = contentRef.current;
  
      // Wait for all images to load before rendering
      const images = element.querySelectorAll('img');
      const imagePromises = Array.from(images).map(img =>
        new Promise((resolve) => {
          if (img.complete) {
            resolve();
          } else {
            img.onload = resolve;
            img.onerror = resolve; // In case the image fails to load
          }
        })
      );
  
      // Ensure all images are loaded
      await Promise.all(imagePromises);
  
      const options = {
        margin: 0.5,
        filename: 'preview.pdf',
        html2canvas: { 
          scale: 2, 
          useCORS: true, 
          logging: true, 
          windowWidth: 1080 // Simulates a larger viewport width if necessary
        },
        jsPDF: { unit: 'in', format: 'A4', orientation: 'portrait' }
      };
      
  
      html2pdf().set(options).from(element).save();
    } else {
      alert('No content to save.');
    }
  };

  // Highlighting functionality
  useEffect(() => {
    const handleSelection = () => {
      if (!isHighlightMode) return;
      
      const selection = window.getSelection();
      const selectedText = selection.toString().trim();
      
      if (!selectedText) return;

      // Check if the selection is within our content area
      let container = selection.getRangeAt(0).commonAncestorContainer;
      while (container && container !== contentRef.current) {
        container = container.parentNode;
      }
      if (!container) return;

      // Create highlight span
      const range = selection.getRangeAt(0);
      const span = document.createElement('span');
      span.className = highlightColor;
      
      try {
        range.surroundContents(span);
      } catch (e) {
        console.warn('Could not highlight complex selection');
      }
      
      selection.removeAllRanges();
    };

    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && isHighlightMode) {
        handleSelection();
      }
    };

    const handleMouseUp = () => {
      if (isHighlightMode) {
        setTimeout(handleSelection, 10); // Small delay to ensure selection is complete
      }
    };

    document.addEventListener('keypress', handleKeyPress);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('keypress', handleKeyPress);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isHighlightMode, highlightColor]);

  return (
    <div className="flex-1 flex flex-col h-full bg-gray-100">
      <Toolbar 
        zoom={zoom}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        isDarkMode={isDarkMode}
        onThemeToggle={() => setIsDarkMode(!isDarkMode)}
        isHighlightMode={isHighlightMode}
        onHighlightToggle={() => setIsHighlightMode(!isHighlightMode)}
        highlightColor={highlightColor}
        onColorChange={setHighlightColor}
        currentPage={currentPage}
        estimatedPages={estimatedPages}
        onPageChange={setCurrentPage}
        onPrint={handlePrint}
        onSavePDF={handleSaveAsPDF}
      />

      {/* Context Menu */}
      {ContextMenuComponent}
      
      {/* Content Area */}
      <div 
        className="flex-1 overflow-auto p-4"
        onContextMenu={handleContextMenu}
      >
        <div 
          ref={contentRef}
          className={`max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-md prose prose-lg ${
            isDarkMode ? 'dark:bg-gray-800 dark:prose-invert' : ''
          }`}
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'top center',
            transition: 'transform 0.2s ease'
          }}
        >
          <ReactMarkdown
            children={markdownContent}
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[
              rehypeHighlight,
              [rehypeKatex, {
                strict: false,
                throwOnError: false,
                output: 'html'
              }],
              rehypeRaw
            ]}
          />
        </div>
      </div>

      {/* Bottom Status Bar */}
      <div className="bg-white border-t px-4 py-2 text-sm text-gray-600">
        <div className="flex justify-between items-center">
          <div className="flex space-x-6">
            <div>Reading time: {readingTimeMinutes} min</div>
            <div>Words: {wordCount.toLocaleString()}</div>
            <div>Characters: {charCount.toLocaleString()}</div>
          </div>
          <div>Zoom: {zoom}%</div>
        </div>
      </div>
    </div>
  );
};

export default MarkdownViewer;