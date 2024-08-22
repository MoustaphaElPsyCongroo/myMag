import { authenticator } from '~/features/auth/auth.server';

/**
 * Authenticates user
 * @param {Requests} param0
 * @returns
 */
export const loader = async ({ request, params }) => {
  return authenticator.authenticate(params.provider, request, {
    successRedirect: '/articles',
  });
};
