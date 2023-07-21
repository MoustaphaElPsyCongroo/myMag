import styles from '~/styles/main/landingpage.css';

export const links = () => [
  { rel: 'stylesheet', href: styles }
];

export function LandingPage () {
  return (
    <h2>Here a landing page will introduce you to the site… later</h2>
  );
}
