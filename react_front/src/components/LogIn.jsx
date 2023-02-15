import React, { useContext } from 'react';
import axios from 'axios';
import { useGoogleLogin } from '@react-oauth/google';
import UserContext from '../services/UserContext';

const LogIn = () => {
  const [currentUser, setCurrentUser] = useContext(UserContext);

  const login = useGoogleLogin({
    onSuccess: async ({ code }) => {
      const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/auth/login`, {
        code
      });

      const user = res.data;

      if (user.id_token) {
        localStorage.setItem('user', JSON.stringify(user));
      }

      setCurrentUser(user);
    },
    flow: 'auth_code'
  });
  return (
    <div>
      <button onClick={login} className='login'>
        <img
          style={{ width: '50px', height: '50px', paddingTop: '10px' }}
          src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png'
          alt='Google Logo'
        />
        Log in
      </button>
    </div>
  );
};

export default LogIn;
