import { json } from '@remix-run/node';
// import { useLoaderData } from '@remix-run/react';
import { authenticator } from '~/features/auth/auth.server';

export const loader = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/'
  });

  return json(user);
};

export default function ArticlesRoute () {
  // const user = useLoaderData();
  // console.log('user in articles', user);

  return <h2>Here are your Articles!</h2>;
}
