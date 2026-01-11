
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';

const RequireAuth = ({ children }) => {
  const { isAuthenticated, loading } = useAppContext();
  const location = useLocation();

  if (loading) {
      return <div className="min-h-screen flex items-center justify-center bg-background">Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect them to the /signin page, but save the current location they were
    // trying to go to when they were redirected. This allows us to send them
    // along to that page after they login, which is a nicer user experience.
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  return children;
};

export default RequireAuth;
