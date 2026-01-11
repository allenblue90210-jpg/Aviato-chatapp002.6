
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import TopBar from './TopBar';
import BottomNav from './BottomNav';
import { useAppContext } from '../../contexts/AppContext';

const Layout = () => {
  const location = useLocation();
  const { dataLoading } = useAppContext();
  const showTopBar = !location.pathname.startsWith('/profile');

  if (dataLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center relative overflow-hidden">
         <div className="animate-pulse flex flex-col items-center gap-6">
            <img 
              src="https://customer-assets.emergentagent.com/job_messaging-app-253/artifacts/55vxbv1v_aviato.png" 
              alt="Loading..." 
              className="w-24 h-24 object-contain"
            />
            <div className="flex flex-col items-center gap-2">
                <div className="h-1 w-24 bg-primary/20 rounded-full overflow-hidden">
                    <div className="h-full bg-primary animate-[loading_1.5s_ease-in-out_infinite]" style={{width: '50%'}}></div>
                </div>
                <p className="text-sm text-muted-foreground font-medium animate-pulse">Loading your experience...</p>
            </div>
         </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col max-w-md mx-auto shadow-2xl overflow-hidden relative border-x border-border">
      {showTopBar && <TopBar />}
      <main className="flex-1 overflow-y-auto pb-20 scrollbar-hide">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
};

export default Layout;
