import React, { useEffect, useState } from 'react';
import Axios from 'axios';
import { useNavigate } from 'react-router';

function LoggedIn () {
  const [auth, setAuth] = useState(null);
  const nav = useNavigate();
  useEffect(() => {
    if (localStorage.getItem('JWT') == null) {
      return nav('/login');
    } else {
      Axios.get(`${process.env.REACT_APP_BACKEND_URL}/home`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('JWT')}`
        }
      })
        .then((res) => {
          console.log('data: ', res.data);
          setAuth(res.data);
        })
        .catch((err) => { nav('/login'); });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('JWT');
    return nav('/login');
  };
  return (
    <div style={{ padding: '10px', border: '2px solid black', margin: '20px' }}>
      <img src={auth ? auth.user_picture : ''} alt='Profile picture' />
      <h1>Hello {auth ? auth.user_name : ''}, Welcome</h1>
      <h2>Email: {auth ? auth.user_email : ''}</h2>
      <button onClick={() => handleLogout()}>Logout</button>
    </div>
  );
}

export default LoggedIn;
