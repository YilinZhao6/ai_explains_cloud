import React, { useState, useEffect } from 'react';
import InitialSearch from './InitialSearch';
import LoadingAnimation from './LoadingAnimation';
import MarkdownViewer from './MarkdownViewer';
import LeftNavigationBar from './LeftNavigationBar';
import ConceptExplanationProvider from './ConceptExplanation';
import UserProfilePage from './UserProfilePage'; // Adjusted import path

const Papuros = () => {
  const [view, setView] = useState('initial'); // 'initial', 'loading', 'markdown', 'userProfile'
  const [markdownContent, setMarkdownContent] = useState('');
  const [loadingMessages, setLoadingMessages] = useState([]); 
  const [imageLoading, setImageLoading] = useState(false);

  const handleSearch = (query) => {
    console.log('Search query:', query);

    // Save the query and start generation process
    fetch(`http://localhost:5000/save_query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    }).then(() => {
      setView('loading');
      setLoadingMessages([]);

      const eventSource = new EventSource(`http://localhost:5000/generate?query=${encodeURIComponent(query)}`);

      eventSource.onmessage = (event) => {
        const message = event.data;
        setLoadingMessages((prevMessages) => [...prevMessages, message]);

        if (message.includes('Text generation complete')) {
          eventSource.close();

          fetch('http://localhost:5000/article')
            .then((response) => response.ok ? response.text() : Promise.reject('Error loading article'))
            .then((text) => {
              setMarkdownContent(text);
              setView('markdown');
              setImageLoading(true);
              checkForUpdatedArticle();
            })
            .catch(console.error);
        } else if (message.includes('Image generation started')) {
          setImageLoading(true);
        }
      };

      eventSource.onerror = (err) => {
        console.error('EventSource failed:', err);
        eventSource.close();
      };
    }).catch(console.error);
  };

  const checkForUpdatedArticle = () => {
    fetch('http://localhost:5000/updated_article')
      .then(response => response.status === 200 ? response.text() : setTimeout(checkForUpdatedArticle, 3000))
      .then(updatedContent => {
        if (updatedContent) {
          setMarkdownContent(updatedContent);
          setImageLoading(false);
        }
      })
      .catch(console.error);
  };

  const handleHomeClick = () => {
    setView('initial');
  };

  const handleProfileClick = () => {
    setView('userProfile');
  };

  return (
    <ConceptExplanationProvider>
      <div className="flex h-screen bg-gray-50">
        <LeftNavigationBar onHomeClick={handleHomeClick} onProfileClick={handleProfileClick} />
        <div className="flex-1">
          {view === 'initial' && <InitialSearch onSearch={handleSearch} />}
          {view === 'loading' && <LoadingAnimation loadingMessages={loadingMessages} />}
          {view === 'markdown' && (
            <>
              {imageLoading && <div className="text-center text-gray-500">Images are loading...</div>}
              <MarkdownViewer markdownContent={markdownContent} />
            </>
          )}
          {view === 'userProfile' && <UserProfilePage />}
        </div>
      </div>
    </ConceptExplanationProvider>
  );
};

export default Papuros;
