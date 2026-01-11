import React from 'react';
import { MessageSquare, Search, Star, User, Settings } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const BottomNav = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const isActive = (path) => location.pathname === path || location.pathname.startsWith(`${path}/`);
  
  const ChatIcon = ({ className }) => (
    <img 
      src="https://customer-assets.emergentagent.com/job_chat-messenger-306/artifacts/q0vg3vgc_messenger-icon-messenger-social-media-logo-free-png.webp" 
      alt="Chat"
      className={className.replace('w-5 h-5', 'w-6 h-6')} // Slightly larger than default
      style={{ objectFit: 'contain' }}
    />
  );

  const MixtapeIcon = ({ className }) => (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      className={className}
    >
      <rect width="20" height="16" x="2" y="4" rx="2" />
      <path d="M6 8h12" />
      <path d="M20 12h-2" />
      <path d="M4 12h2" />
      <circle cx="8" cy="14" r="2" />
      <path d="M16 14h.01" />
      <path d="M16 14h.01" />
      <circle cx="16" cy="14" r="2" />
    </svg>
  );

  const WhistleIcon = ({ className }) => (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      className={className}
    >
      <path d="M11 3a8 8 0 0 1 8 8v7a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-1a2 2 0 0 0-2-2H8a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3Z" />
      <path d="M2.5 10a4.5 4.5 0 0 1 7-4.5" />
    </svg>
  );

  const navItems = [
    { id: 'chat', icon: ChatIcon, label: t('nav.chat'), path: '/chat' },
    { id: 'match', icon: MixtapeIcon, label: t('nav.match'), path: '/match' },
    { id: 'review', icon: WhistleIcon, label: t('nav.review'), path: '/review' },
    { id: 'profile', icon: User, label: t('nav.profile'), path: '/profile' },
    { id: 'settings', icon: Settings, label: t('nav.settings'), path: '/settings' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-card border-t border-border pb-safe pt-2 px-4 z-50">
      <div className="flex justify-around items-center max-w-md mx-auto">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => navigate(item.path)}
            className={`flex flex-col items-center p-2 min-w-[56px] transition-colors ${
              isActive(item.path) 
                ? 'text-primary' 
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <item.icon className={`w-5 h-5 mb-1 ${isActive(item.path) ? 'stroke-2' : 'stroke-1'}`} />
            <span className="text-[10px] font-medium">{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default BottomNav;
