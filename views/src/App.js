import React, { useEffect } from 'react';
import Signin from './components/SignIn/Signin';
import LoggedIn from './components/Loggedin';
import { Routes, Route, Navigate } from 'react-router-dom';
import Axios from 'axios';

function App () {
  const handleClick = (e) => {
    console.log(process.env.REACT_APP_BACKEND_URL);
    e.preventDefault();
    Axios.get(`${process.env.REACT_APP_BACKEND_URL}/auth/google`, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    })
      .then((res) => {
        console.log('going!');
        window.location.assign(res.data.auth_url);
        console.log('gone!');
      })
      .catch((err) => console.error(err));
    console.log(process.env.REACT_APP_BACKEND_URL);
  };

  useEffect(() => {
    if (localStorage.getItem('JWT') == null) {
      const query = new URLSearchParams(window.location.search);
      const token = query.get('jwt');
      if (token) {
        localStorage.setItem('JWT', token);
        return <Navigate to='/home' />;
      }
    }
  }, []);

  return (
    <Routes>
      <Route
        exact
        path='/login'
        element={<Signin login={handleClick} />}
      />
      <Route path='/home' element={<LoggedIn />} />
    </Routes>
  );
}

export default App;
