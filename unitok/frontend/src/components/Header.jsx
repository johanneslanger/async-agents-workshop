import { FaHorse } from 'react-icons/fa';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <FaHorse className="logo-icon" />
          <h1>UniTok</h1>
        </div>
        <div className="tagline">
          Where Magical Unicorns Share Their Sparkle
        </div>
      </div>
    </header>
  );
};

export default Header;
