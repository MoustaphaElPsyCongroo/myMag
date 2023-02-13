import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

// export const login = useGoogleLogin({
//   onSuccess: async ({ code }) => {
//     const res = await axios.post('http://127.0.0.1:5000/api/v1/auth/login', {
//       code
//     });

//     console.log('authService ', res);
//     const user = res.data;

//     if (user.access_token) {
//       localStorage.setItem('user', user);
//     }

//     // const user = {
//     //   id: userInfo.id,
//     //   name: userInfo.name,
//     //   email: userInfo.email,
//     //   profile_pic: userInfo.profile_pic,
//     //   accessToken: userInfo.accessToken,
//     //   refreshToken: userInfo.refreshToken
//     // };

//     return user;
//   },
//   flow: 'auth_code'
// });

export const isAuthenticated = () => {
  const user = localStorage.getItem('user');
  console.log('isAuthenticated ', user);
  if (!user) {
    return {};
  }
  return JSON.parse(user);
};
