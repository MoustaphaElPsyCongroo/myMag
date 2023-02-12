import React, { useEffect } from 'react';
import Signin from './components/SignIn/Signin';
import LoggedIn from './components/Loggedin';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

function App () {
  const login = useGoogleLogin({
    onSuccess: async ({ code }) => {
      const tokens = await axios.post('http://127.0.0.1:5000/api/v1/auth/login', {
        code
      });

      console.log(tokens);
    },
    flow: 'auth_code'
  });

  return (
    <div style={{ padding: '10px', border: '2px solid black', margin: '20px' }}>
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
}

export default App;
