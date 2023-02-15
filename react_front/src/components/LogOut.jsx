import React, { useContext } from 'react';
import UserContext from '../services/UserContext';

const LogOut = () => {
  const [currentUser, setCurrentUser] = useContext(UserContext);

  const logout = () => {
    localStorage.removeItem('user');
    setCurrentUser({});
  };

  return (
    <div>
      <img src={currentUser.profile_pic} alt='Profile picture' />
      <h1>Hello {currentUser.name}, Welcome</h1>
      <h2>Email: {currentUser.email}</h2>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default LogOut;
