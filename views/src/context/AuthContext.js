import { createContext } from 'react';
import { User } from '../hooks/useUser';

// const AutContext = {
//   user: User | null,
//   setUser: (user) => {}
// };

export const AuthContext = createContext()({
  user: User | null,
  setUser: (user) => {}
});
