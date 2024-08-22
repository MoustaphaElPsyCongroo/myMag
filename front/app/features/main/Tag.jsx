import { useFetcher } from '@remix-run/react';
import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faThumbsUp, faThumbsDown } from '@fortawesome/free-regular-svg-icons';
import {
  faThumbsUp as likedSolid,
  faThumbsDown as dislikedSolid,
} from '@fortawesome/free-solid-svg-icons';

import styles from '~/styles/main/tag.css';

export const links = () => [{ rel: 'stylesheet', href: styles }];

/**
 * Tag component
 * @param {object} tag Object describing a tag
 * @param {object} likeDislikeData Object describing tag like/dislike counts
 * @returns
 */
export const Tag = ({ tag, likeDislikeData }) => {
  const [tagLiked, setTagLiked] = useState(false);
  const [tagDisliked, setTagDisliked] = useState(false);
  const fetcher = useFetcher();

  /**
   * Handles Click events on Like/Dislike buttons to add a bouncing animation.
   * @param {Event} e Click event
   */
  const handleClickTagLikeDislike = (e) => {
    const button = e.currentTarget;
    const icon = button.firstChild.firstChild;
    if (
      (icon.classList.contains('fa-thumbs-up') && !tagLiked) ||
      (icon.classList.contains('fa-thumbs-down') && !tagDisliked)
    ) {
      icon.classList.add('fa-bounce');
    }
    if (icon.classList.contains('fa-thumbs-up')) {
      setTagLiked((tagLiked) => !tagLiked);
    } else if (icon.classList.contains('fa-thumbs-down')) {
      setTagDisliked((articleDisliked) => !articleDisliked);
    }
    setTimeout(() => {
      icon.classList.remove('fa-bounce');
    }, 500);
  };

  let likeCount = null;
  let dislikeCount = null;
  if (likeDislikeData) {
    likeCount = likeDislikeData.like_count_from_user;
    dislikeCount = likeDislikeData.dislike_count_from_user;
  }
  if (fetcher.data) {
    likeCount = fetcher.data.like_count_from_user;
    dislikeCount = fetcher.data.dislike_count_from_user;
  }

  return (
    <div className="tag-container">
      <fetcher.Form method="post" action="/tags">
        <input type="hidden" name="id" value={tag.id} />
        <button
          type="submit"
          className="like-button"
          aria-label="Like this tag"
          name="_action"
          value={tagLiked ? 'like_tag' : 'unlike_tag'}
          onClick={handleClickTagLikeDislike}
        >
          <span className="fa-layers fa-fw">
            <FontAwesomeIcon
              icon={tagLiked ? likedSolid : faThumbsUp}
              className="like-icon like-tag-icon fa-xl"
              style={tagLiked && { color: '#bd001c' }}
            />
            {likeCount > 0 && (
              <span
                className="like-counter fa-layers-counter fa-layers-top-left fa-fade"
                style={{ backgroundColor: 'green' }}
              >
                {likeCount}
              </span>
            )}
          </span>
        </button>
        <span className="tag-name" style={{ display: 'inline-block' }}>
          {tag.name}
        </span>
        <button
          type="submit"
          className="dislike-button"
          aria-label="Dislike this tag"
          name="_action"
          value={tagDisliked ? 'dislike_tag' : 'undislike_tag'}
          onClick={handleClickTagLikeDislike}
        >
          <span className="fa-layers fa-fw">
            <FontAwesomeIcon
              icon={tagDisliked ? dislikedSolid : faThumbsDown}
              className="dislike-icon dislike-tag-icon fa-xl"
              style={tagDisliked && { color: '#bd001c' }}
            />
            {dislikeCount > 0 && (
              <span
                className="dislike-counter fa-layers-counter fa-layers-top-left fa-fade"
                style={{ backgroundColor: 'Tomato' }}
              >
                {dislikeCount}
              </span>
            )}
          </span>
        </button>
      </fetcher.Form>
    </div>
  );
};
