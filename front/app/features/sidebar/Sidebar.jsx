import { useFetcher } from '@remix-run/react';
import { useRef } from 'react';
import { FeedSubscriber } from './FeedSubscriber';

import styles from '~/styles/sidebar/sidebar.css';

export const links = () => [{ rel: 'stylesheet', href: styles }];

export const Sidebar = () => {
  const fetcher = useFetcher();
  const feeder = useFetcher();
  const formRef = useRef();

  const subscribeFeed = (e) => {
    const feedId = e.currentTarget.dataset.feed_id;
    feeder.submit(
      {
        _action: 'subscribe_feed',
        id: feedId,
      },
      { method: 'post', action: '/feed' }
    );
    formRef.current?.reset();
  };

  // useEffect(() => {
  //   const hideFeedDropdown = () => {
  //     const dropdowns = document.getElementsByClassName('dropdown');
  //     for (let i = 0; i < dropdowns.length; i++) {
  //       const openDropdown = dropdowns[i];
  //       if (openDropdown.classList.contains('show')) {
  //         openDropdown.classList.remove('show');
  //       }
  //     }
  //   };

  //   if (typeof window !== 'undefined') {
  //     window.addEventListener('click', hideFeedDropdown);
  //   }

  //   return () => {
  //     window.removeEventListener('click', hideFeedDropdown);
  //   };
  // }, []);

  return (
    <div className="sidebar-container">
      <fetcher.Form method="get" action="/feed" ref={formRef}>
        <FeedSubscriber
          fetcher={fetcher}
          feeder={feeder}
          subscribeFn={subscribeFeed}
          formRef={formRef}
        />
      </fetcher.Form>
      <h5>Subscribed feeds</h5>
      <span>(upcoming)</span>
    </div>
  );
};
