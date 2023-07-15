import { authenticator } from '~/features/auth/auth.server';

export const action = async ({ request }) => {
  await authenticator.logout(request, { redirectTo: '/' });
};
