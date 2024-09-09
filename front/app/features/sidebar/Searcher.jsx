import { useFetcher } from '@remix-run/react';
import { useRef } from 'react';
import { FeedSubscriber } from './FeedSubscriber';

/**
 * Searcher component. Provides an input element to search for inputted feeds
 * (by rss url or general name) or articles (by url), adding them/subscribing
 * to them if not in database.
 * @param {string} type The type of element to search
 * @param {array} feeds All already subscribed feeds
 * @returns
 */
export const Searcher = ({ type, feeds }) => {
  const searcher = useFetcher(); // Will contain a form to search a feed
  const formRef = useRef(); // Ref as hook to easily blank the form on submit

  switch (type) {
    case 'feedUrl':
      return (
        <searcher.Form method="get" action="/feed" ref={formRef}>
          <FeedSubscriber
            feedSearcher={searcher}
            formRef={formRef}
            text="Paste a RSS/ATOM url"
            subscribedFeeds={feeds}
          />
        </searcher.Form>
      );
    case 'feedName':
      return (
        <searcher.Form method="get" action="/feed" ref={formRef}>
          <FeedSubscriber
            feedSearcher={searcher}
            formRef={formRef}
            text="Type the name/url of a website"
            subscribedFeeds={feeds}
          />
        </searcher.Form>
      );
    case 'articleUrl':
      return (
        <searcher.Form method="get" action="/feed" ref={formRef}>
          <FeedSubscriber
            feedSearcher={searcher}
            formRef={formRef}
            text="Paste an article URL"
            subscribedFeeds={feeds}
          />
        </searcher.Form>
      );
    default:
      return <p className="errorText">Searcher error: unsupported type prop</p>;
  }
};
