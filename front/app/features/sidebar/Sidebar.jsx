import { Searcher } from './Searcher';
import { TabList } from '../utilityComponents/TabList';
import { TabItem } from '../utilityComponents/TabItem';

import styles from '~/styles/sidebar/sidebar.css';
import { useRouteLoaderData } from '@remix-run/react';

export const links = () => [{ rel: 'stylesheet', href: styles }];

/**
 * Sidebar component
 * @returns
 */
export const Sidebar = ({ feeds }) => {
  const articlesData = useRouteLoaderData('routes/articles');
  const unreadArticlesCount = articlesData?.total;

  /**
   * Renders subscribed feeds
   * @returns
   */
  const renderSubscribedFeeds = (feedsStatus, results) => {
    if (feedsStatus >= 400) {
      const errorMessage = results.error.split(': ')[1];
      return (
        <p className="errorText">
          `Error getting the list of subscribed feeds: ${errorMessage}`
        </p>
      );
    }

    return results.map((feed) => (
      <li key={feed.id} className="subscribed_feeds-item">
        {/* <img src={feed.icon} alt="Feed favicon" /> */}
        {feed.name}
      </li>
    ));
  };

  return (
    // TODO: Feedsearcher currently only searches by precise URL. (/feed expects
    // a url). Add keyword search (Le Monde pour trouver lemonde.fr rss avec
    // la librarie feedsearch) et article search/add, probablement dans un
    // système d'onglets: quand l'onglet est sélectionné, le feedSearcher.Form
    // correspondant sera activé. Probabkement diviser encore donc ce component
    // en un grand component (FeedFinder? Ou SidebarSearcher? ugh.
    // SidebarSearcher aura l'avantage de pouvoir ensuite mettre un if, pour
    // utiliser feedSearcher.form ou articleSearcher.form ptêtre. Donc
    // peut-être même l'appeler juste Searcher, déclinable en plein de types
    // selon une prop 'type=')
    <nav className="sidebar-container" aria-label="sidebar-navigator">
      <h2>
        {unreadArticlesCount === 0 ? 'No' : unreadArticlesCount} new articles
      </h2>
      <h3>Add new feeds or articles</h3>
      <TabList
        tabs={[
          <TabItem key="feedUrl" label="by RSS or ATOM URL" id="feedUrl0">
            <Searcher
              type="feedUrl"
              feeds={feeds.status < 400 ? feeds.results : []}
            />
          </TabItem>,
          <TabItem key="feedName" label="by website name" id="feedName0">
            <Searcher
              type="feedName"
              feeds={feeds.status < 400 ? feeds.results : []}
            />
          </TabItem>,
          <TabItem key="articleUrl" label="by article URL" id="articleUrl0">
            <Searcher
              type="articleUrl"
              feeds={feeds.status < 400 ? feeds.results : []}
            />
          </TabItem>,
        ]}
      />
      <h5>Subscribed feeds</h5>
      <ul className="sidebar-subscribed_feeds">
        {renderSubscribedFeeds(feeds.status, feeds.results)}
      </ul>
    </nav>
  );
};
