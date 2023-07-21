import { json } from '@remix-run/node';
import { authenticator } from '~/features/auth/auth.server';
import { searchFeed } from '~/utils/feeds.server';
import { subscribeFeed } from '../utils/feeds.server';

export const loader = async ({ request }) => {
  // const user = await authenticator.isAuthenticated(request, {
  //   failureRedirect: '/'
  // });

  const url = new URL(request.url);
  const search = new URLSearchParams(url.search);
  const feedUrl = search.get('query_feed');

  console.log('feed_url', feedUrl);

  const { feedData, feedStatus } = await searchFeed(feedUrl);
  return json(feedData);
};

export const action = async ({ request }) => {
  const user = await authenticator.isAuthenticated(request, {
    failureRedirect: '/'
  });
  const userId = user.id;
  const formData = await request.formData();
  const { _action, ...values } = Object.fromEntries(formData);
  const feedId = values.id;

  console.log(_action);

  switch (_action) {
    case 'subscribe_feed': {
      const { feedData, feedStatus } = await subscribeFeed(userId, feedId);
      if (feedStatus !== 200) {
        throw json(feedData.error, { status: feedStatus, statusText: feedData.error });
      }
      return json(feedData);
    }
  }
  throw json('Error: unknown Form', { status: 400, statusText: 'Error: unknown Form' });
};

// export const action = async ({ request }) => {
//   const user = await authenticator.isAuthenticated(request, {
//     failureRedirect: '/'
//   });
//   const userId = user.id;
//   const formData = await request.formData();
//   const { _action, ...values } = Object.fromEntries(formData);
//   const articleId = values.id;

//   console.log(_action);

//   switch (_action) {
//     case 'like_article': {
//       const { likeData, likeStatus } = await likeArticle(userId, articleId);
//       if (likeStatus !== 200) {
//         throw json(likeData.error, { status: likeStatus, statusText: likeData.error });
//       }
//       return json(likeData);
//     }
//     case 'unlike_article': {
//       const { unlikeData, unlikeStatus } = await unlikeArticle(userId, articleId);
//       if (unlikeStatus !== 200) {
//         throw json(unlikeData.error, { status: unlikeStatus, statusText: unlikeData.error });
//       }
//       return json(unlikeData);
//     }
//     case 'dislike_article': {
//       const { dislikeData, dislikeStatus } = await dislikeArticle(userId, articleId);
//       if (dislikeStatus !== 200) {
//         throw json(dislikeData.error, { status: dislikeStatus, statusText: dislikeData.error });
//       }
//       return json(dislikeData);
//     }
//     case 'undislike_article': {
//       const { undislikeData, undislikeStatus } = await undislikeArticle(userId, articleId);
//       if (undislikeStatus !== 200) {
//         throw json(undislikeData.error, { status: undislikeStatus, statusText: undislikeData.error });
//       }
//       return json(undislikeData);
//     }
//     case 'read_article': {
//       const { readData, readStatus } = await readArticle(userId, articleId);
//       if (readStatus !== 200) {
//         throw json(readData.error, { status: readStatus, statusText: readData.error });
//       }
//       return json(readData);
//     }
//   }
//   throw json('Error: unknown Form', { status: 400, statusText: 'Error: unknown Form' });
// };

// TODO: Handle and render action errors here
// export const CatchBoundary = () => {
// }
