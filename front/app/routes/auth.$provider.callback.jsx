import { authenticator } from '~/features/auth/auth.server';

/**
 * Authenticates user
 * @param {Requests} request
 * @returns
 */
export const loader = async ({ request, params }) => {
  return authenticator.authenticate(params.provider, request, {
    successRedirect: '/articles',
  });
};
