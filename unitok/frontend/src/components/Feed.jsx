import './Feed.css';
import Post from './Post';

const Feed = ({ posts }) => {
  if (!posts || posts.length === 0) {
    return (
      <div className="empty-feed">
        <h2>No posts yet!</h2>
        <p>Be the first to share your unicorn adventures.</p>
      </div>
    );
  }

  return (
    <div className="feed">
      {posts.map(post => (
        <Post key={post.postId} post={post} />
      ))}
    </div>
  );
};

export default Feed;
