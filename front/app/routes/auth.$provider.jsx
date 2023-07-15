import { redirect } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';

export const loader = () => redirect('/');

export const action = ({ request, params }) => {
  return authenticator.authenticate(params.provider, request);
};
