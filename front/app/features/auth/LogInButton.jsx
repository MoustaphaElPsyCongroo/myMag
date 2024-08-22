import { Form } from '@remix-run/react';
import { SocialsProvider } from 'remix-auth-socials';

import styles from '~/styles/auth/loginButton.css';
import googleLogo from '~/styles/auth/googleLogo.png';

export const links = () => [{ rel: 'stylesheet', href: styles }];

/**
 * A button that logs the user in with the specified provider
 * @param {string} provider The login provider name (e.g. "google")
 * @returns A login button that logs in to Google
 */
export const LogInButton = ({ provider }) => {
  const SocialButton = ({ provider }) => (
    <Form action={`/auth/${provider}`} method="post">
      <button className="login">
        <img src={googleLogo} alt="Google Logo" />
      </button>
    </Form>
  );

  return (
    <div className="login-container">
      {provider === 'google' && (
        <SocialButton provider={SocialsProvider.GOOGLE} />
      )}
    </div>
  );
};
