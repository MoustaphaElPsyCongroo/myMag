import { json, redirect } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';
import { dislikeTag, likeTag, undislikeTag, unlikeTag } from '../utils/user_tags.server';

export const loader = () => redirect('/');

export const action = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/'
  });
  const userId = user.id;
  const formData = await request.formData();
  const { _action, ...values } = Object.fromEntries(formData);
  const articleId = values.id;

  console.log(_action);

  switch (_action) {
    case 'like_tag': {
      const { likeData, likeStatus } = await likeTag(userId, articleId);
      if (likeStatus !== 200) {
        throw json(likeData.error, { status: likeStatus, statusText: likeData.error });
      }
      return json(likeData);
    }
    case 'unlike_tag': {
      const { unlikeData, unlikeStatus } = await unlikeTag(userId, articleId);
      if (unlikeStatus !== 200) {
        throw json(unlikeData.error, { status: unlikeStatus, statusText: unlikeData.error });
      }
      return json(unlikeData);
    }
    case 'dislike_tag': {
      const { dislikeData, dislikeStatus } = await dislikeTag(userId, articleId);
      if (dislikeStatus !== 200) {
        throw json(dislikeData.error, { status: dislikeStatus, statusText: dislikeData.error });
      }
      return json(dislikeData);
    }
    case 'undislike_tag': {
      const { undislikeData, undislikeStatus } = await undislikeTag(userId, articleId);
      if (undislikeStatus !== 200) {
        throw json(undislikeData.error, { status: undislikeStatus, statusText: undislikeData.error });
      }
      return json(undislikeData);
    }
  }
  throw json('Error: unknown Form', { status: 400, statusText: 'Error: unknown Form' });
};

export const shouldRevalidate = ({ actionResult, defaultShouldRevalidate }) => {
  if (actionResult) {
    return false;
  }
  return defaultShouldRevalidate;
};
