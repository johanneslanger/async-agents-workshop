import { FaHeart, FaHorse } from 'react-icons/fa';
import './Post.css';

const Post = ({ post }) => {
  const { content, author, timestamp, likes, unicornColor } = post;
  
  // Format the timestamp
  const formattedDate = new Date(timestamp).toLocaleString();
  
  // Get unicorn color style
  const getUnicornColorStyle = (color) => {
    const colorMap = {
      'pink': '#FF69B4',
      'blue': '#1E90FF',
      'purple': '#9370DB',
      'green': '#3CB371',
      'yellow': '#FFD700',
      'rainbow': 'linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet)'
    };
    
    return colorMap[color.toLowerCase()] || colorMap.rainbow;
  };
  
  const unicornStyle = {
    color: unicornColor !== 'rainbow' ? getUnicornColorStyle(unicornColor) : undefined,
    background: unicornColor === 'rainbow' ? getUnicornColorStyle('rainbow') : undefined,
    WebkitBackgroundClip: unicornColor === 'rainbow' ? 'text' : undefined,
    WebkitTextFillColor: unicornColor === 'rainbow' ? 'transparent' : undefined
  };

  return (
    <div className="post">
      <div className="post-header">
        <div className="post-author">
          <FaHorse className="author-icon" style={unicornStyle} />
          <span>{author}</span>
        </div>
        <div className="post-time">{formattedDate}</div>
      </div>
      
      <div className="post-content">{content}</div>
      
      <div className="post-footer">
        <div className="post-likes">
          <FaHeart className="like-icon" />
          <span>{likes}</span>
        </div>
        <div className="post-unicorn-color">
          <span className="color-label">Unicorn Color:</span>
          <span className="color-value" style={unicornStyle}>{unicornColor}</span>
        </div>
      </div>
    </div>
  );
};

export default Post;
