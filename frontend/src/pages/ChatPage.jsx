
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Plus, Smile, X } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import RatingModal from '../components/chat/RatingModal';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import ModeIndicator from '../components/availability/ModeIndicator';
import { checkUserAvailability } from '../utils/availability';

// Popular emojis organized by category
const EMOJI_CATEGORIES = {
  'Smileys': ['😀', '😃', '😄', '😁', '😅', '😂', '🤣', '😊', '😇', '🙂', '😉', '😍', '🥰', '😘', '😋', '😜', '🤪', '😎', '🤩', '🥳'],
  'Gestures': ['👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👋', '🙌', '👏', '🤝', '💪', '🙏', '✋', '🖐️', '👊', '✊', '🫶', '❤️'],
  'Faces': ['😢', '😭', '😤', '😠', '🤬', '😈', '💀', '🤡', '👻', '😱', '😨', '😰', '🥺', '😩', '😫', '🥱', '😴', '🤮', '🤧', '🤒'],
  'Objects': ['🎉', '🎊', '🎁', '🎈', '💯', '🔥', '⭐', '✨', '💫', '🌟', '💥', '💢', '💬', '💭', '🗯️', '📱', '💻', '🎮', '🎵', '🎶'],
  'Love': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '♥️']
};

import UserAvatar from '../components/common/UserAvatar';

const ChatPage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { 
    getUserById, 
    getConversation, 
    sendMessage, 
    receiveMessage, 
    startChat, 
    rateConversation,
    currentUser 
  } = useAppContext();
  
  const [text, setText] = useState('');
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [hasRatedCurrentSession, setHasRatedCurrentSession] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('Smileys');
  const scrollRef = useRef(null);
  const emojiPickerRef = useRef(null);
  
  const otherUser = getUserById ? getUserById(userId) : null;
  const conversation = getConversation ? getConversation(userId) : null;
  const availabilityStatus = otherUser ? checkUserAvailability(otherUser) : { available: false, reason: 'Offline' };
  
  // Logic: 
  // 1. If available (Green, Yellow, etc.) -> YES
  // 2. If Orange Mode AND existing chat -> YES (Bypass limit for existing participants)
  // 3. If Blue/Red/Gray/Brown -> NO (Strict blocking logic applies universally, overriding existing chats)
  
  const hasExistingChat = conversation && conversation.messages && conversation.messages.length > 0;
  const isOrangeBypass = otherUser?.availabilityMode === 'orange' && hasExistingChat;
  
  const canMessage = availabilityStatus.available || isOrangeBypass;

  const TIMER_DURATION = 2 * 60 * 1000; // 2 minutes

  // Close emoji picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target)) {
        setShowEmojiPicker(false);
      }
    };
    
    if (showEmojiPicker) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showEmojiPicker]);

  const handleEmojiClick = (emoji) => {
    setText(prev => prev + emoji);
  };

  // 1. INITIALIZATION: Ensure conversation exists (but don't auto-start timer)
  useEffect(() => {
    if (userId && startChat) {
      startChat(userId);
    }
  }, [userId, startChat]);

  // Reset session rating flag when conversation is rated (so new session can trigger modal)
  useEffect(() => {
    if (conversation?.rated) {
      setHasRatedCurrentSession(true);
    }
  }, [conversation?.rated]);

  // 2. CALCULATION - Timer only runs if timerStarted is set
  const calculateRemaining = useCallback(() => {
      // Timer not started yet -> show full duration (2:00)
      if (!conversation || conversation.timerStarted === null || conversation.timerStarted === undefined) {
        return TIMER_DURATION;
      }
      
      // If rated, show 00:00
      if (conversation.rated) {
        return 0;
      }
      
      const elapsed = Date.now() - conversation.timerStarted;
      return Math.max(0, TIMER_DURATION - elapsed);
  }, [conversation, TIMER_DURATION]);

  // Reset rating flag ONLY when a NEW timer starts (meaning time > 0)
  // Fixes issue where modal pops up twice because previous effect reset flag too aggressively
  useEffect(() => {
    // We check if the timer is running and we have plenty of time left (> 2 seconds),
    // which implies a RESET happened (new message sent).
    const remaining = calculateRemaining();
    if (conversation?.timerStarted && !conversation?.rated && hasRatedCurrentSession && remaining > 2000) {
      setHasRatedCurrentSession(false);
    }
  }, [conversation?.timerStarted, conversation?.rated, hasRatedCurrentSession, calculateRemaining]);

  const [timeRemaining, setTimeRemaining] = useState(calculateRemaining());

  // 3. INTERVAL - Timer logic
  useEffect(() => {
    if (!conversation) return;

    // If timer not started, show full duration (2:00)
    if (!conversation.timerStarted) {
        setTimeRemaining(TIMER_DURATION);
        return;
    }
    
    // If already rated, show 00:00
    if (conversation.rated) {
        setTimeRemaining(0);
        return;
    }

    const interval = setInterval(() => {
      const remaining = calculateRemaining();
      setTimeRemaining(remaining);

      // Trigger Modal when timer expires
      if (remaining <= 0) {
         clearInterval(interval);
         // Only show modal if:
         // 1. Not already rated
         // 2. Not already shown locally
         // 3. Current user is the SENDER of the last message (Only sender rates)
         const isSender = conversation.lastMessageSenderId === currentUser?.id;
         
         if (!conversation.rated && !hasRatedCurrentSession && isSender) {
             setShowRatingModal(true);
         }
      }
    }, 200);

    return () => clearInterval(interval);
  }, [conversation, calculateRemaining, hasRatedCurrentSession, currentUser]); 

  // 4. AUTO-REPLY - Removed (Backend does not auto-reply)
  useEffect(() => {
    // This effect intentionally left empty as backend integration 
    // does not include the previous mock auto-reply logic.
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [conversation?.messages]);

  const formatTime = (ms) => {
    if (isNaN(ms) || ms < 0) return "00:00"; 
    const totalSeconds = Math.ceil(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    // Timer not started - show gray
    if (!conversation?.timerStarted) {
      return 'text-muted-foreground';
    }
    // Timer rated/done
    if (conversation?.rated) {
      return 'text-green-600';
    }
    if (timeRemaining <= 10000) return 'text-destructive animate-pulse';
    if (timeRemaining <= 30000) return 'text-orange-500';
    return 'text-foreground';
  };

  const getTimerDisplay = () => {
    // Timer not started yet - show 2:00
    if (!conversation?.timerStarted) {
      return '⏸ 02:00';
    }
    // Timer rated/stopped
    if (conversation?.rated) {
      return '✓ Done';
    }
    // Timer running or expired
    return formatTime(timeRemaining);
  };

  const handleRate = useCallback((isGood, reason) => {
    if (rateConversation) {
        rateConversation(userId, isGood, reason);
    }
    setHasRatedCurrentSession(true);
    setShowRatingModal(false);
    // After rating, timer logic will see conversation.rated = true and set 00:00
  }, [rateConversation, userId]);

  const handleSendMessage = () => {
    if (!text.trim() || !canMessage) return;
    if (sendMessage) sendMessage(userId, text);
    setText('');
  };

  if (!otherUser) return <div className="flex items-center justify-center h-screen bg-background text-foreground">Loading...</div>;

  return (
    <div className="flex flex-col h-[calc(100vh-130px)] bg-background relative">
      <div className="border-b border-border p-3 flex items-center justify-between sticky top-0 bg-card z-10 relative">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-1 hover:bg-accent rounded-full text-muted-foreground">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="relative">
            <UserAvatar src={otherUser.profilePic} alt={otherUser.name} className="w-10 h-10 rounded-full" size={20} />
            <ModeIndicator mode={otherUser.availabilityMode} className="absolute -top-1 -right-1" size="small" />
          </div>
          <div>
            <h2 className="font-semibold text-foreground text-sm">{otherUser.name}</h2>
            <div className="text-xs text-muted-foreground">
                {availabilityStatus.available ? 'Online' : availabilityStatus.statusText || 'Offline'}
            </div>
          </div>
        </div>

        {/* Orange Mode Status Indicator */}
        <div className="flex items-center gap-2">
            {otherUser.availabilityMode === 'orange' && (
                <div className={`hidden sm:flex px-2 py-1 rounded-full text-[10px] font-bold border shadow-sm items-center gap-1 h-7 ${
                    (otherUser.availability?.currentContacts || 0) >= (otherUser.availability?.maxContact || 0)
                    ? 'bg-destructive/10 text-destructive border-destructive/20'
                    : 'bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400'
                }`}>
                   <span className="whitespace-nowrap">
                     {Math.min((otherUser.availability?.currentContacts || 0), (otherUser.availability?.maxContact || 0))}/{(otherUser.availability?.maxContact || 0)} max contact
                   </span>
                </div>
            )}

            {/* Yellow Mode Status Indicator */}
            {otherUser.availabilityMode === 'yellow' && otherUser.availability?.laterStartTime && (
                <div className="flex px-2 py-1 rounded-full text-[10px] font-bold border shadow-sm items-center gap-1 h-7 bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400">
                   <span className="whitespace-nowrap">
                     {(() => {
                        const now = Date.now();
                        const end = otherUser.availability.laterStartTime + (otherUser.availability.laterMinutes * 60 * 1000);
                        const diff = Math.max(0, end - now);
                        const mins = Math.floor(diff / 60000);
                        if (mins >= 60) {
                            return `Active: ${Math.floor(mins/60)}h ${mins%60}m`;
                        }
                        return `Active: ${mins}m`;
                     })()}
                   </span>
                </div>
            )}

            {/* Brown Mode Status Indicator - Removed Feature */}
            {otherUser.availabilityMode === 'brown' && (
                <div className="hidden sm:flex px-2 py-1 rounded-full text-[10px] font-bold border shadow-sm items-center gap-1 h-7 bg-gray-100 text-gray-500 border-gray-200">
                   <span className="whitespace-nowrap">
                     Timed Mode (Deprecated)
                   </span>
                </div>
            )}

            <div className="flex items-center gap-2 bg-muted px-3 py-1.5 rounded-full border border-border h-8">
              <span className={`text-sm font-mono font-bold ${getTimerColor()}`}>
                {getTimerDisplay()}
              </span>
              {timeRemaining <= 0 && conversation?.timerStarted && !conversation?.rated && <span className="text-xs">⌛</span>}
            </div>
        </div>
      </div>
      
      {/* Mobile-only Orange Status Bar (if it doesn't fit in top bar) */}
      {otherUser.availabilityMode === 'orange' && (
          <div className="sm:hidden bg-orange-50/50 dark:bg-orange-900/10 border-b border-orange-100 dark:border-orange-900/20 py-1 flex justify-center">
              <span className={`text-[10px] font-bold ${
                    (otherUser.availability?.currentContacts || 0) >= (otherUser.availability?.maxContact || 0)
                    ? 'text-destructive'
                    : 'text-orange-600 dark:text-orange-400'
                }`}>
                  Max Contacts: {Math.min((otherUser.availability?.currentContacts || 0), (otherUser.availability?.maxContact || 0))}/{(otherUser.availability?.maxContact || 0)}
              </span>
          </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/30" ref={scrollRef}>
        {(!conversation?.messages || conversation.messages.length === 0) && (
           <div className="text-center text-muted-foreground text-sm mt-10">
             Start a conversation with {otherUser.name}.<br/>
             {conversation?.timerStarted ? 'Timer is running!' : 'Timer starts when you send a message.'}
           </div>
        )}
        {conversation?.messages?.map((msg) => {
          const isMe = msg.senderId === currentUser?.id;
          return (
            <div key={msg.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm shadow-sm ${
                  isMe ? 'bg-primary text-primary-foreground rounded-tr-none' : 'bg-card border border-border text-card-foreground rounded-tl-none'
                }`}>
                <p>{msg.text}</p>
                <div className={`text-[10px] mt-1 text-right ${isMe ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                  {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                  {isMe && (
                    <span className="ml-1">
                      {msg.seen ? <span className="text-primary-foreground/90">Seen</span> : '✓✓'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-card p-3 border-t border-border flex items-center gap-2 relative">
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground" disabled={!canMessage}>
          <Plus className="w-5 h-5" />
        </Button>
        <div className="flex-1 relative">
          <Input
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={canMessage ? "Type message..." : `⛔ ${availabilityStatus.reason || "User Unavailable"}`}
            className="pr-10 rounded-full border-border bg-muted focus:bg-background transition-all"
            disabled={!canMessage}
          />
          <button 
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
            className={`absolute right-3 top-2.5 w-5 h-5 transition-colors ${showEmojiPicker ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`}
            disabled={!canMessage}
          >
            <Smile className="w-5 h-5" />
          </button>
        </div>
        <Button onClick={handleSendMessage} disabled={!text.trim() || !canMessage} size="icon" className="bg-primary hover:bg-primary/90 rounded-full w-10 h-10 flex items-center justify-center transition-colors shadow-sm">
            <Send className="w-4 h-4 text-primary-foreground ml-0.5" />
        </Button>

        {/* Emoji Picker */}
        {showEmojiPicker && (
          <div 
            ref={emojiPickerRef}
            className="absolute bottom-16 right-2 bg-card rounded-xl shadow-xl border border-border w-72 z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-muted">
              <span className="text-sm font-semibold text-foreground">Emojis</span>
              <button 
                onClick={() => setShowEmojiPicker(false)}
                className="p-1 hover:bg-accent rounded-full transition-colors"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>
            
            {/* Category Tabs */}
            <div className="flex gap-1 px-2 py-2 border-b border-border overflow-x-auto scrollbar-hide">
              {Object.keys(EMOJI_CATEGORIES).map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-1 text-xs font-medium rounded-full whitespace-nowrap transition-colors ${
                    selectedCategory === category 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
            
            {/* Emoji Grid */}
            <div className="p-2 max-h-48 overflow-y-auto">
              <div className="grid grid-cols-8 gap-1">
                {EMOJI_CATEGORIES[selectedCategory].map((emoji, index) => (
                  <button
                    key={index}
                    onClick={() => handleEmojiClick(emoji)}
                    className="w-8 h-8 flex items-center justify-center text-xl hover:bg-accent rounded-lg transition-colors"
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {showRatingModal && (
        <RatingModal
          isOpen={showRatingModal}
          userName={otherUser.name}
          onRate={handleRate}
          onClose={() => {
            setShowRatingModal(false);
            setHasRatedCurrentSession(true);
          }}
          onGoBack={() => navigate(-1)}
          type="chat"
        />
      )}
    </div>
  );
};

export default ChatPage;
