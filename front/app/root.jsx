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

import normalizeCss from '~/styles/normalize.css';
import globalStyles from '~/styles/global.css';

export const links = () => [
  { rel: 'stylesheet', href: normalizeCss },
  { rel: 'stylesheet', href: globalStyles },
  ...headerLinks()
];

export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request);
  console.log('user', user);
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
        <Outlet />
        <ScrollRestoration />
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}
