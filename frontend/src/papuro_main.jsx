import React, { useState, useEffect } from 'react';
import InitialSearch from './InitialSearch';
import SourceCollectAnime from './source_collect_anime'; // Import the source_collect anime component
import OutlineGenerationScreen from './outline_loading_anime'; // Import the OutlineGenerationScreen component
import SectionWriterScreen from './section_writer_anime'; // Import the SectionWriterScreen component
import MarkdownViewer from './MarkdownViewer';
import LeftNavigationBar from './LeftNavigationBar';
import UserProfilePage from './UserProfilePage';
import BookshelfPage from './BookShelfPage';
import ConceptExplanationProvider from './ConceptExplanation';

const Papuros = () => {
  const [view, setView] = useState('initial'); // 'initial', 'source_collecting', 'outline_generating', 'section_writing', 'markdown', 'profile', 'archive'
  const [markdownContent, setMarkdownContent] = useState('');
  const [loadingMessages, setLoadingMessages] = useState([]); // Store loading messages
  const [imageLoading, setImageLoading] = useState(false);

  const handleSearch = (query) => {
    console.log('Search query:', query);

    // Step 1: Save the query to topic.txt
    fetch(`https://papuros-backend.onrender.com/save_query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    }).then(() => {
      // Step 2: Run the generate process after saving the query
      setLoadingMessages([]); // Reset loading messages

      const eventSource = new EventSource(`https://papuros-backend.onrender.com/generate?query=${encodeURIComponent(query)}`);

      eventSource.onmessage = (event) => {
        const message = event.data;
        setLoadingMessages((prevMessages) => [...prevMessages, message]);

        if (message.includes('Collecting sources from academic and web sources')) {
          setView('source_collecting'); // Display specific animation for source collection
        } else if (message.includes('Generating article outline based on collected sources')) {
          setView('outline_generating'); // Switch to outline generation animation
        } else if (message.includes('Writing article sections based on outline')) {
          setView('section_writing'); // Switch to section writing animation
        } else if (message.includes('Text generation complete')) {
          // Close the event source temporarily to avoid further updates during text display
          eventSource.close();

          // Display article.md
          fetch('https://papuros-backend.onrender.com/article')
            .then((response) => {
              if (!response.ok) throw new Error('Network response was not ok');
              return response.text();
            })
            .then((text) => {
              setMarkdownContent(text);
              setView('markdown');
              setImageLoading(true); // Show image loading message
              checkForUpdatedArticle(); // Start polling for updated_article.md
            })
            .catch((error) => console.error('Error loading Markdown file:', error));
        } else if (message.includes('Image generation started')) {
          setImageLoading(true); // Update the state to show the image loading message
        }
      };

      eventSource.onerror = (err) => {
        console.error('EventSource failed:', err);
        eventSource.close();
      };
    }).catch(error => console.error('Error saving query:', error));
  };

  const checkForUpdatedArticle = () => {
    fetch('https://papuros-backend.onrender.com/updated_article')
      .then(response => {
        if (response.status === 200) {
          return response.text();
        } else if (response.status === 202) {
          setTimeout(checkForUpdatedArticle, 3000); // Retry every 3 seconds if not ready
          return null;
        }
      })
      .then(updatedContent => {
        if (updatedContent) {
          setMarkdownContent(updatedContent);
          setImageLoading(false); // Image loading complete
        }
      })
      .catch(error => console.error('Error checking updated article:', error));
  };

  const handleHomeClick = () => {
    setView('initial'); // Set the view to 'initial' to return to the initial search
  };

  const handleProfileClick = () => {
    setView('profile'); // Set the view to 'profile' to show UserProfilePage
  };

  const handleArchivesClick = () => {
    setView('archive'); // Set the view to 'archive' to show BookshelfPage
  };

  return (
    <ConceptExplanationProvider>
      <div className="flex h-screen bg-gray-50">
        <LeftNavigationBar 
          onHomeClick={handleHomeClick} 
          onProfileClick={handleProfileClick} 
          onArchivesClick={handleArchivesClick} 
        />
        <div className="flex-1">
          {view === 'initial' && <InitialSearch onSearch={handleSearch} />}
          {view === 'source_collecting' && (
            <div className="flex h-screen">
              <div className="flex-1">
                <SourceCollectAnime />
              </div>
            </div>
          )}
          {view === 'outline_generating' && (
            <div className="flex h-screen">
              <div className="flex-1">
                <OutlineGenerationScreen />
              </div>
            </div>
          )}
          {view === 'section_writing' && (
            <div className="flex h-screen">
              <div className="flex-1">
                <SectionWriterScreen />
              </div>
            </div>
          )}
          {view === 'markdown' && (
            <>
              {imageLoading && (
                <div className="text-center text-gray-500">Images are loading...</div>
              )}
              <MarkdownViewer markdownContent={markdownContent} />
            </>
          )}
          {view === 'profile' && <UserProfilePage />}
          {view === 'archive' && <BookshelfPage />}
        </div>
      </div>
    </ConceptExplanationProvider>
  );
};

export default Papuros;
