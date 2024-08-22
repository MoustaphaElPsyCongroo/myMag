import {
  LandingPage,
  links as landingPageLinks,
} from '~/features/main/LandingPage';
import { authenticator } from '~/features/auth/auth.server';

export const links = () => [...landingPageLinks()];

export const meta = () => [
  { title: 'myMag - Create your own magazine' },
  { name: 'description', content: 'Welcome to myMag' },
];

/**
 * On page load checks if user is authenticated, if so redirects them to
 * /articles
 * @param {Request} request Current request that brought to this route (/)
 * @returns
 */
export const loader = async ({ request }) => {
  return authenticator.isAuthenticated(request, {
    successRedirect: '/articles',
  });
};

/**
 * Index route. Default / route when user is not authenticated, thus not redirected to
 * /articles
 * @returns
 */
export default function Index() {
  return (
    <>
      <LandingPage />
    </>
  );
}
