import { useState, useEffect } from 'react';

/**
 * Infinite scroll manager component for articles
 * @param {boolean} isMoreArticlesLoading Indicates if more articles are loading
 * @param {boolean} noNewArticles Indicates if no new articles are left
 * @param {function} loadMoreArticles Function prop calling /articles loader
 * @param {React.JSX.Element} children Children elements, by default articles
 * @returns
 */
export const ArticleScroller = ({
  isMoreArticlesLoading,
  noNewArticles,
  loadMoreArticles,
  children,
}) => {
  const [displayLoading, setDisplayLoading] = useState('block');

  useEffect(() => {
    let loadMoreArticlesTimeout;

    /**
     * Gives a time limit to displaying of article loading indicator, so
     * fetching ending with no new articles but still articles unread remaining
     * (in case of manual unread marking for example), can display "no new
     * articles"
     */
    const setupLoadingTimelimit = () => {
      setTimeout(() => {
        setDisplayLoading('none');
      }, 8000);
    };

    /**
     * Fetches new articles from the API when scroll position is almost at the
     * bottom of the screen. Debounced to account for scrolling speed
     * risking to call the API multiple times in the interval where parent
     * component's fetcher state didn't have time to be updated.
     */
    const loadMoreArticlesOnScroll = () => {
      const documentHeight = document.body.scrollHeight;
      const scrollY = window.scrollY;
      const bottom = scrollY + window.innerHeight;
      const almostAtBottom = 800 + bottom > documentHeight;

      if (displayLoading === 'none') {
        setDisplayLoading('block');
      }

      if (almostAtBottom) {
        clearTimeout(loadMoreArticlesTimeout);
        loadMoreArticlesTimeout = setTimeout(() => {
          loadMoreArticles();
          setupLoadingTimelimit();
        }, 1000);
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', loadMoreArticlesOnScroll);
    }

    return () => {
      window.removeEventListener('scroll', loadMoreArticlesOnScroll);
    };
  }, [loadMoreArticles, displayLoading]);

  return (
    <>
      {children}
      {(!noNewArticles || isMoreArticlesLoading) && (
        <p style={{ display: displayLoading }}>Loading new articles…</p>
      )}
      {(noNewArticles || displayLoading === 'none') && <p>No new articles</p>}
    </>
  );
};
