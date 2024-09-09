/**
 * Searches a feed from the database (API imports it if absent)
 * @param {string} feedUrl
 * @returns Feed data
 */
export const getOrImportFeedFromURL = async (feedUrl) => {
  const url = `${process.env.BACKEND_URL}/feeds`;
  const feedRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      link: feedUrl,
    }),
  });
  const feedStatus = feedRes.status;
  const feedData = await feedRes.json();
  return { feedData, feedStatus };
};

/**
 * Subscribes a user to a feed
 * @param {string} userId User id
 * @param {string} feedId Feed id
 * @returns Subscribed feed data
 */
export const subscribeFeed = async (userId, feedId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/feeds`;
  const feedRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      feed_id: feedId,
    }),
  });
  const feedStatus = feedRes.status;
  const feedData = await feedRes.json();
  return { feedData, feedStatus };
};

/**
 *
 * @param {string} userId User id
 * @returns Subscribed feeds list
 */
export const getUserFeeds = async (userId) => {
  const feedsRes = await fetch(
    `${process.env.BACKEND_URL}/users/${userId}/feeds`
  );
  const feedsStatus = feedsRes.status;
  const feedsData = await feedsRes.json();
  return { feedsData, feedsStatus };
};
