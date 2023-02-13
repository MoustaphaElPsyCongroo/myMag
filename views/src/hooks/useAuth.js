import { useEffect } from 'react';
import { useUser } from './useUser';
import { useLocalStorage } from './useLocalStorage';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

export const useAuth = () => {
  const { user, addUser, removeUser } = useUser();
  const { getItem } = useLocalStorage();

  useEffect(() => {
    const user = getItem('user');
    if (user) {
      addUser(JSON.parse(user));
    }
  }, []);

  const login = useGoogleLogin({
    onSuccess: async ({ code }) => {
      const res = await axios.post('http://127.0.0.1:5000/api/v1/auth/login', {
        code
      });

      console.log(res);
      const user = res.data;

      // const user = {
      //   id: userInfo.id,
      //   name: userInfo.name,
      //   email: userInfo.email,
      //   profile_pic: userInfo.profile_pic,
      //   accessToken: userInfo.accessToken,
      //   refreshToken: userInfo.refreshToken
      // };

      addUser(JSON.parse(user));
    },
    flow: 'auth_code'
  });

  const logout = () => {
    removeUser();
  };

  return { user, login, logout };
};
