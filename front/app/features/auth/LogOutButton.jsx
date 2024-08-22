import { Form } from '@remix-run/react';

import styles from '~/styles/auth/logoutButton.css';

export const links = () => [{ rel: 'stylesheet', href: styles }];

/**
 * A button that logs the user out by redirecting to the /logout route.
 * @param {string} profilePic The user's profile pic to decorate the button
 * @returns A Form redirecting to the /logout route
 */
export function LogOutButton({ profilePic }) {
  return (
    <Form action="/logout" method="post" className="logout-container">
      <img src={profilePic} alt="User profile" />
      <button>Logout</button>
    </Form>
  );
}
