import React, { useState, useEffect, createContext } from 'react';
import { isAuthenticated } from './AuthService';

import LogIn from '../components/LogIn';
import LogOut from '../components/LogOut';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(undefined);

  useEffect(() => {
    const checkLoggedIn = () => {
      let cuser = isAuthenticated();
      console.log('UserContext avant', cuser);
      if (cuser === null) {
        console.log('type au moment de setUser dans UserContext', typeof cuser);
        localStorage.setItem('user', '');
        cuser = '';
      }

      setCurrentUser(cuser);
    };

    // Uncomment en cas de pb dans le code
    // localStorage.removeItem('user');
    checkLoggedIn();
  }, []);

  console.log('UserContext ', currentUser);

  return (
    <UserContext.Provider value={[currentUser, setCurrentUser]}>
      {currentUser?.access_token ? <LogOut /> : <LogIn />}
    </UserContext.Provider>
  );
};

export default UserContext;
