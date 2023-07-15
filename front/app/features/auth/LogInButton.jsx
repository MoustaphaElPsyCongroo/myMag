import { Form } from '@remix-run/react';
import { SocialsProvider } from 'remix-auth-socials';

import styles from '~/styles/auth/loginButton.css';
import googleLogo from '~/styles/auth/googleLogo.png';

export const links = () => [
  { rel: 'stylesheet', href: styles }
];

export const LogInButton = ({ provider }) => {
  const SocialButton = ({ provider }) => (
    <Form action={`/auth/${provider}`} method='post'>
      <button className='login'>
        <img
          src={googleLogo}
          alt='Google Logo'
        />
      </button>
    </Form>
  );

  return (
    <div className='login-container'>
      {provider === 'google' && <SocialButton provider={SocialsProvider.GOOGLE} />}
    </div>
  );
};
