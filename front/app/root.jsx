import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLoaderData,
} from '@remix-run/react';
import { authenticator } from '~/features/auth/auth.server';

import { Header, links as headerLinks } from '~/features/header/Header';
import { Sidebar, links as sidebarLinks } from './features/sidebar/Sidebar';
import { getUserFeeds } from './utils/feeds.server';

import normalizeCss from '~/styles/normalize.css';
import globalStyles from '~/styles/global.css';
import { json } from '@remix-run/node';

export const links = () => [
  { rel: 'stylesheet', href: normalizeCss },
  { rel: 'stylesheet', href: globalStyles },
  ...headerLinks(),
  ...sidebarLinks(),
];

/**
 * Loads the logged in user for distribution to permanent components (Header,
 * Sidebar) and their subscribed feeds (for Sidebar).
 * @param {Request} request GET to the site
 * @returns Logged user data or empty object
 */
export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request);

  if (!user) {
    return json({ user: null, feeds: null });
  }

  const userId = user.id;
  const { feedsData, feedsStatus } = await getUserFeeds(userId);
  return json({
    user: user,
    feeds: { status: feedsStatus, results: feedsData },
  });
};

/**
 * Root route. Generates whole app structure. All routes are rendering through
 * the Outlet. Header and Sidebar are permanent components spanning every route.
 * @returns App structure
 */
export default function App() {
  const globalData = useLoaderData();
  const user = globalData.user;
  const subscribedFeeds = globalData.feeds;

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <Header user={user} />
        <div className="main-container">
          {user && <Sidebar feeds={subscribedFeeds} />}
          <main>
            <Outlet />
          </main>
        </div>
        <ScrollRestoration />
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}
