import React, { useContext } from 'react';
import axios from 'axios';
import { useGoogleLogin } from '@react-oauth/google';
import { LoginContext } from './LoginContextProvider';

function LoggedIn () {
  const {
    isAuth,
    accessToken,
    idToken,
    refreshToken,
    setAuth,
    setAccessToken,
    setIdToken,
    setRefreshToken
  } = useContext(LoginContext);

  const login = useGoogleLogin({
    onSuccess: async ({ code }) => {
      const tokens = await axios.post('http://127.0.0.1:5000/api/v1/auth/login', {
        code
      });

      setAuth(tokens.data != null);
      setAccessToken(tokens.data.access_token);
      setIdToken(tokens.data.id_token);
      setRefreshToken(tokens.data.setRefreshToken);
      console.log(tokens);
    },
    flow: 'auth_code'
  });

  const logout = () => {
    localStorage.removeItem(isAuth);
    localStorage.removeItem(idToken);
    localStorage.removeItem(accessToken);
    localStorage.removeItem(refreshToken);
    setAuth(false);
  };

  // useEffect(() => {
  //   if (localStorage.getItem('JWT') == null) {
  //     return nav('/login');
  //   } else {
  //     Axios.get(`${process.env.REACT_APP_BACKEND_URL}/home`, {
  //       headers: {
  //         Authorization: `Bearer ${localStorage.getItem('JWT')}`
  //       }
  //     })
  //       .then((res) => {
  //         console.log('data: ', res.data);
  //         setAuth(res.data);
  //       })
  //       .catch((err) => { nav('/login'); });
  //   }
  // }, []);

  // const handleLogout = () => {
  //   localStorage.removeItem('JWT');
  //   return nav('/login');
  // };

  return (
    // <LoginContext.Consumer>
    //   isAuth
    //   ? (
    //   <div>
    //     <img src={idToken} alt='Profile picture' />
    //     <h1>Hello {}, Welcome</h1>
    //     <h2>Email: {}</h2>
    //     <button onClick={() => logout()}>Logout</button>
    //   </div>
    //   )
    //   : (
    //   <button onClick={login} className='login'>
    //     <img
    //       style={{ width: '50px', height: '50px', paddingTop: '10px' }}
    //       src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png'
    //       alt='Google Logo'
    //     />
    //     Log in
    //   </button>
    //   )
    // </LoginContext.Consumer>
    <div>OK</div>
  );
}

export default LoggedIn;
