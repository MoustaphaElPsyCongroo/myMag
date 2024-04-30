import { json } from '@remix-run/node';
import { useLoaderData, useNavigation } from '@remix-run/react';
import { authenticator } from '~/features/auth/auth.server';
import { Article, links as articleLinks } from '~/features/main/Article';
import { dislikeArticle, likeArticle, readArticle, undislikeArticle, unlikeArticle } from '../utils/user_articles.server';

import styles from '~/styles/main/articles.css';

export const links = () => [
  { rel: 'stylesheet', href: styles },
  ...articleLinks()
];

export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/'
  });

  const userId = user.id;
  const thirtyFirstUnreadArticles = await fetch(
    `${process.env.BACKEND_URL}/users/${userId}/articles/unread`);
  const articlesData = await thirtyFirstUnreadArticles.json();
  return json(articlesData);
};

export const action = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/'
  });
  const userId = user.id;
  const formData = await request.formData();
  const { _action, ...values } = Object.fromEntries(formData);
  const articleId = values.id;

  // console.log(_action);

  switch (_action) {
    case 'like_article': {
      const { likeData, likeStatus } = await likeArticle(userId, articleId);
      if (likeStatus !== 200) {
        throw json(likeData.error, { status: likeStatus, statusText: likeData.error });
      }
      return json(likeData);
    }
    case 'unlike_article': {
      const { unlikeData, unlikeStatus } = await unlikeArticle(userId, articleId);
      if (unlikeStatus !== 200) {
        throw json(unlikeData.error, { status: unlikeStatus, statusText: unlikeData.error });
      }
      return json(unlikeData);
    }
    case 'dislike_article': {
      const { dislikeData, dislikeStatus } = await dislikeArticle(userId, articleId);
      if (dislikeStatus !== 200) {
        throw json(dislikeData.error, { status: dislikeStatus, statusText: dislikeData.error });
      }
      return json(dislikeData);
    }
    case 'undislike_article': {
      const { undislikeData, undislikeStatus } = await undislikeArticle(userId, articleId);
      if (undislikeStatus !== 200) {
        throw json(undislikeData.error, { status: undislikeStatus, statusText: undislikeData.error });
      }
      return json(undislikeData);
    }
    case 'read_article': {
      const { readData, readStatus } = await readArticle(userId, articleId);
      if (readStatus !== 200) {
        throw json(readData.error, { status: readStatus, statusText: readData.error });
      }
      return json(readData);
    }
  }
  throw json('Error: unknown Form', { status: 400, statusText: 'Error: unknown Form' });
};

export default function ArticlesRoute () {
  const articlesData = useLoaderData();
  const articles = articlesData.results;
  const loadingState = useNavigation();

  return (
    <>
      <h2>{articlesData.total} new articles</h2>
      <div className='articles-container'>
        {loadingState === 'loading' ?
        <p>It's been a while.<br />Let's take the time to sort your articles...</p>
        :
        articles.map(article => <Article key={article.id} article={article} />)}
      </div>
    </>
  );
}

export const shouldRevalidate = ({ actionResult, defaultShouldRevalidate }) => {
  if (actionResult) {
    return false;
  }
  return defaultShouldRevalidate;
};

// TODO: Handle and render action errors here
// export const CatchBoundary = () => {
// }
