import { Form, useFetcher } from '@remix-run/react';
import { useEffect } from 'react';

import styles from '~/styles/sidebar/sidebar.css';

export const links = () => [
  { rel: 'stylesheet', href: styles }
];

export const Sidebar = () => {
  const fetcher = useFetcher();
  const feeder = useFetcher();

  const hideFeedDropdown = () => {
    const dropdowns = document.getElementsByClassName('dropdown');
    for (let i = 0; i < dropdowns.length; i++) {
      const openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  };

  const subscribeFeed = (e) => {
    const feedId = e.currentTarget.dataset.feed_id;
    feeder.submit({
      _action: 'subscribe_feed',
      id: feedId
    },
    { method: 'post', action: '/feed' });
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('click', hideFeedDropdown);
    }
  }, [hideFeedDropdown]);

  return (
    <div className='sidebar-container'>
      <fetcher.Form method='get' action='/feed'>
        <input type='text' name='query_feed' placeholder='Paste a RSS/ATOM url' />
        {feeder.state === 'submitting' ? <p>Subscribing...</p> : null}
        {feeder.data && feeder.data.name ? <p><em>Subscribed successfully to {feeder.data.name}</em></p> : null}
        {fetcher.data && fetcher.data.name
          ? (
            <div class='dropdown show'>
              <button className='dropbtn'>Select the feed to subscribe to</button>
              <div id='feedResults' class='dropdown-content show'>
                <div
                  className='subscribe-button'
                  aria-label='Subscribe to this feed'
                  data-feed_id={fetcher.data.id}
                  name='_action'
                  value='subscribe_feed'
                  onClick={subscribeFeed}
                >
                  <a href='#'>
                    <div>
                      <h6 className='feed-result-title'>{fetcher.data.name}</h6>
                      <p dangerouslySetInnerHTML={{ __html: fetcher.data.description }} />
                    </div>
                  </a>
                </div>
              </div>
            </div>
            )
          : null}
        {fetcher.data && !fetcher.data.name
          ? (
            <div class='dropdown show'>
              <div id='feedResults' class='dropdown-content'>
                <div>
                  No results found
                </div>
              </div>
            </div>
            )
          : null}
      </fetcher.Form>
      <h5>Subscribed feeds</h5>
      <span>(upcoming)</span>
    </div>
  );
}
;
