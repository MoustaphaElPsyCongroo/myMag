import { AuthContext } from '../context/AuthContext';

export default function LoggedIn (props) {
  return (
    <AuthContext.Consumer>
      <div>
        <img src={idToken} alt='Profile picture' />
        <h1>Hello {}, Welcome</h1>
        <h2>Email: {}</h2>
        <button onClick={() => props.logout()}>Logout</button>
      </div>
    </AuthContext.Consumer>
  );
}
