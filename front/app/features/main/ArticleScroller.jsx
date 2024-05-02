import { useEffect } from 'react';

export const ArticleScroller = (props) => {
  const loadMoreArticlesOnScroll = () => {
    const documentHeight = document.body.scrollHeight;
    const scrollY = window.scrollY;
    const bottom = scrollY + window.innerHeight;
    const almostAtBottom = 800 + bottom > documentHeight;

    if (almostAtBottom && !props.isMoreArticlesLoading) {
      props.loadMoreArticles();
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', loadMoreArticlesOnScroll);
    }

    return () => {
      window.removeEventListener('scroll', loadMoreArticlesOnScroll);
    };
  });

  return (
    <>
      {props.children}
      {!props.noNewArticles && props.isMoreArticlesLoading && (
        <p>Loading new articles…</p>
      )}
      {props.noNewArticles && <p>No new articles</p>}
    </>
  );
};
