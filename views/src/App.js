import React from 'react';
// import { LoginContext } from './components/LoginContextProvider';
import { useAuth } from './hooks/useAuth';

function App () {
  // const login = useGoogleLogin({
  //   onSuccess: async ({ code }) => {
  //     const tokens = await axios.post('http://127.0.0.1:5000/api/v1/auth/login', {
  //       code
  //     });

  //     console.log(tokens);
  //   },
  //   flow: 'auth_code'
  // });

  const { user, login, logout } = useAuth();

  // <div style={{ padding: '10px', border: '2px solid black', margin: '20px' }}>
  //   <button onClick={login} className='login'>
  //     <img
  //       style={{ width: '50px', height: '50px', paddingTop: '10px' }}
  //       src='https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png'
  //       alt='Google Logo'
  //     />
  //     Log in
  //   </button>
  // </div>
  // <LoginContext>
  //   <div style={{ padding: '10px', border: '2px solid black', margin: '20px' }}>
  //     <LoggedIn />
  //   </div>
  // </LoginContext>
  if (user) {
    return (

      <div>
        <img src={user.id} alt='Profile picture' />
        <h1>Hello {user.name}, Welcome</h1>
        <h2>Email: {user.email}</h2>
        <button onClick={() => logout()}>Logout</button>
      </div>

    )
    ;
  } else {
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
  }
}

export default App;
