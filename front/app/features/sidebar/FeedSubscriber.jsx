import { useState, useEffect, useRef } from 'react';
import { useFetcher } from '@remix-run/react';

/**
 * FeedSubscriber component. Displays list of found feeds to subscribe to
 * @param {FetcherWithComponents} feedSearcher Fetcher of a form to search a feed
 * @param {array} subscribedFeeds All already subscribed feeds
 * @param {ref} formRef Ref to the feedSearcher form to easily blank it
 * @param {string} text Placeholder text of FeedSubscriber's form input
 * @returns
 */
export const FeedSubscriber = ({
  feedSearcher,
  subscribedFeeds,
  formRef,
  text,
}) => {
  const [feedList, setFeedList] = useState([]);
  const [feedSearcherStatus, setFeedSearcherStatus] = useState(200);
  const feedHandler = useFetcher();
  const feedListElemsRef = useRef(null);

  const subscribeFeed = (e) => {
    const feedId = e.currentTarget.dataset.feed_id;
    feedHandler.submit(
      {
        _action: 'subscribe_feed',
        id: feedId,
      },
      { method: 'post', action: '/feed' }
    );
    formRef.current?.reset();
  };

  const hideFeedDropdown = () => {
    // setFeedList([]);
    setFeedSearcherStatus(200);
    formRef.current?.reset();
  };

  const isAlreadySubscribed = (feedId) => {
    return subscribedFeeds.some((feed) => feed.id === feedId);
  };

  /**
   * Renders errors on fetching a feed
   * @returns
   */
  const renderFeedFetchErrors = () => {
    switch (feedSearcherStatus) {
      case 400:
        return <div>Invalid RSS feed: contact the creator of this feed</div>;
      case 404:
        return <div>No RSS feed with this url has been found</div>;
      case 410:
        return <div>This feed is permanently inactive</div>;
      default:
        return <div>Error fetching this feed URL</div>;
    }
  };

  useEffect(() => {
    if (feedSearcher.data) {
      if (feedSearcher.data.status >= 400) {
        setFeedSearcherStatus(feedSearcher.data.status);
      } else {
        setFeedList([feedSearcher.data.results]);
        setFeedSearcherStatus(200);
      }
    }
  }, [feedSearcher.data]);

  useEffect(() => {
    const handleClickOutsideFeedList = (e) => {
      if (
        feedListElemsRef.current &&
        !feedListElemsRef.current.contains(e.target)
      ) {
        setFeedList([]);
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('mousedown', handleClickOutsideFeedList);
    }
    return () => {
      window.removeEventListener('mousedown', handleClickOutsideFeedList);
    };
  }, [feedListElemsRef]);

  return (
    <>
      <input
        type="text"
        name="query_feed"
        placeholder={text}
        onBlur={hideFeedDropdown}
      />
      {feedHandler.state === 'submitting' ? <p>Subscribing...</p> : null}
      {feedHandler.data && feedHandler.data.results.name ? (
        <p>
          <em>Subscribed successfully to {feedHandler.data.results.name}</em>
        </p>
      ) : null}
      {feedList.length > 0 && (
        <div className="dropdown" ref={feedListElemsRef}>
          <button className="dropbtn">Select the feed to subscribe to</button>
          {feedList.map((feed) => (
            <div
              key={feed.id}
              id="feedResults"
              className={`dropdown dropdown-content show`}
            >
              <div
                className="subscribe-button"
                aria-label="Subscribe to this feed"
                data-feed_id={feed.id}
                name="_action"
                value="subscribe_feed"
                onClick={subscribeFeed}
              >
                <a href="#">
                  <div>
                    <h6 className="feed-result-title">{feed.name}</h6>
                    <img src={feed.banner_img} alt="feed banner" />
                    <p
                      dangerouslySetInnerHTML={{
                        __html: feed.description,
                      }}
                    />
                    {feedHandler.state !== 'idle' && <p>Subscribing...</p>}
                  </div>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
      {feedSearcherStatus >= 400 ? (
        <div className="dropdown">
          <div id="feedResults" className="dropdown-content">
            {renderFeedFetchErrors()}
          </div>
        </div>
      ) : null}
    </>
  );
};
