import { useEffect, useState, createContext } from 'react';

export const LoginContext = createContext({
  isAuth: false,
  accessToken: '',
  idToken: '',
  refreshToken: '',
  setAuth: () => {}
});

const LoginProvider = ({ child }) => {
  const [isAuth, setAuth] = useState(localStorage.getItem('isAuth') || false);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
  const [idToken, setIdToken] = useState(localStorage.getItem('idToken'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));
  useEffect(() => {
    localStorage.setItem('isAuth', isAuth);
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('idToken', idToken);
    localStorage.setItem('refreshToken', refreshToken);
  }, [isAuth, accessToken, idToken, refreshToken]);

  return (
    <LoginContext.LoginProvider value={{
      isAuth,
      accessToken,
      idToken,
      refreshToken,
      setAuth,
      setAccessToken,
      setIdToken,
      setRefreshToken
    }}
    >
      {child}
    </LoginContext.LoginProvider>
  );
};
