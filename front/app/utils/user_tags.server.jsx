/**
 * Makes a user like a tag
 * @param {string} userId User id
 * @param {string} tagId Tag id
 * @returns Liked tag data
 */
export const likeTag = async (userId, tagId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/tags/liked`;
  const likeRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tag_id: tagId,
    }),
  });
  const likeStatus = likeRes.status;
  const likeData = await likeRes.json();
  return { likeData, likeStatus };
};

/**
 * Makes a user unlike a tag
 * @param {string} userId User id
 * @param {string} tagId Tag id
 * @returns Unliked tag data
 */
export const unlikeTag = async (userId, tagId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/tags/liked/${tagId}`;
  const unlikeRes = await fetch(url, { method: 'DELETE' });
  const unlikeStatus = unlikeRes.status;
  const unlikeData = await unlikeRes.json();
  return { unlikeData, unlikeStatus };
};

/**
 * Makes a user dislike a tag
 * @param {string} userId User id
 * @param {string} tagId Tag id
 * @returns Disliked tag data
 */
export const dislikeTag = async (userId, tagId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/tags/disliked`;
  const dislikeRes = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tag_id: tagId,
    }),
  });
  const dislikeStatus = dislikeRes.status;
  const dislikeData = await dislikeRes.json();

  return { dislikeData, dislikeStatus };
};

/**
 * Makes a user undislike a tag
 * @param {string} userId User id
 * @param {string} tagId Tag id
 * @returns Undisliked tag data
 */
export const undislikeTag = async (userId, tagId) => {
  const url = `${process.env.BACKEND_URL}/users/${userId}/tags/disliked/${tagId}`;
  const undislikeRes = await fetch(url, { method: 'DELETE' });
  const undislikeStatus = undislikeRes.status;
  const undislikeData = await undislikeRes.json();
  return { undislikeData, undislikeStatus };
};
