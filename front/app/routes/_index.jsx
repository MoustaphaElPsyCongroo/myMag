import { LandingPage, links as landingPageLinks } from '~/features/main/LandingPage';
import { authenticator } from '~/features/auth/auth.server';

export const links = () => [
  ...landingPageLinks()
];

export const meta = () => [
  { title: 'myMag - Create your own magazine' },
  { name: 'description', content: 'Welcome to myMag' }
];

export const loader = async ({ request }) => {
  return authenticator.isAuthenticated(request, {
    successRedirect: '/articles'
  });
};

export default function Index () {
  return (
    <>
      <LandingPage />
    </>
  );
}
