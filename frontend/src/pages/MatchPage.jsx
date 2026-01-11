import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { 
  MessageSquare, 
  Lock, 
  Calendar, 
  Clock, 
  Users, 
  PauseCircle,
  ThumbsUp,
  Star,
  Filter,
  Search
} from 'lucide-react';
import { checkUserAvailability, getModeColor, getApprovalColor } from '../utils/availability';
import { AvailabilityMode } from '../data/mockData';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import CategorySelector from '../components/availability/CategorySelector';
import { useTranslation } from 'react-i18next';

import UserAvatar from '../components/common/UserAvatar';

export default function MatchPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { 
    users, 
    currentUser, 
    currentSelections, 
    addSelection, 
    removeSelection, 
    clearSelections, 
    findMatches,
    setSelections,
    conversations 
  } = useAppContext();

  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Optimized Search & Filter Logic
  const displayUsers = useMemo(() => {
    // 1. If searching, search GLOBAL users (ignoring interest filters to find anyone)
    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const numQuery = parseInt(query);
        const isNum = !isNaN(numQuery);

        return users.filter(user => {
            // Name match
            if (user.name.toLowerCase().includes(query)) return true;
            // Vibe match
            if (user.vibe?.toLowerCase()?.includes(query)) return true;
            // Rating match (>= query)
            if (isNum && user.approvalRating >= numQuery) return true;
            
            return false;
        }).sort((a, b) => b.approvalRating - a.approvalRating);
    }

    // 2. If no search, use standard Selection/Interest matching
    if (currentSelections.length > 0) {
        return findMatches();
    }

    // 3. Default: Show all users sorted by rating
    return [...users].sort((a, b) => b.approvalRating - a.approvalRating);
  }, [searchQuery, users, currentSelections, findMatches]);

  // Check if we have an existing active conversation with a user
  const hasActiveChat = (userId) => {
      const conv = (conversations || []).find(c => c.userId === userId);
      return conv && conv.messages && conv.messages.length > 0;
  };

  const handleMessage = (userId) => {
    navigate(`/chat/${userId}`);
  };

  const handleApplyFilters = (newSelections) => {
    setSelections(newSelections);
    setIsFilterOpen(false);
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <div className="bg-card px-4 py-3 sticky top-0 z-10 border-b border-border shadow-sm space-y-3">
        <div>
          <h1 className="text-xl font-bold text-foreground">{t('match.find_vibe')}</h1>
          <p className="text-xs text-muted-foreground">
            {currentSelections.length > 0 
              ? t('match.interests_selected', { count: currentSelections.length })
              : t('match.select_interests')
            }
          </p>
        </div>

        <div className="flex gap-2">
          <div className="relative flex-1">
            {/* Whistle Icon */}
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"
            >
              <path d="M11 3a8 8 0 0 1 8 8v7a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-1a2 2 0 0 0-2-2H8a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3Z" />
              <path d="M2.5 10a4.5 4.5 0 0 1 7-4.5" />
            </svg>
            <Input
              placeholder={t('match.search_placeholder')}
              className="pl-9 bg-muted border-border text-foreground h-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button 
            onClick={() => setIsFilterOpen(true)}
            variant="outline"
            size="icon"
            className="h-10 w-10 border-primary/20 bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary shrink-0"
          >
            <Filter className="w-4 h-4" />
            {currentSelections.length > 0 && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
              </span>
            )}
          </Button>
        </div>
      </div>

      {/* Selected Categories Horizontal Scroll */}
      {currentSelections.length > 0 && (
        <div className="bg-card px-4 py-2 border-b border-border overflow-x-auto whitespace-nowrap scrollbar-hide">
          <div className="flex gap-2">
            {currentSelections.map(item => (
              <Badge 
                key={item} 
                variant="secondary"
                className="cursor-pointer hover:bg-accent px-3 py-1 text-sm font-medium bg-muted text-muted-foreground"
                onClick={() => removeSelection(item)}
              >
                {item} ×
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-4 space-y-4">
        {displayUsers.length === 0 ? (
           <div className="text-center py-10 text-muted-foreground">
             {searchQuery 
                ? t('match.no_users', { query: searchQuery })
                : t('match.no_matches')}
           </div>
        ) : (
          displayUsers.filter(u => u.id !== currentUser?.id).map(user => (
            <MatchCard 
              key={user.id} 
              user={user} 
              onMessage={() => handleMessage(user.id)} 
              t={t}
              hasExistingChat={conversations.some(c => c.userId === user.id && c.messages && c.messages.length > 0)}
            />
          ))
        )}
      </div>

      {/* Category Selector Sheet */}
      <CategorySelector 
        isOpen={isFilterOpen}
        onClose={setIsFilterOpen}
        currentSelected={currentSelections}
        onApply={handleApplyFilters}
        maxSelections={5}
        title={t('match.select_interests')}
      />
    </div>
  );
}

function MatchCard({ user, onMessage, t, hasExistingChat }) {
  const { available, reason, modeColor, statusText } = checkUserAvailability(user);
  
  // Logic: Only Orange Mode allows bypassing the "Unavailable" state for existing chats.
  // Blue/Red/Gray are strict blocks.
  const isOrangeBypass = user.availabilityMode === 'orange' && hasExistingChat;
  const canMessage = available || isOrangeBypass;

  const getStatusIcon = () => {
    switch(user.availabilityMode) {
      case AvailabilityMode.RED: return <Lock className="w-4 h-4" />;
      case AvailabilityMode.GRAY: return <PauseCircle className="w-4 h-4" />;
      case AvailabilityMode.BLUE: return <Calendar className="w-4 h-4" />;
      case AvailabilityMode.YELLOW: return <Clock className="w-4 h-4" />;
      case AvailabilityMode.BROWN: return <Clock className="w-4 h-4" />;
      case AvailabilityMode.ORANGE: return <Users className="w-4 h-4" />;
      case AvailabilityMode.GREEN: return null; 
      default: return null; 
    }
  };

  // Determine if "Message" button should be disabled
  // We want to allow clicking to VIEW the chat even if unavailable (to see limits),
  // EXCEPT if they are strictly blocked by other means (like Red mode maybe? But prompt says User 4 opens chatbox).
  // So let's enable it generally but the Chat Page will handle the "Read Only" state.
  const isClickable = true; 

  return (
    <div className="bg-card rounded-xl p-4 shadow-sm border border-border">
      <div className="flex gap-4">
        {/* Avatar with Mode Indicator */}
        <div className="relative">
          <UserAvatar 
            src={user.profilePic} 
            alt={user.name} 
            className="w-16 h-16 rounded-full"
            size={32}
          />
          <div 
            className="absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-background"
            style={{ backgroundColor: modeColor }}
          />
        </div>

        {/* Info */}
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-bold text-lg text-foreground">{user.name}</h3>
              <p className="text-sm text-muted-foreground">{user.vibe} • {user.location}</p>
            </div>
            {user.matchPercentage !== undefined && (
              <div className="bg-primary/10 text-primary px-2 py-1 rounded-lg text-xs font-bold">
                {user.matchPercentage}% Match
              </div>
            )}
          </div>

          <div className="mt-2 flex items-center gap-4 text-sm">
            <div className={`flex items-center gap-1 ${getApprovalColor(user.approvalRating)}`}>
              <ThumbsUp className="w-3 h-3" />
              <span className="font-bold">{user.approvalRating > 0 ? `+${user.approvalRating}` : user.approvalRating}</span>
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <Star className="w-3 h-3 text-yellow-400" />
              <span>{user.reviewRating} ({user.reviewCount})</span>
            </div>
          </div>
        </div>
      </div>

      {/* Common Interests Preview if matched */}
      {user.matchPercentage !== undefined && (
          <div className="mt-3 flex gap-1 flex-wrap">
             {user.selections?.slice(0, 5).map(interest => (
                 <span key={interest} className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
                     {interest}
                 </span>
             ))}
             {user.selections?.length > 5 && (
                 <span className="text-[10px] text-muted-foreground px-1 py-0.5">+{user.selections.length - 5} more</span>
             )}
          </div>
      )}

      {/* Status & Action */}
      <div className="mt-4 flex items-center justify-between pt-3 border-t border-border">
        <div className="flex items-center gap-2 text-sm">
          {getStatusIcon()}
          <span style={{ color: modeColor }} className="font-medium">
            {statusText || reason}
          </span>
        </div>

        <button
          onClick={onMessage}
          className={`
            px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors
            ${canMessage 
              ? 'bg-green-600 text-white hover:bg-green-700 shadow-sm' 
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }
          `}
        >
          {canMessage ? (
            <>
              <MessageSquare className="w-4 h-4" />
              {t('common.message')}
            </>
          ) : (
            // Show "Unavailable" but allow click to view details/limit
            <>
               <Lock className="w-4 h-4" />
               {t('common.view')}
            </>
          )}
        </button>
      </div>
    </div>
  );
}
