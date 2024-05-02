import { useEffect } from 'react';

export const ArticleScroller = ({
  isMoreArticlesLoading,
  noNewArticles,
  loadMoreArticles,
  children,
}) => {
  useEffect(() => {
    const loadMoreArticlesOnScroll = () => {
      const documentHeight = document.body.scrollHeight;
      const scrollY = window.scrollY;
      const bottom = scrollY + window.innerHeight;
      const almostAtBottom = 800 + bottom > documentHeight;

      if (almostAtBottom) {
        loadMoreArticles();
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('scrollend', loadMoreArticlesOnScroll);
    }

    return () => {
      window.removeEventListener('scrollend', loadMoreArticlesOnScroll);
    };
  }, [loadMoreArticles]);

  return (
    <>
      {children}
      {(!noNewArticles || isMoreArticlesLoading) && (
        <p>Loading new articles…</p>
      )}
      {noNewArticles && <p>No new articles</p>}
    </>
  );
};
