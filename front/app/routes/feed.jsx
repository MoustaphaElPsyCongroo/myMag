import { json, redirect } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';
import { getOrImportFeedFromURL, subscribeFeed } from '~/utils/feeds.server';

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

  if (!feedUrl) {
    return redirect('/');
  }

  const { feedData, feedStatus } = await getOrImportFeedFromURL(feedUrl);
  return json({ status: feedStatus, results: feedData });
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
      return json({ status: feedStatus, results: feedData });
    }
  }
  throw json('Error: unknown Form', {
    status: 400,
    statusText: 'Error: unknown Form',
  });
};
