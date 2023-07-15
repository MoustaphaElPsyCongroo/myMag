import { LogInButton, links as logInButtonLinks } from '~/features/auth/LogInButton';
import { LogOutButton, links as logOutButtonLinks } from '~/features/auth/LogOutButton';

import styles from '~/styles/header/header.css';

export const links = () => [
  { rel: 'stylesheet', href: styles },
  ...logInButtonLinks(),
  ...logOutButtonLinks()
];

export const Header = ({ user }) => {
  return (
    <header>
      <h1>myMag</h1>
      <span>Create your own Magazine</span>
      {user?.id ? <LogOutButton profilePic={user.profile_pic} /> : <LogInButton provider='google' />}
    </header>
  );
};
