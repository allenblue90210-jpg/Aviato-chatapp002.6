import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { Settings, Camera, Edit2, Plus } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import ModeCard from '../components/profile/ModeCard';
import ModeSettingsDialog from '../components/profile/ModeSettingsDialog';
import ProfilePicDialog from '../components/profile/ProfilePicDialog';
import CategorySelector from '../components/availability/CategorySelector';
import { AvailabilityMode } from '../data/mockData';
import { useTranslation } from 'react-i18next';

import UserAvatar from '../components/common/UserAvatar';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { currentUser, isAuthenticated, setAvailabilityMode, showToast, updateUserSelections, updateUserProfile } = useAppContext();

  
  // State for modals
  const [deactivateMode, setDeactivateMode] = useState(null);
  const [settingsMode, setSettingsMode] = useState(null);
  const [isProfilePicOpen, setIsProfilePicOpen] = useState(false);
  const [confirmRedMode, setConfirmRedMode] = useState(false);
  const [isInterestsOpen, setIsInterestsOpen] = useState(false);
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/signin');
    }
  }, [isAuthenticated, navigate]);
  
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">{t('profile.loading')}</p>
        </div>
      </div>
    );
  }

  const currentMode = currentUser.availabilityMode;

  const handleInterestsApply = (newSelections) => {
    updateUserSelections(newSelections);
  };

  const modes = [
    {
      mode: AvailabilityMode.GREEN,
      icon: '🟢',
      name: t('mode.green.name'),
      description: t('mode.green.desc'),
      color: '#10B981'
    },
    {
      mode: AvailabilityMode.BLUE,
      icon: '🔵',
      name: t('mode.blue.name'),
      description: t('mode.blue.desc'),
      color: '#0066FF'
    },
    {
      mode: AvailabilityMode.YELLOW,
      icon: '🟡',
      name: t('mode.yellow.name'),
      description: t('mode.yellow.desc'),
      color: '#FBBF24'
    },
    {
      mode: AvailabilityMode.ORANGE,
      icon: '🟠',
      name: t('mode.orange.name'),
      description: t('mode.orange.desc'),
      color: '#F97316'
    },
    {
      mode: AvailabilityMode.RED,
      icon: '🔴',
      name: t('mode.red.name'),
      description: t('mode.red.desc'),
      color: '#DC2626'
    },
    {
      mode: AvailabilityMode.GRAY,
      icon: '⚪',
      name: t('mode.gray.name'),
      description: t('mode.gray.desc'),
      color: '#9CA3AF'
    }
  ];

  const getModeName = (mode) => {
    const found = modes.find(m => m.mode === mode);
    return found ? found.name : 'Unknown Mode';
  };

  const handleToggle = (mode, checked) => {
    if (checked) {
      // Activating Logic
      const needsSettings = [
        AvailabilityMode.BLUE,
        AvailabilityMode.YELLOW,
        AvailabilityMode.ORANGE,
        AvailabilityMode.BROWN
      ].includes(mode);

      if (needsSettings) {
        setSettingsMode(mode);
      } else if (mode === AvailabilityMode.RED) {
        setConfirmRedMode(true);
      } else {
        // Green or Gray - Activate immediately
        setAvailabilityMode(mode, { suppressToast: true });
        
        if (mode === AvailabilityMode.GREEN) {
           showToast(t('mode.toast_active', { mode: t('mode.green.name') }), 'success');
        } else {
           showToast(t('mode.toast_active', { mode: getModeName(mode) }), 'success');
        }
      }
    } else {
      // Deactivating Logic
      setDeactivateMode(mode);
    }
  };

  const confirmDeactivate = () => {
    if (deactivateMode) {
      setAvailabilityMode(null); // Set to Invisible (null)
      showToast(t('mode.toast_inactive', { mode: getModeName(deactivateMode) }), 'success');
      setDeactivateMode(null);
    }
  };

  const handleProfileUpdate = (newUrl, newName, newLocation) => {
    const updates = {};
    // Always update profilePic (it can be null if removed)
    updates.profilePic = newUrl; 
    
    if (newName) updates.name = newName;
    if (newLocation) updates.location = newLocation;
    
    updateUserProfile(updates);
  };

  const handleEdit = (mode) => {
    setSettingsMode(mode);
  };

  // Helper function to get settings text for active mode
  const getActiveSettings = (mode) => {
    if (currentUser.availabilityMode !== mode) return undefined;

    switch(mode) {
      case AvailabilityMode.BLUE:
        return currentUser.availability.openDate 
          ? `Opens ${new Date(currentUser.availability.openDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
          : undefined;
      
      case AvailabilityMode.YELLOW:
        if (currentUser.availability.laterStartTime) {
            const elapsed = Math.floor((Date.now() - currentUser.availability.laterStartTime) / 60000);
            const remaining = Math.max(0, currentUser.availability.laterMinutes - elapsed);
            return t('mode.yellow.expires_in', { minutes: remaining });
        }
        return currentUser.availability.laterMinutes 
          ? t('mode.yellow.expires_in', { minutes: currentUser.availability.laterMinutes })
          : undefined;
      
      case AvailabilityMode.ORANGE:
        return t('mode.orange.slots', { current: currentUser.availability.currentContacts, max: currentUser.availability.maxContact });
      
      case AvailabilityMode.BROWN:
        return currentUser.availability.timedHour !== null
          ? t('mode.brown.opens_at', { time: formatTime(currentUser.availability.timedHour, currentUser.availability.timedMinute || 0) })
          : undefined;
      
      case AvailabilityMode.GREEN:
        return t('mode.green.settings');
      
      case AvailabilityMode.RED:
        return t('mode.red.settings');
      
      case AvailabilityMode.GRAY:
        return t('mode.gray.settings');
      
      default:
        return undefined;
    }
  };

  const formatTime = (hour, minute) => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    const displayMinute = minute.toString().padStart(2, '0');
    return `${displayHour}:${displayMinute} ${period}`;
  };

  // Helper for mode colors/emojis
  function getModeColor(mode) {
    const colors = {
      blue: '#0066FF',
      yellow: '#FBBF24',
      orange: '#F97316',
      green: '#10B981',
      red: '#DC2626',
      gray: '#9CA3AF',
      brown: '#92400E'
    };
    return colors[mode] || '#10B981';
  }

  function getModeEmoji(mode) {
    const emojis = {
      blue: '🔵',
      yellow: '🟡',
      orange: '🟠',
      green: '🟢',
      red: '🔴',
      gray: '⚪',
      brown: '🟤'
    };
    return emojis[mode] || '🟢';
  }

  return (
    <div className="min-h-screen bg-background pb-32">
      {/* Top Bar */}
      <div className="bg-card p-4 sticky top-0 border-b border-border z-10 flex items-center justify-center">
        <h1 className="text-xl font-bold text-foreground">{t('profile.title')}</h1>
      </div>

      <div className="p-4 space-y-6">
        {/* Profile Info */}
        <div className="flex flex-col items-center py-4">
          <div className="relative">
            <UserAvatar 
              src={currentUser.profilePic} 
              alt="Profile" 
              className="w-28 h-28 rounded-full border-4 border-card shadow-md" 
              size={48}
            />
            <div 
              className="absolute bottom-0 right-0 bg-card rounded-full p-2 cursor-pointer shadow-md border border-border hover:bg-accent transition-colors"
              onClick={() => setIsProfilePicOpen(true)}
            >
              <Camera className="w-4 h-4 text-muted-foreground" />
            </div>
          </div>
          <div className="flex items-center gap-2 mt-4 justify-center">
            <h2 className="text-2xl font-bold text-foreground">{currentUser.name}</h2>
          </div>
          <div className="flex items-center justify-center gap-2 text-muted-foreground mt-1 cursor-pointer group" onClick={() => setIsProfilePicOpen(true)}>
             <span>{currentUser.location || 'San Francisco, CA'}</span>
             <Edit2 className="w-3 h-3 opacity-50 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        {/* My Vibe / Interests Section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-lg text-foreground">{t('profile.vibe')} ({currentUser.selections?.length || 0}/5)</h3>
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-primary hover:text-primary/90 p-0 h-auto font-medium"
              onClick={() => setIsInterestsOpen(true)}
            >
              {currentUser.selections?.length > 0 ? t('profile.edit') : t('profile.add')}
            </Button>
          </div>
          
          <div 
            className="bg-card border border-border rounded-xl p-4 shadow-sm min-h-[80px] cursor-pointer hover:border-primary/50 transition-colors"
            onClick={() => setIsInterestsOpen(true)}
          >
            {currentUser.selections?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {currentUser.selections.map((interest) => (
                  <Badge 
                    key={interest} 
                    variant="secondary" 
                    className="bg-primary/10 text-primary hover:bg-primary/20 border-primary/20 px-3 py-1"
                  >
                    {interest}
                  </Badge>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-2 text-muted-foreground gap-2">
                <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                  <Plus className="w-5 h-5" />
                </div>
                <span className="text-sm">{t('profile.add_interests')}</span>
              </div>
            )}
          </div>
        </div>

        {/* Profile Set Regulation */}
        <div>
          <h3 className="font-bold text-lg text-foreground mb-2">{t('profile.regulation')}</h3>
          
          {/* VISIBILITY STATUS BANNER */}
          <div className="mb-6 bg-card border border-border rounded-xl overflow-hidden shadow-sm">
            <div className="bg-muted px-4 py-2 border-b border-border">
              <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{t('profile.visibility')}</h4>
            </div>
            
            {currentMode ? (
               <div className="p-4 flex items-center gap-3 bg-card">
                 <div 
                   className="w-10 h-10 rounded-full flex items-center justify-center text-xl"
                   style={{ backgroundColor: getModeColor(currentMode) + '20' }}
                 >
                   {getModeEmoji(currentMode)}
                 </div>
                 <div>
                   <div className="font-bold text-foreground">{getModeName(currentMode)} - {t('profile.active')}</div>
                   <div className="text-sm text-green-600 font-medium">{getActiveSettings(currentMode) || t('profile.active')}</div>
                 </div>
               </div>
            ) : (
               <div className="p-4 bg-card">
                 <div className="flex items-center gap-3 mb-2">
                   <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-xl">
                     👻
                   </div>
                   <div>
                     <div className="font-bold text-foreground">{t('mode.invisible.name')} - {t('profile.active')}</div>
                     <div className="text-xs text-muted-foreground">{t('profile.default_state')}</div>
                   </div>
                 </div>
                 <p className="text-sm text-muted-foreground leading-relaxed">
                   {t('profile.invisible_desc')}
                 </p>
               </div>
            )}
          </div>
          
          <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">{t('profile.select_mode')}</h4>
          
          <div className="space-y-3">
            {modes.map((modeData) => (
              <ModeCard
                key={modeData.mode}
                mode={modeData.mode}
                icon={modeData.icon}
                name={modeData.name}
                description={modeData.description}
                color={modeData.color}
                isActive={currentUser.availabilityMode === modeData.mode}
                settings={getActiveSettings(modeData.mode)}
                onToggle={handleToggle}
                onEdit={handleEdit}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      <ModeSettingsDialog 
         mode={settingsMode}
         isOpen={!!settingsMode}
         onClose={() => setSettingsMode(null)}
      />

      {/* Interests Selector Modal */}
      <CategorySelector
        isOpen={isInterestsOpen}
        onClose={setIsInterestsOpen}
        currentSelected={currentUser.selections || []}
        onApply={handleInterestsApply}
        maxSelections={5}
        title={`${t('profile.vibe')} (Max 5)`}
      />

      {/* Red Mode Confirmation */}
      <AlertDialog open={confirmRedMode} onOpenChange={setConfirmRedMode}>
        <AlertDialogContent className="max-w-[90vw] w-full rounded-xl bg-card border-border">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-foreground">⚠️ {t('mode.red.confirm_title')}</AlertDialogTitle>
            <AlertDialogDescription className="text-muted-foreground">
              {t('mode.red.confirm_desc')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-row gap-2 justify-end">
            <AlertDialogCancel className="mt-0 flex-1 bg-muted text-muted-foreground hover:bg-accent border-border">{t('common.cancel')}</AlertDialogCancel>
            <AlertDialogAction 
              onClick={() => {
                setAvailabilityMode(AvailabilityMode.RED, { suppressToast: true });
                showToast(t('mode.toast_active', { mode: t('mode.red.name') }), 'success');
                setConfirmRedMode(false);
              }} 
              className="bg-destructive hover:bg-destructive/90 text-destructive-foreground flex-1"
            >
              {t('mode.red.action')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Deactivate Confirmation */}
      <AlertDialog open={!!deactivateMode} onOpenChange={(open) => !open && setDeactivateMode(null)}>
        <AlertDialogContent className="max-w-[90vw] w-full rounded-xl bg-card border-border">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-foreground">{t('mode.deactivate_title', { mode: deactivateMode && getModeName(deactivateMode) })}</AlertDialogTitle>
            <AlertDialogDescription className="text-muted-foreground">
              {t('mode.deactivate_desc')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-row gap-2 justify-end">
            <AlertDialogCancel className="mt-0 flex-1 bg-muted text-muted-foreground hover:bg-accent border-border">{t('common.cancel')}</AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmDeactivate} 
              className="bg-destructive hover:bg-destructive/90 text-destructive-foreground flex-1"
            >
              {t('mode.deactivate_action')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      {/* Profile Pic Dialog - Now Edit Profile Dialog */}
      <ProfilePicDialog 
        isOpen={isProfilePicOpen}
        onClose={() => setIsProfilePicOpen(false)}
        currentPic={currentUser.profilePic}
        currentName={currentUser.name}
        currentLocation={currentUser.location}
        onSave={handleProfileUpdate}
      />
    </div>
  );
}
