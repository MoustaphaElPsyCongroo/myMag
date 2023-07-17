import { json } from '@remix-run/node';
import { Link, useLoaderData } from '@remix-run/react';
import { authenticator } from '~/features/auth/auth.server';

export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/'
  });

  const userId = user.id;
  const thirtyFirstUnreadArticles = await fetch(
    `${process.env.BACKEND_URL}/users/${userId}/articles/unread`);
  return json(await thirtyFirstUnreadArticles.json());
};

export default function ArticlesRoute () {
  const articlesData = useLoaderData();
  const articles = articlesData.results;
  // console.log('user in articles', user);

  return (
    <>
      <h2>Here are your Articles!</h2>
      <ul>
        {articles.map(article => {
          return (
            <Link to={article.link} target='_blank' key={article.id}>
              <li>
                <h3>{article.title}</h3>
                <p>{article.description}</p>
                <img src={article.image} alt='article image' />
              </li>
            </Link>
          );
        })}
      </ul>
    </>
  );
}
