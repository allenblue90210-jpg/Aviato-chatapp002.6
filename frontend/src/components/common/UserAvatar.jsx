
import React from 'react';
import { User } from 'lucide-react';

const UserAvatar = ({ src, alt, className, size = 24 }) => {
  if (src) {
    return (
      <img 
        src={src} 
        alt={alt} 
        className={`${className} object-cover`}
      />
    );
  }

  return (
    <div className={`${className} bg-muted flex items-center justify-center`}>
      <User className="text-muted-foreground" size={size} />
    </div>
  );
};

export default UserAvatar;
