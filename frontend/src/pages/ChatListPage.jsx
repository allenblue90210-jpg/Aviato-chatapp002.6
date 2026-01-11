
import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import ModeIndicator from '../components/availability/ModeIndicator';
import { MessageSquare, PenSquare, Search, Lock, Calendar, Users, Clock, UserPlus } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { AvailabilityMode } from '../data/mockData';
import { checkUserAvailability } from '../utils/availability';

import UserAvatar from '../components/common/UserAvatar';

// Helper for timestamp formatting
const formatMessageTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

  if (diffDays === 0 && date.getDate() === now.getDate()) {
    // Today: "Today 2:15 PM"
    return `Today ${date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
  } else if (diffDays === 0 || diffDays === 1) {
    // Yesterday
    return `Yesterday ${date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
  } else {
    // "Jan 28, 3:45 PM"
    return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
  }
};

// Helper for Timer formatting
const formatDuration = (ms) => {
    if (ms === undefined || ms === null || isNaN(ms)) return "00:00";
    const totalSeconds = Math.max(0, Math.ceil(ms / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
};

const TIMER_DURATION = 2 * 60 * 1000; // 2 minutes

const ChatListItem = ({ conversation, user }) => {
  const navigate = useNavigate();
  const [timeRemaining, setTimeRemaining] = useState(0);
  
  // Calculate time remaining
  useEffect(() => {
    const calculateRemaining = () => {
      // Timer not started
      if (!conversation.timerStarted) {
        return 0;
      }
      // Timer rated/completed
      if (conversation.rated) {
        return 0;
      }
      const elapsed = Date.now() - conversation.timerStarted;
      return Math.max(0, TIMER_DURATION - elapsed);
    };
    
    // Initial calculation
    setTimeRemaining(calculateRemaining());
    
    // Only run interval if timer is active (started and not rated)
    if (conversation.timerStarted && !conversation.rated) {
      const interval = setInterval(() => {
        const remaining = calculateRemaining();
        setTimeRemaining(remaining);
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [conversation.timerStarted, conversation.rated]);
  
  const formatted = formatDuration(timeRemaining);
  const expired = timeRemaining <= 0;
  const timerActive = conversation.timerStarted && !conversation.rated;
  
  if (!user) return null;

  // Check user availability
  const availabilityStatus = checkUserAvailability(user);
  
  // Get formatted time for brown mode
  const formatTime = (hour, minute) => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    const displayMinute = minute ? minute.toString().padStart(2, '0') : '00';
    return `${displayHour}:${displayMinute} ${period}`;
  };
  
  // Get mode-specific status text
  const getModeStatusText = () => {
    switch(user.availabilityMode) {
      case AvailabilityMode.RED:
        return <span className="text-destructive font-medium flex items-center gap-1">
          🔒 User locked messaging
        </span>;
      case AvailabilityMode.BLUE:
        if (user.availability?.openDate) {
          const date = new Date(user.availability.openDate).toLocaleDateString();
          return <span className="text-primary font-medium flex items-center gap-1">
            📅 Available: {date}
          </span>;
        }
        break;
      case AvailabilityMode.ORANGE:
        if (user.availability.currentContacts >= user.availability.maxContact) {
          return <span className="text-orange-600 font-medium flex items-center gap-1">
            👥 Max contacts reached
          </span>;
        }
        break;
      case AvailabilityMode.BROWN:
        if (user.availability?.timedHour !== null) {
          const timedHour = user.availability.timedHour;
          const timedMinute = user.availability.timedMinute || 0;
          const timeStr = formatTime(timedHour, timedMinute);
          
          const now = new Date();
          const currentHour = now.getHours();
          const currentMinute = now.getMinutes();
          
          let isPastDeadline = false;
          if (currentHour > timedHour) {
            isPastDeadline = true;
          } else if (currentHour === timedHour && currentMinute >= timedMinute) {
            isPastDeadline = true;
          }

          if (isPastDeadline) {
             return <span className="text-yellow-600 font-medium flex items-center gap-1">
                🔒 Closed at: {timeStr}
             </span>;
          }
          
          return <span className="text-green-600 font-medium flex items-center gap-1">
            🕐 Closes at: {timeStr}
          </span>;
        }
        break;
      case AvailabilityMode.GRAY:
        return <span className="text-muted-foreground font-medium flex items-center gap-1">
          ⏸️ User paused messaging
        </span>;
      case AvailabilityMode.YELLOW:
        if (user.availability?.laterStartTime && user.availability?.laterMinutes) {
            const now = Date.now();
            const end = user.availability.laterStartTime + (user.availability.laterMinutes * 60 * 1000);
            if (now > end) {
                return <span className="text-yellow-600 font-medium flex items-center gap-1">
                  ⚠️ Expired
                </span>;
            }
        }
        break;
      default:
        return null;
    }
    return null;
  };

  // Get timer color based on time remaining
  const getTimerColor = () => {
    if (timeRemaining <= 10000) return 'text-destructive';
    if (timeRemaining <= 30000) return 'text-orange-500';
    return 'text-green-600';
  };

  // Determine status display
  let statusDisplay;
  
  if (conversation.rated) {
    // Show mode-specific status for unavailable modes even when rated
    const modeStatus = getModeStatusText();
    if (modeStatus && !availabilityStatus.available) {
      statusDisplay = modeStatus;
    } else {
      statusDisplay = <span className="text-muted-foreground font-medium">✓ Rated</span>;
    }
  } else if (!conversation.timerStarted) {
    // Timer not started yet
    const modeStatus = getModeStatusText();
    if (modeStatus && !availabilityStatus.available) {
      statusDisplay = modeStatus;
    } else {
      statusDisplay = <span className="text-muted-foreground font-medium">⏸ Waiting to start</span>;
    }
  } else if (expired && !conversation.rated) {
    // Timer expired but not rated
    statusDisplay = <span className="text-destructive font-medium">⌛ Expired • Rate pending</span>;
  } else {
    // Active conversation with running timer
    const modeStatus = getModeStatusText();
    if (modeStatus && !availabilityStatus.available) {
      statusDisplay = modeStatus;
    } else {
      statusDisplay = (
        <span className={`flex items-center gap-1 font-medium ${getTimerColor()}`}>
          ⏱️ {formatted} remaining
        </span>
      );
    }
  }

  return (
    <div 
      onClick={() => navigate(`/chat/${user.id}`)}
      className="bg-card p-4 border-b border-border hover:bg-accent transition-colors cursor-pointer flex gap-3"
    >
      <div className="relative">
        <UserAvatar src={user.profilePic} alt={user.name} className="w-12 h-12 rounded-full" size={24} />
        <ModeIndicator mode={user.availabilityMode} className="absolute -top-1 -right-1" size="small" />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start mb-0.5">
          <h3 className="font-bold text-foreground truncate text-base">{user.name}</h3>
        </div>
        
        <p className={`text-sm mb-1.5 truncate ${conversation.rated || expired ? 'text-muted-foreground' : 'text-foreground/80 font-medium'}`}>
          {conversation.lastMessage || "Started a new conversation"}
        </p>
        
        <div className="flex justify-between items-center text-xs">
          {statusDisplay}
          <span className="text-muted-foreground whitespace-nowrap ml-2">
            {formatMessageTime(conversation.lastMessageTime)}
          </span>
        </div>
      </div>
    </div>
  );
};

// Component for searching new users within Chat List
const NewUserResultItem = ({ user, onClick }) => {
  const availabilityStatus = checkUserAvailability(user);
  const isAvailable = availabilityStatus.available;

  return (
    <div 
      onClick={onClick}
      className={`p-4 flex items-center gap-3 border-b border-border transition-colors ${
        isAvailable ? 'hover:bg-accent cursor-pointer' : 'opacity-60 cursor-not-allowed bg-muted/50'
      }`}
    >
      <div className="relative">
        <UserAvatar src={user.profilePic} alt={user.name} className="w-10 h-10 rounded-full" size={20} />
        <ModeIndicator mode={user.availabilityMode} className="absolute -top-1 -right-1" size="small" />
      </div>
      
      <div className="flex-1">
        <div className="flex justify-between items-center mb-0.5">
          <h3 className="font-semibold text-foreground text-sm">{user.name}</h3>
          <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
            isAvailable ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100' : 'bg-muted text-muted-foreground'
          }`}>
            {isAvailable ? 'Available' : availabilityStatus.statusText}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          {user.vibe}
        </p>
      </div>
      <Button size="sm" variant="ghost" className="h-8 w-8 p-0 text-primary">
        <MessageSquare className="w-4 h-4" />
      </Button>
    </div>
  );
};

const ChatListPage = () => {
  const { conversations, users, getCurrentMode, startChat, currentUser } = useAppContext();
  const navigate = useNavigate();
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [chatSearchQuery, setChatSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);

  // Filter conversations by user name
  const filteredConversations = useMemo(() => {
    if (!chatSearchQuery.trim()) return conversations;
    
    const lowerQuery = chatSearchQuery.toLowerCase();
    return conversations.filter(conv => {
      const user = users.find(u => u.id === conv.userId);
      if (!user) return false;
      return user.name.toLowerCase().includes(lowerQuery) ||
             user.vibe?.toLowerCase()?.includes(lowerQuery) ||
             user.location?.toLowerCase()?.includes(lowerQuery);
    });
  }, [conversations, users, chatSearchQuery]);

  // Find users NOT in conversations but matching search (Global Search)
  const newConnections = useMemo(() => {
      if (!chatSearchQuery.trim() || !currentUser) return [];
      
      const chattedIds = new Set(conversations.map(c => c.userId));
      const lowerQuery = chatSearchQuery.toLowerCase();
      
      return users.filter(u => 
          u.id !== currentUser.id && 
          !chattedIds.has(u.id) &&
          (u.name.toLowerCase().includes(lowerQuery) || 
           u.vibe?.toLowerCase().includes(lowerQuery))
      ).slice(0, 5); // Limit to 5 suggestions
  }, [chatSearchQuery, users, conversations, currentUser]);

  const filteredUsers = useMemo(() => {
    if (!currentUser) return [];
    
    // Filter out current user and sort by name
    let result = users.filter(u => u.id !== currentUser.id);
    
    if (searchQuery) {
      const lowerQuery = searchQuery.toLowerCase();
      result = result.filter(u => 
        u.name.toLowerCase().includes(lowerQuery) || 
        u.vibe?.toLowerCase()?.includes(lowerQuery) ||
        u.location?.toLowerCase()?.includes(lowerQuery)
      );
    }
    
    return result;
  }, [users, searchQuery, currentUser]);

  const handleUserClick = (userId) => {
    // Navigate even if unavailable so user can see the reason/limit
    startChat(userId);
    setIsComposeOpen(false);
    navigate(`/chat/${userId}`);
  };

  return (
    <div className="bg-background min-h-full pb-20">
      <div className="p-4 border-b border-border bg-card sticky top-0 z-10">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold text-foreground">Chat</h1>
          <div className="flex gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className={`${showSearch ? 'bg-primary/10 text-primary' : 'text-muted-foreground'} hover:bg-primary/10 hover:text-primary`}
              onClick={() => {
                setShowSearch(!showSearch);
                if (showSearch) setChatSearchQuery("");
              }}
            >
              <Search className="w-5 h-5" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-primary hover:bg-primary/10"
              onClick={() => setIsComposeOpen(true)}
            >
              <PenSquare className="w-6 h-6" />
            </Button>
          </div>
        </div>
        
        {/* Search Input */}
        {showSearch && (
          <div className="mt-3 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search chats or find new people..."
              value={chatSearchQuery}
              onChange={(e) => setChatSearchQuery(e.target.value)}
              className="pl-9 bg-muted border-border text-foreground"
              autoFocus
            />
            {chatSearchQuery && (
              <button
                onClick={() => setChatSearchQuery("")}
                className="absolute right-3 top-2.5 text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            )}
          </div>
        )}
      </div>

      <div className="divide-y divide-border">
        {/* Active Conversations */}
        {filteredConversations.length > 0 && (
            filteredConversations.map(conv => {
                const user = users.find(u => u.id === conv.userId);
                return <ChatListItem key={conv.id} conversation={conv} user={user} />;
            })
        )}

        {/* Global Search Results (New Connections) */}
        {newConnections.length > 0 && (
            <div className="bg-muted/30">
                <div className="px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted/50">
                    Start a new chat
                </div>
                {newConnections.map(user => (
                    <NewUserResultItem 
                        key={user.id} 
                        user={user} 
                        onClick={() => handleUserClick(user.id)} 
                    />
                ))}
            </div>
        )}

        {/* Empty States */}
        {filteredConversations.length === 0 && newConnections.length === 0 && (
            conversations.length > 0 && chatSearchQuery ? (
            <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
                <div className="bg-muted p-4 rounded-full mb-4">
                <Search className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-medium text-foreground mb-2">No results found</h3>
                <p className="text-muted-foreground">No chats or people found matching "{chatSearchQuery}"</p>
            </div>
            ) : conversations.length === 0 && !chatSearchQuery && (
            <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
                <div className="bg-muted p-4 rounded-full mb-4">
                <MessageSquare className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-medium text-foreground mb-2">No conversations yet</h3>
                <p className="text-muted-foreground mb-6">Start a conversation with anyone!</p>
                <Button 
                onClick={() => setIsComposeOpen(true)}
                className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
                >
                Start New Chat
                </Button>
            </div>
            )
        )}
      </div>

      {/* Compose/New Message Modal */}
      <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
        <DialogContent className="sm:max-w-md h-[80vh] flex flex-col p-0 gap-0 overflow-hidden bg-card border-border">
          <DialogHeader className="px-4 py-3 border-b border-border flex flex-row items-center justify-between space-y-0">
            <DialogTitle className="text-lg font-bold text-foreground">New Message</DialogTitle>
          </DialogHeader>
          
          <div className="p-3 border-b border-border bg-card">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, vibe..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-muted border-border text-foreground"
                autoFocus
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {filteredUsers.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No users found
              </div>
            ) : (
              <div className="divide-y divide-border">
                {filteredUsers.map(user => {
                  const availabilityStatus = checkUserAvailability(user);
                  const isAvailable = availabilityStatus.available;
                  
                  // Get icon for unavailable state
                  const getUnavailableIcon = () => {
                    switch(user.availabilityMode) {
                      case AvailabilityMode.RED:
                        return <Lock className="w-3.5 h-3.5" />;
                      case AvailabilityMode.BLUE:
                        return <Calendar className="w-3.5 h-3.5" />;
                      case AvailabilityMode.ORANGE:
                        if (user.availability?.currentContacts >= user.availability?.maxContact) {
                          return <Users className="w-3.5 h-3.5" />;
                        }
                        return null;
                      case AvailabilityMode.BROWN:
                        return <Clock className="w-3.5 h-3.5" />;
                      case AvailabilityMode.GRAY:
                        return <span className="text-xs">⏸️</span>;
                      default:
                        return null;
                    }
                  };

                  return (
                    <div 
                      key={user.id}
                      onClick={() => handleUserClick(user.id)}
                      className={`p-4 flex items-center gap-3 transition-colors ${
                        isAvailable 
                          ? 'hover:bg-accent cursor-pointer' 
                          : 'opacity-60 cursor-not-allowed bg-muted/50'
                      }`}
                    >
                      <div className="relative">
                        <UserAvatar src={user.profilePic} alt={user.name} className="w-12 h-12 rounded-full" size={24} />
                        <ModeIndicator mode={user.availabilityMode} className="absolute -top-1 -right-1" size="small" />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-1">
                          <h3 className="font-semibold text-foreground">{user.name}</h3>
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full flex items-center gap-1 ${
                            isAvailable ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100' : 'bg-muted text-muted-foreground'
                          }`}>
                            {!isAvailable && getUnavailableIcon()}
                            {isAvailable ? 'Available' : availabilityStatus.statusText}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {user.vibe} • {user.location}
                        </p>
                        {!isAvailable && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {availabilityStatus.reason}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChatListPage;
