import { Authenticator } from 'remix-auth';
import { GoogleStrategy, SocialsProvider } from 'remix-auth-socials';
import { sessionStorage } from '~/sessions';

export const authenticator = new Authenticator(sessionStorage, {
  sessionKey: '_user_session'
});

const getCallback = provider => {
  return `${process.env.FRONTEND_URL}/auth/${provider}/callback`;
};

authenticator.use(new GoogleStrategy(
  {
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: getCallback(SocialsProvider.GOOGLE)
  },
  async ({ refreshToken, extraParams, profile }) => {
    const idToken = extraParams?.id_token;
    const expiresIn = extraParams?.expires_in;

    const url = `${process.env.BACKEND_URL}/auth/login`;
    const userRes = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${idToken}`,
        Refreshing: `RefreshToken ${refreshToken}`
      },
      body: JSON.stringify({
        id: profile._json.sub,
        expires_in: expiresIn
      })
    });

    if (!userRes.ok) {
      // TODO: Add exception handling here to catch eventual error from the API
      return null;
    }

    const userData = await userRes.json();
    return { ...userData };
  }
));
