import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router';

function SignIn (props) {
  // useEffect(() => {
  //   if (localStorage.getItem('JWT') != null) {
  //     return <Navigate to='/home' />;
  //   }
  // }, []);

  return (
    <div style={{ padding: '10px', border: '2px solid black', margin: '20px' }}>
      <button onClick={(e) => props.login(e)} className='login'>
        <img
          style={{ width: '50px', height: '50px', paddingTop: '10px' }}
          src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png'
          alt='Google Logo'
        />
        Log in With Google
      </button>
    </div>
  );
}

export default SignIn;
