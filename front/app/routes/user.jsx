import { authenticator } from '~/features/auth/auth.server';

export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request);
  console.log('user dans ressource route', user);
  return user || {};
};
