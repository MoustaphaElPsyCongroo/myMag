import { json, redirect } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';
import {
  dislikeTag,
  likeTag,
  undislikeTag,
  unlikeTag,
} from '../utils/user_tags.server';

export const loader = () => redirect('/');

/**
 * Handles /tags POST or DELETE requests
 * @param {Request} request POST or DELETE to /tags
 * @returns
 */
export const action = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/',
  });
  const userId = user.id;
  const formData = await request.formData();
  const { _action, ...values } = Object.fromEntries(formData);
  const articleId = values.id;

  // console.log(_action);

  switch (_action) {
    case 'like_tag': {
      const { likeData, likeStatus } = await likeTag(userId, articleId);
      return json({ status: likeStatus, results: likeData });
    }
    case 'unlike_tag': {
      const { unlikeData, unlikeStatus } = await unlikeTag(userId, articleId);
      return json({ status: unlikeStatus, results: unlikeData });
    }
    case 'dislike_tag': {
      const { dislikeData, dislikeStatus } = await dislikeTag(
        userId,
        articleId
      );
      return json({ status: dislikeStatus, results: dislikeData });
    }
    case 'undislike_tag': {
      const { undislikeData, undislikeStatus } = await undislikeTag(
        userId,
        articleId
      );
      return json({ status: undislikeStatus, results: undislikeData });
    }
  }
  throw json('Error: unknown Form', {
    status: 400,
    statusText: 'Error: unknown Form',
  });
};

/**
 * Prevents reloading the page on all tag actions
 */
export const shouldRevalidate = ({ actionResult, defaultShouldRevalidate }) => {
  if (actionResult) {
    return false;
  }
  return defaultShouldRevalidate;
};
