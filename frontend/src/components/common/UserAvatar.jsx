
import React, { useState, useEffect } from 'react';
import { User } from 'lucide-react';

const UserAvatar = ({ src, alt, className, size = 24 }) => {
  const [imgSrc, setImgSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setImgSrc(src);
    setHasError(false);
  }, [src]);

  const handleError = () => {
    setHasError(true);
  };

  if (imgSrc && !hasError) {
    return (
      <img 
        src={imgSrc} 
        alt={alt} 
        className={`${className} object-cover`}
        onError={handleError}
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
