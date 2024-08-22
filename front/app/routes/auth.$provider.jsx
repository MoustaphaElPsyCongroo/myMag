import { redirect } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';

/**
 * Fallback loader, unused
 * @returns
 */
export const loader = () => redirect('/');

/**
 * Authenticates user
 * @param {Request} param0
 * @returns
 */
export const action = ({ request, params }) => {
  return authenticator.authenticate(params.provider, request);
};
