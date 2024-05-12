import { useState, useEffect } from 'react';

export const FeedSubscriber = ({ fetcher, feeder, subscribeFn, formRef }) => {
  const [feedList, setFeedList] = useState([]);
  const [fetcherStatus, setFetcherStatus] = useState(200);

  const hideFeedDropdown = () => {
    setFeedList([]);
    setFetcherStatus(200);
    formRef.current?.reset();
  };

  useEffect(() => {
    if (fetcher.data) {
      if (fetcher.data.status !== 404) {
        setFeedList([fetcher.data]);
        setFetcherStatus(200);
      } else {
        setFetcherStatus(404);
      }
    }
  }, [fetcher.data, formRef]);

  return (
    <>
      <input
        type="text"
        name="query_feed"
        placeholder="Paste a RSS/ATOM url"
        onBlur={hideFeedDropdown}
      />
      {feeder.state === 'submitting' ? <p>Subscribing...</p> : null}
      {feeder.data && feeder.data.name ? (
        <p>
          <em>Subscribed successfully to {feeder.data.name}</em>
        </p>
      ) : null}
      {feedList.length > 0 && (
        <div className="dropdown">
          <button className="dropbtn">Select the feed to subscribe to</button>
          {feedList.map((feed) => (
            <div
              key={feed.id}
              id="feedResults"
              className="dropdown dropdown-content show"
            >
              <div
                className="subscribe-button"
                aria-label="Subscribe to this feed"
                data-feed_id={feed.id}
                name="_action"
                value="subscribe_feed"
                onClick={subscribeFn}
              >
                <a href="#">
                  <div>
                    <h6 className="feed-result-title">{feed.name}</h6>
                    <p
                      dangerouslySetInnerHTML={{
                        __html: feed.description,
                      }}
                    />
                  </div>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
      {fetcherStatus === 404 ? (
        <div className="dropdown">
          <div id="feedResults" className="dropdown-content">
            <div>No results found</div>
          </div>
        </div>
      ) : null}
    </>
  );
};
