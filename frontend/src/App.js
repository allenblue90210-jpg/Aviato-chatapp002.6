
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import Layout from './components/layout/Layout';
import SignInPage from './pages/SignInPage';
import MatchPage from './pages/MatchPage';
import ChatListPage from './pages/ChatListPage';
import ChatPage from './pages/ChatPage';
import ReviewPage from './pages/ReviewPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import ProfileSetRegulationPage from './pages/ProfileSetRegulationPage';
import BlueModeSettings from './pages/modes/BlueModeSettings';
import YellowModeSettings from './pages/modes/YellowModeSettings';
import OrangeModeSettings from './pages/modes/OrangeModeSettings';
import GreenModeSettings from './pages/modes/GreenModeSettings';
import RedModeSettings from './pages/modes/RedModeSettings';
import GrayModeSettings from './pages/modes/GrayModeSettings';
// import BrownModeSettings from './pages/modes/BrownModeSettings'; // Feature Removed
import { Toaster } from './components/ui/toaster';
import RequireAuth from './components/common/RequireAuth';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/signin" element={<SignInPage />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }>
            <Route index element={<Navigate to="/match" replace />} />
            <Route path="match" element={<MatchPage />} />
            <Route path="chat" element={<ChatListPage />} />
            <Route path="chat/:userId" element={<ChatPage />} />
            <Route path="review" element={<ReviewPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />
            
            {/* Mode-specific routes */}
            <Route path="profile/modes" element={<ProfileSetRegulationPage />} />
            <Route path="profile/modes/blue" element={<BlueModeSettings />} />
            <Route path="profile/modes/yellow" element={<YellowModeSettings />} />
            <Route path="profile/modes/orange" element={<OrangeModeSettings />} />
            <Route path="profile/modes/green" element={<GreenModeSettings />} />
            <Route path="profile/modes/red" element={<RedModeSettings />} />
            <Route path="profile/modes/gray" element={<GrayModeSettings />} />
            {/* <Route path="profile/modes/brown" element={<BrownModeSettings />} /> Feature Removed */}
          </Route>
          
          {/* Catch all */}
          <Route path="*" element={<Navigate to="/match" replace />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
