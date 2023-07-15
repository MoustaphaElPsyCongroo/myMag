import { useOutletContext, useLoaderData, useFetcher } from '@remix-run/react';
import { useEffect } from 'react';

import styles from '~/styles/main/articlereader.css';

export const links = () => [
  { rel: 'stylesheet', href: styles }
];

export const loader = async () => {

};

export function ArticleReader () {
  const fetcher = useFetcher();

  useEffect(() => {
		if (!fetcher.data || fetcher.state === 'loading') {

		}
	}, []);
  return (
    <p>
      Article Reader
    </p>
  );
}
