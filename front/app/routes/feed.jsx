import { json } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';
import { searchFeed, subscribeFeed } from '~/utils/feeds.server';

/**
 * Fetches a feed by url
 * @param {Request} request GET to /feed
 * @returns Fetched feed data
 */
export const loader = async ({ request }) => {
  // const user = await authenticator.isAuthenticated(request, {
  //   failureRedirect: '/'
  // });

  const url = new URL(request.url);
  const search = new URLSearchParams(url.search);
  const feedUrl = search.get('query_feed');

  const { feedData, feedStatus } = await searchFeed(feedUrl);
  if (feedStatus !== 200) {
    return json({ error: feedData.error, status: feedStatus });
  }
  return json(feedData);
};

/**
 * Handles feed POST requests, for subscribing for example
 * @param {Request} request POST to /feed
 * @returns
 */
export const action = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/',
  });
  const userId = user.id;
  const formData = await request.formData();
  const { _action, ...values } = Object.fromEntries(formData);
  const feedId = values.id;

  switch (_action) {
    case 'subscribe_feed': {
      const { feedData, feedStatus } = await subscribeFeed(userId, feedId);
      if (feedStatus !== 200) {
        return json({ error: feedData.error, status: feedStatus });
      }
      return json(feedData);
    }
  }
  throw json('Error: unknown Form', {
    status: 400,
    statusText: 'Error: unknown Form',
  });
};
