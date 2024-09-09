import { json } from '@remix-run/node';
import { useLoaderData, useFetcher, useRouteError } from '@remix-run/react';
import { useEffect, useState, useCallback } from 'react';
import { authenticator } from '~/features/auth/auth.server';
import { Article, links as articleLinks } from '~/features/main/Article';
import { ArticleScroller } from '~/features/main/ArticleScroller';
import {
  dislikeArticle,
  likeArticle,
  readArticle,
  undislikeArticle,
  unlikeArticle,
} from '../utils/user_articles.server';

import styles from '~/styles/main/articles.css';

export const links = () => [
  { rel: 'stylesheet', href: styles },
  ...articleLinks(),
];

/**
 * Fetches initial article data
 * @param {Request} request GET to /articles
 * @returns Received article data
 */
export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/',
  });

  const userId = user.id;
  const thirtyFirstUnreadArticles = await fetch(
    `${process.env.BACKEND_URL}/users/${userId}/articles/unread`
  );
  const articlesStatus = thirtyFirstUnreadArticles.status;
  const articlesData = await thirtyFirstUnreadArticles.json();

  if (articlesStatus >= 400) {
    const errorMessage = articlesData.error.split(': ')[1];
    throw json(errorMessage, {
      status: articlesStatus,
      statusText: errorMessage,
    });
  }

  // Response here has different structure from the other loaders/actions (no
  // {status: x, results: y}) because API doesn't only return a single array or
  // object but an object + array in the form {total: nb, results: r}. Would be
  // redundant to then access articlesData.results.[index].results so I only
  // return the data and instead access status + render errors in an
  // ErrorBoundary
  return json(articlesData);
};

/**
 * Handles article actions (read, like/dislike/un)
 * @param {Request} request POST to /articles
 * @returns
 */
export const action = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/',
  });
  const userId = user.id;
  const formData = await request.formData();
  const { _action, ...values } = Object.fromEntries(formData);
  const articleId = values.id;

  switch (_action) {
    case 'like_article': {
      const { likeData, likeStatus } = await likeArticle(userId, articleId);
      return json({
        status: likeStatus,
        results: likeData,
        shouldNotRevalidate: true,
      });
    }
    case 'unlike_article': {
      const { unlikeData, unlikeStatus } = await unlikeArticle(
        userId,
        articleId
      );
      return json({
        status: unlikeStatus,
        results: unlikeData,
        shouldNotRevalidate: true,
      });
    }
    case 'dislike_article': {
      const { dislikeData, dislikeStatus } = await dislikeArticle(
        userId,
        articleId
      );
      return json({
        status: dislikeStatus,
        results: dislikeData,
        shouldNotRevalidate: true,
      });
    }
    case 'undislike_article': {
      const { undislikeData, undislikeStatus } = await undislikeArticle(
        userId,
        articleId
      );
      return json({
        status: undislikeStatus,
        results: undislikeData,
        shouldNotRevalidate: true,
      });
    }
    case 'read_article': {
      const { readData, readStatus } = await readArticle(userId, articleId);
      return json({
        status: readStatus,
        results: readData,
        shouldNotRevalidate: true,
      });
    }
  }
  throw json('Error: unknown Form', {
    status: 400,
    statusText: 'Error: unknown Form',
  });
};

/**
 * Articles route, main page displaying all articles
 * @returns
 */
export default function ArticlesRoute() {
  const articlesData = useLoaderData();
  const fetcher = useFetcher();

  const [articles, setArticles] = useState(articlesData.results);
  const [noNewArticles, setNoNewArticles] = useState(articlesData.total === 0);

  useEffect(() => {
    if (!fetcher.data || fetcher.state !== 'idle') {
      return;
    }

    if (fetcher.data) {
      const receivedArticles = fetcher.data.results;

      setNoNewArticles(fetcher.data.total === 0);
      // setArticles((existingArticles) => [...existingArticles,
      // ...newArticles]);

      setArticles((existingArticles) => {
        const newArticles = receivedArticles.filter(
          (article) =>
            !existingArticles.some(
              (existingArticle) => article.id === existingArticle.id
            )
        );

        return [...existingArticles, ...newArticles];
      });
    }
  }, [fetcher.data, fetcher.state]);

  const loadMoreArticles = useCallback(() => {
    if (!noNewArticles && fetcher.state === 'idle') {
      fetcher.load('/articles');
    }
  }, [fetcher, noNewArticles]);

  return (
    <>
      <div className="articles-container">
        {articles && articlesData.total > 0 && (
          <ArticleScroller
            loadMoreArticles={loadMoreArticles}
            isMoreArticlesLoading={fetcher.state !== 'idle'}
            noNewArticles={noNewArticles}
          >
            {articles.map((article) => (
              <Article key={article.id} article={article} />
            ))}
          </ArticleScroller>
        )}
      </div>
    </>
  );
}

// In case of performance or data usage impact, use action responses'
// shouldNotRevalidate field to prevent refetching the API each time an action
// is called. But in this case it's useful to keep the counter of unread
// articles updated without using other methods.

/**
 * Prevents reloading this route after an action has been sent (like
 * liking/marking as read/etc)
 */
// export const shouldRevalidate = ({ actionResult, defaultShouldRevalidate }) => {
//   if (actionResult?.shouldNotRevalidate) {
//     return false;
//   }
//   return defaultShouldRevalidate;
// };

// TODO: Handle and render loader errors here
export const ErrorBoundary = () => {
  const error = useRouteError();

  return (
    <div>
      <p>Error! {error.statusText}</p>
    </div>
  );
};
