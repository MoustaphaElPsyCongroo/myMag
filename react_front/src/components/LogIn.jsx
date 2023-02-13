import React, { useState, useContext } from 'react';
import axios from 'axios';
import { useGoogleLogin } from '@react-oauth/google';
// import { login } from '../services/AuthService';
import UserContext from '../services/UserContext';

const LogIn = () => {
  const [currentUser, setCurrentUser] = useContext(UserContext);

  const login = useGoogleLogin({
    onSuccess: async ({ code }) => {
      const res = await axios.post('http://127.0.0.1:5000/api/v1/auth/login', {
        code
      });

      console.log('LogIn ', res);
      const user = res.data;

      if (user.access_token) {
        console.log('good');
        localStorage.setItem('user', JSON.stringify(user));
      }

      // const user = {
      //   id: userInfo.id,
      //   name: userInfo.name,
      //   email: userInfo.email,
      //   profile_pic: userInfo.profile_pic,
      //   accessToken: userInfo.accessToken,
      //   refreshToken: userInfo.refreshToken
      // };

      // return user;
      setCurrentUser(user);
    },
    flow: 'auth_code'
  });
  return (
    <button onClick={login} className='login'>
      <img
        style={{ width: '50px', height: '50px', paddingTop: '10px' }}
        src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png'
        alt='Google Logo'
      />
      Log in
    </button>
  );
};

export default LogIn;
