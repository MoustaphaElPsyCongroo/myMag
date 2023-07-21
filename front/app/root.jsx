import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLoaderData
} from '@remix-run/react';
import { authenticator } from '~/features/auth/auth.server';

import { Header, links as headerLinks } from '~/features/header/Header';
import { Sidebar, links as sidebarLinks } from './features/sidebar/Sidebar';

import normalizeCss from '~/styles/normalize.css';
import globalStyles from '~/styles/global.css';

export const links = () => [
  { rel: 'stylesheet', href: normalizeCss },
  { rel: 'stylesheet', href: globalStyles },
  ...headerLinks(),
  ...sidebarLinks()
];

export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request);
  return user || {};
};

export default function App () {
  const user = useLoaderData();

  return (
    <html lang='en'>
      <head>
        <meta charSet='utf-8' />
        <meta name='viewport' content='width=device-width,initial-scale=1' />
        <Meta />
        <Links />
      </head>
      <body>
        <Header user={user} />
        <div className='main-container'>
          <Sidebar user={user} />
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
