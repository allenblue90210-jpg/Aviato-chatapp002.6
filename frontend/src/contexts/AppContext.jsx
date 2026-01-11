
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { AvailabilityMode, mockUsers } from '../data/mockData';
import { checkUserAvailability, calculateMatchPercentage } from '../utils/availability';
import { useToast } from '../hooks/use-toast';
import { translations } from '../data/translations';
import api from '../api/axios';

const AppContext = createContext();

export const useAppContext = () => useContext(AppContext);
export const useApp = useAppContext;

export const AppProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [currentSelections, setCurrentSelections] = useState([]);
  const [theme, setTheme] = useState('system');
  const [dataLoading, setDataLoading] = useState(false);
  
  // Language State
  const [language, setLanguageState] = useState(() => {
    try {
      return localStorage.getItem('aviato_language') || 'en';
    } catch {
      return 'en';
    }
  });

  const setLanguage = (lang) => {
    setLanguageState(lang);
    localStorage.setItem('aviato_language', lang);
  };

  // Translation Helper
  const t = useCallback((key) => {
    return translations[language]?.[key] || translations['en']?.[key] || key;
  }, [language]);

  const { toast } = useToast();
  
  const showToast = useCallback((message, type = 'info') => {
    let variant = "default";
    if (type === 'error') variant = "destructive";
    toast({
      variant: variant,
      description: <div className="whitespace-pre-line font-medium">{message}</div>, 
      duration: 3000,
    });
  }, [toast]);

  // Auth & Initial Data Loading
  useEffect(() => {
    const initAuth = async () => {
        const token = localStorage.getItem('aviato_token');
        if (token) {
            try {
                const { data } = await api.get('/auth/me');
                setCurrentUser(data);
                // Also fetch initial data immediately
                fetchData();
            } catch (e) {
                console.error("Auth check failed", e);
                localStorage.removeItem('aviato_token');
            }
        }
        setLoading(false);
    };
    initAuth();
  }, []);

  const fetchData = async () => {
    try {
        const [usersRes, convRes] = await Promise.all([
            api.get('/users'),
            api.get('/conversations')
        ]);
        setUsers(usersRes.data);
        setConversations(convRes.data);
    } catch (e) {
        console.error("Failed to fetch data", e);
    }
  };

  // Poll for updates (simple real-time simulation)
  useEffect(() => {
      if (currentUser) {
          const interval = setInterval(fetchData, 3000); // 3 seconds polling
          return () => clearInterval(interval);
      }
  }, [currentUser]);


  // Theme Handling
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);


  const login = async (email, password) => {
    try {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        
        const { data } = await api.post('/auth/login', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        localStorage.setItem('aviato_token', data.access_token);
        setCurrentUser(data.user);
        
        // Start background fetch and show loading screen
        setDataLoading(true);
        // Artificial delay for better UX + data fetch
        fetchData().then(() => {
            setTimeout(() => setDataLoading(false), 1500);
        });
        
        return true;
    } catch (error) {
        console.error(error);
        let msg = error.response?.data?.detail || "Login failed";
        if (typeof msg === 'object') msg = JSON.stringify(msg);
        showToast(msg, "error");
        return false;
    }
  };

  const signup = async (name, email, password) => {
    try {
        const { data } = await api.post('/auth/signup', { name, email, password });
        localStorage.setItem('aviato_token', data.access_token);
        setCurrentUser(data.user);
        
        // Start background fetch and show loading screen
        setDataLoading(true);
        fetchData().then(() => {
            setTimeout(() => setDataLoading(false), 1500);
        });

        return true;
    } catch (error) {
        console.error(error);
        let msg = error.response?.data?.detail || "Signup failed";
        if (typeof msg === 'object') msg = JSON.stringify(msg);
        showToast(msg, "error");
        return false;
    }
  };

  const logout = () => {
    setCurrentUser(null);
    setConversations([]);
    setCurrentSelections([]);
    localStorage.removeItem('aviato_token');
    // localStorage.removeItem('aviato_current_user'); // Legacy cleanup
  };

  const deleteAllChats = () => setConversations([]); // Client-side only for now?

  const addSelection = (item) => {
    if (!currentSelections.includes(item)) {
      setCurrentSelections(prev => [...prev, item]);
    }
  };

  const setSelections = (items) => {
    setCurrentSelections(items);
  };

  const removeSelection = (item) => {
    setCurrentSelections(currentSelections.filter(i => i !== item));
  };
  
  const clearSelections = () => setCurrentSelections([]);

  const findMatches = () => {
    return users.map(user => ({
      ...user,
      matchPercentage: calculateMatchPercentage(currentSelections, user.selections)
    })).sort((a, b) => b.matchPercentage - a.matchPercentage);
  };

  // --- CHAT LOGIC ---

  const startChat = async (userId) => {
    try {
        await api.post('/conversations/start', { userId });
        await fetchData();
    } catch (e) {
        console.error(e);
    }
  };

  // Explicit timer update not needed for Wall Clock
  const updateConversationTimer = useCallback(() => {}, []);

  const sendMessage = async (userId, text) => {
    if (!currentUser) return;
    try {
        // Optimistic Update for Conversations
        const tempId = Date.now().toString();
        
        // Check if this is the first message to handle Orange Mode counter optimistically
        const targetConversation = conversations.find(c => c.userId === userId);
        const isFirstMessage = !targetConversation || !targetConversation.messages || targetConversation.messages.length === 0;

        // If it's the first message and target is Orange Mode, increment their count locally
        let previousUsersState = null;
        if (isFirstMessage) {
            setUsers(prevUsers => {
                previousUsersState = prevUsers; // Capture for rollback
                return prevUsers.map(u => {
                    if (u.id === userId && u.availabilityMode === 'orange') {
                        const current = u.availability?.currentContacts || 0;
                        const max = u.availability?.maxContact || 0;
                        // Don't increment if already at/over max (UI protection)
                        if (current >= max) return u; 
                        
                        return {
                            ...u,
                            availability: {
                                ...u.availability,
                                currentContacts: current + 1
                            }
                        };
                    }
                    return u;
                });
            });
        }

        setConversations(prev => {
            const updated = prev.map(c => {
                if (c.userId === userId) {
                    return {
                        ...c,
                        messages: [...c.messages, {
                            id: tempId,
                            senderId: currentUser.id,
                            text,
                            timestamp: Date.now(),
                            read: false
                        }],
                        lastMessage: text,
                        lastMessageTime: Date.now()
                    };
                }
                return c;
            });
            // Sort by lastMessageTime descending
            return updated.sort((a, b) => b.lastMessageTime - a.lastMessageTime);
        });

        await api.post(`/conversations/${userId}/messages`, { text });
        
        // Slight delay to allow backend dynamic count to update in DB before refetching
        setTimeout(() => {
            fetchData();
        }, 500);
    } catch (e) {
        console.error(e);
        // Revert users state if failed (e.g. 403 Blocked) to prevent "3/2" display
        // Note: We can't easily use 'previousUsersState' here because it's inside the render cycle scope logic previously.
        // Instead, we just trigger fetchData to reset state from backend truth.
        await fetchData(); 
        
        let msg = "Failed to send message";
        if (e.response && e.response.status === 403) {
             msg = e.response.data.detail || "Limit reached";
        }
        showToast(msg, "error");
    }
  };
  
  // Receive message is now handled by polling fetchData, but we keep the function signature if needed
  const receiveMessage = () => {}; 
  
  const markConversationRated = (userId, isGood, reason = null) => {
      // Handled via rateConversation API
  };

  const updateUserApproval = useCallback((userId, change) => {
    // Handled by backend
  }, []);

  // CHAT RATING (Good/Bad)
  const rateConversation = useCallback(async (userId, isGood, reason = null) => {
    try {
        await api.post(`/conversations/${userId}/rate`, { isGood, reason });
        
        let change;
        if (isGood) {
            change = 10;
        } else {
             const penalties = {
                'No response / Ghosted': -15,
                'Rude or disrespectful': -20,
                'Spam messages': -25,
                'Inappropriate content': -30,
                'One-word answers': -10
             };
             change = reason ? (penalties[reason] || -10) : -10;
        }

        if (isGood) {
            showToast(`Rated positively! +${change}% approval`, 'success');
        } else {
            showToast(`Rated negatively: ${change}% approval`, 'error');
        }
        await fetchData();
    } catch (e) {
        console.error(e);
        showToast("Failed to submit rating", "error");
    }
  }, [showToast]);

  // REVIEW RATING (1-5 Stars)
  const submitReview = useCallback(async (userId, rating) => {
    if (!currentUser) return;
    try {
        const review = {
            raterId: currentUser.id,
            raterName: currentUser.name || "Anonymous",
            raterProfilePic: currentUser.profilePic,
            rating: rating,
            timestamp: Date.now()
        };
        await api.post(`/users/${userId}/reviews`, review);
        showToast(`Review submitted: ${rating} stars`, 'success');
        await fetchData();
    } catch (e) {
        console.error(e);
        showToast("Failed to submit review", "error");
    }
  }, [currentUser, showToast]);

  // Generic Profile Update
  const updateUserProfile = useCallback(async (updates) => {
    if (!currentUser) return;
    try {
        const { data } = await api.put(`/users/${currentUser.id}`, updates);
        setCurrentUser(data);
        setUsers(prev => prev.map(u => u.id === currentUser.id ? data : u));
        showToast('Profile updated', 'success');
    } catch (e) {
        console.error(e);
        showToast("Failed to update profile", "error");
    }
  }, [currentUser, showToast]);

  const updateProfilePic = (newUrl) => updateUserProfile({ profilePic: newUrl });
  const updateProfileName = (newName) => updateUserProfile({ name: newName });
  const updateProfileLocation = (newLocation) => updateUserProfile({ location: newLocation });
  const updateUserSelections = (newSelections) => updateUserProfile({ selections: newSelections });

  const getConversation = (userId) => conversations.find(c => c.userId === userId);
  const getUserById = (userId) => users.find(u => u.id === userId);

  const setAvailabilityMode = useCallback((mode, settings = {}) => {
    if (!currentUser) return;
    const { suppressToast, ...modeSettings } = settings;
    
    // Merge existing availability with new settings
    const newAvailability = { ...currentUser.availability, ...modeSettings };
    
    updateUserProfile({
        availabilityMode: mode,
        availability: newAvailability
    }).then(() => {
        if (!suppressToast) showToast('Mode updated', 'success');
    });

  }, [currentUser, updateUserProfile, showToast]);

  const getCurrentMode = (userId) => {
    const user = userId === currentUser?.id ? currentUser : users.find(u => u.id === userId);
    if (!user) return { displayMode: AvailabilityMode.GRAY, canMessage: false, statusText: "Unknown" };
    const status = checkUserAvailability(user);
    return { displayMode: user.availabilityMode, canMessage: status.available, statusText: status.statusText };
  };

  const value = {
    currentUser, isAuthenticated: !!currentUser, loading, dataLoading, login, signup, logout,
    users, getUserById, currentSelections, addSelection, removeSelection, clearSelections, findMatches,
    conversations, startChat, updateConversationTimer, sendMessage, receiveMessage, 
    markConversationRated, updateUserApproval, rateConversation, submitReview, getConversation, 
    updateProfilePic, updateProfileName, updateProfileLocation, updateUserProfile,
    setAvailabilityMode, getCurrentMode, theme, setTheme, deleteAllChats, showToast, setSelections, updateUserSelections,
    language, setLanguage, t 
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
