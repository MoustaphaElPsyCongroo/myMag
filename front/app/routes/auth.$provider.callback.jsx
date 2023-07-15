import { authenticator } from '~/features/auth/auth.server';

export const loader = async ({ request, params }) => {
  return authenticator.authenticate(params.provider, request, {
    successRedirect: '/articles'
  });
};
