export const searchFeed = async (feedUrl) => {
  const url = `${process.env.BACKEND_URL}/feeds`;
  const feedRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      link: feedUrl
    })
  });
  const feedStatus = feedRes.status;
  const feedData = await feedRes.json();
  return { feedData, feedStatus };
};

export const subscribeFeed = async (userId, feedId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/feeds`;
  const feedRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      feed_id: feedId
    })
  });
  const feedStatus = feedRes.status;
  const feedData = await feedRes.json();
  return { feedData, feedStatus };
};
