import { useOutletContext } from '@remix-run/react';
import { LandingPage, links as landingPageLinks } from '~/features/main/LandingPage';
import { ArticleReader, links as articleReaderLinks } from '~/features/main/ArticleReader';

import styles from '~/styles/main/main.css';

export const links = () => [
  { rel: 'stylesheet', href: styles }
];

export function Main () {
  const [currentUser] = useOutletContext();

  return (
    <main>
      {currentUser?.id_token ? <ArticleReader /> : <LandingPage />}
    </main>
  );
}
