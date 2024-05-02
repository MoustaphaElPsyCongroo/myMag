import { Link, useFetcher } from '@remix-run/react';
import { useEffect, useState, useRef } from 'react';
import { ClientOnly } from 'remix-utils';
import { useInView } from 'react-intersection-observer';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faThumbsUp, faThumbsDown } from '@fortawesome/free-regular-svg-icons';
import {
  faThumbsUp as likedSolid,
  faThumbsDown as dislikedSolid,
} from '@fortawesome/free-solid-svg-icons';

import TimeAgo from 'javascript-time-ago';
import ReactTimeAgo from 'react-time-ago';
import en from 'javascript-time-ago/locale/en.json';

import styles from '~/styles/main/article.css';
import { Tag, links as tagLinks } from './Tag';

TimeAgo.addDefaultLocale(en);

export const links = () => [{ rel: 'stylesheet', href: styles }, ...tagLinks()];

export const Article = ({ article }) => {
  const [articleLiked, setArticleLiked] = useState(article.liked);
  const [articleDisliked, setArticleDisliked] = useState(article.disliked);
  const [articleRead, setArticleRead] = useState(false);
  const articleReadRef = useRef(articleRead);
  const { ref, inView, entry } = useInView();
  const fetcher = useFetcher();

  const markAsReadOnScroll = () => {
    if (inView && !articleReadRef.current) {
      const bodyTop = document.body.getBoundingClientRect().top;
      const articleTop = entry.target.getBoundingClientRect().top;
      const articleOffset = articleTop - bodyTop;
      const documentHeight = document.body.scrollHeight;
      const scrollY = window.scrollY;
      const almostAtBottom =
        550 + entry.target.offsetHeight + scrollY > documentHeight;

      if (
        !articleRead &&
        fetcher.state !== 'submitting' &&
        (scrollY > articleOffset || almostAtBottom)
      ) {
        const articleId = entry.target.dataset.id;
        // console.log(articleReadRef.current);
        // console.log('marking as read:', entry.target.dataset.title);
        entry.target.classList.add('article-read');
        setArticleRead(true);
        fetcher.submit(
          {
            _action: 'read_article',
            id: articleId,
          },
          { method: 'post' }
        );
      }
    }
  };

  const markAsReadOnClick = () => {
    const articleId = article.id;
    if (!articleRead) {
      entry.target.classList.add('article-read');
      setArticleRead(true);
      fetcher.submit(
        {
          _action: 'read_article',
          id: articleId,
        },
        { method: 'post' }
      );
    }
  };

  // TODO: Add handling of thrown errors on form submit
  const handleClickLikeDislike = (e) => {
    const button = e.currentTarget;
    const icon = button.firstChild;
    if (
      (icon.classList.contains('fa-thumbs-up') && !articleLiked) ||
      (icon.classList.contains('fa-thumbs-down') && !articleDisliked)
    ) {
      icon.classList.add('fa-bounce');
    }
    if (icon.classList.contains('fa-thumbs-up')) {
      setArticleLiked(!articleLiked);
      if (articleDisliked) {
        setArticleDisliked(false);
      }
    } else if (icon.classList.contains('fa-thumbs-down')) {
      setArticleDisliked(!articleDisliked);
      if (articleLiked) {
        setArticleLiked(false);
      }
    }
    setTimeout(() => {
      icon.classList.remove('fa-bounce');
    }, 500);
  };

  useEffect(() => {
    articleReadRef.current = articleRead;
    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', markAsReadOnScroll);
    }

    return () => {
      window.removeEventListener('scroll', markAsReadOnScroll);
    };
  });

  return (
    <div
      className="article"
      ref={ref}
      data-id={article.id}
      data-title={article.title}
    >
      <Link
        className="article-link"
        to={article.link}
        target="_blank"
        onClick={markAsReadOnClick}
      >
        <h3 className="article-title">{article.title}</h3>
        <p>{article.feed_name}</p>
        {article.image && (
          <img
            className="article-image"
            src={article.image}
            alt="article image"
          />
        )}
        <p className="article-description">{article.description}</p>
        <ClientOnly fallback={<DatingFallback date={article.publish_date} />}>
          {() => <Dating article={article} />}
        </ClientOnly>
      </Link>
      <h4 className="article-tag-title">Categories and Keywords</h4>
      <ClientOnly fallback={<p>Loading...</p>}>
        {() =>
          article.tags.map((tag) => {
            return (
              <Tag
                key={tag.id}
                tag={tag}
                likeDislikeData={fetcher.data && fetcher.data[tag.id]}
              />
            );
          })
        }
      </ClientOnly>
      <fetcher.Form method="post" action="/articles">
        <input type="hidden" name="id" value={article.id} />
        <button
          type="submit"
          className="like-button"
          aria-label="Like this article"
          name="_action"
          value={articleLiked ? 'like_article' : 'unlike_article'}
          onClick={handleClickLikeDislike}
        >
          <ClientOnly fallback={<p>Like</p>}>
            {() => (
              <FontAwesomeIcon
                icon={articleLiked ? likedSolid : faThumbsUp}
                className="like-icon fa-2xl"
                style={articleLiked && { color: '#bd001c' }}
              />
            )}
          </ClientOnly>
        </button>
        <button
          type="submit"
          className="dislike-button"
          aria-label="Dislike this article"
          name="_action"
          value={articleDisliked ? 'dislike_article' : 'undislike_article'}
          onClick={handleClickLikeDislike}
        >
          <ClientOnly fallback={<p>Dislike</p>}>
            {() => (
              <FontAwesomeIcon
                icon={articleDisliked ? dislikedSolid : faThumbsDown}
                className="dislike-icon fa-2xl"
                style={articleDisliked && { color: '#bd001c' }}
              />
            )}
          </ClientOnly>
        </button>
      </fetcher.Form>
    </div>
  );
};

export const Dating = ({ article }) => {
  const date = new Date(article.publish_date);

  return <ReactTimeAgo date={date} locale="en-US" timeStyle="twitter" />;
};

export const DatingFallback = ({ date }) => <p>{date}</p>;
