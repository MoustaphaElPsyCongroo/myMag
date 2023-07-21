export const likeArticle = async (userId, articleId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/articles/liked`;
  const likeRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      article_id: articleId
    })
  });
  const likeStatus = likeRes.status;
  const likeData = await likeRes.json();
  return { likeData, likeStatus };
};

export const unlikeArticle = async (userId, articleId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/articles/liked/${articleId}`;
  const unlikeRes = await fetch(url, { method: 'DELETE' });
  const unlikeStatus = unlikeRes.status;
  const unlikeData = await unlikeRes.json();
  return { unlikeData, unlikeStatus };
};

export const dislikeArticle = async (userId, articleId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/articles/disliked`;
  const dislikeRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      article_id: articleId
    })
  });
  const dislikeStatus = dislikeRes.status;
  const dislikeData = await dislikeRes.json();

  return { dislikeData, dislikeStatus };
};

export const undislikeArticle = async (userId, articleId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/articles/disliked/${articleId}`;
  const undislikeRes = await fetch(url, { method: 'DELETE' });
  const undislikeStatus = undislikeRes.status;
  const undislikeData = await undislikeRes.json();
  return { undislikeData, undislikeStatus };
};

export const readArticle = async (userId, articleId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/articles/read/`;
  const readRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      article_id: articleId
    })
  });
  const readStatus = readRes.status;
  const readData = await readRes.json();
  return { readData, readStatus };
};
