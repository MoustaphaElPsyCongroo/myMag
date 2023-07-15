import { Form } from '@remix-run/react';

import styles from '~/styles/auth/logoutButton.css';

export const links = () => [
  { rel: 'stylesheet', href: styles }
];

export function LogOutButton ({ profilePic }) {
  return (
    <Form action='/logout' method='post' className='logout-container'>
      <img src={profilePic} alt='User profile picture' />
      <button>Logout</button>
    </Form>
  );
}
