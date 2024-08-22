import { authenticator } from '~/features/auth/auth.server';

/**
 * Logs out the user, redirecting to index route
 * @param {Request} request POST to /logout
 */
export const action = async ({ request }) => {
  await authenticator.logout(request, { redirectTo: '/' });
};
