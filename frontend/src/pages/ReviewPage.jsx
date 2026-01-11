
import React, { useState } from 'react';
import { Search, Star, ChevronDown, ChevronUp, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import ModeIndicator from '../components/availability/ModeIndicator';
import RatingModal from '../components/chat/RatingModal';
import { useTranslation } from 'react-i18next';

import UserAvatar from '../components/common/UserAvatar';

const ReviewPage = () => {
  const navigate = useNavigate();
  const { users, currentUser, submitReview } = useAppContext();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [reviewsSearchTerm, setReviewsSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [expandedUserId, setExpandedUserId] = useState(null);
  
  // Filter users to only show those we've "chatted" with (mocked as all users for now minus self)
  // Logic moved inside component body for 'filteredUsers'
  const rateableUsers = users.filter(u => u.id !== currentUser?.id);

  const handleRateSubmit = (rating) => {
    if (selectedUser) {
        submitReview(selectedUser.id, rating);
    }
    setSelectedUser(null);
  };
  
  const toggleExpanded = (userId) => {
    setExpandedUserId(expandedUserId === userId ? null : userId);
    setReviewsSearchTerm(''); // Reset search when toggling
  };

  const handleRaterClick = (raterId) => {
    // Navigate to chat with this rater (unless it's self)
    if (raterId && raterId !== currentUser?.id) {
        navigate(`/chat/${raterId}`);
    }
  };

  const [filterTab, setFilterTab] = useState('all'); // 'all', 'rated', 'not_rated'
  // Calculate counts for tabs
  const allCount = rateableUsers.length;
  const ratedCount = rateableUsers.filter(u => u.reviews?.some(r => r.raterId === currentUser?.id)).length;
  const notRatedCount = rateableUsers.filter(u => !u.reviews?.some(r => r.raterId === currentUser?.id)).length;

  // Filter users
  const filteredUsers = rateableUsers.filter(user => {
    // Search Term Filter
    if (!user.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;

    // Tab Filter
    const hasRated = user.reviews?.some(r => r.raterId === currentUser?.id);
    if (filterTab === 'rated' && !hasRated) return false;
    if (filterTab === 'not_rated' && hasRated) return false;

    return true;
  });

  return (
    <div className="p-4 space-y-4 pb-20 bg-background min-h-screen">
      <h1 className="text-xl font-bold mb-4 text-foreground">{t('nav.review')}</h1>
      
      {/* Who Rated Me Section */}
      <div className="mb-6">
        <h2 className="text-lg font-bold text-foreground mb-2">Who Rated Me</h2>
        {currentUser?.reviews && currentUser.reviews.length > 0 ? (
            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                {currentUser.reviews.map((review, idx) => (
                    <div key={idx} className="bg-card border border-border rounded-lg p-3 min-w-[140px] shadow-sm flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                            <UserAvatar src={review.raterProfilePic} alt={review.raterName} className="w-8 h-8 rounded-full" size={16} />
                            <div className="flex flex-col overflow-hidden">
                                <span className="text-sm font-semibold truncate">{review.raterName}</span>
                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                    {review.rating} <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        ) : (
            <div className="p-4 bg-muted/30 border border-dashed border-border rounded-xl text-center">
                <p className="text-sm text-muted-foreground">No one has rated you yet.</p>
            </div>
        )}
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input 
          placeholder={t('review.search_placeholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-9 bg-muted border-border text-foreground"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        <Button 
            variant={filterTab === 'all' ? "default" : "outline"} 
            size="sm" 
            onClick={() => setFilterTab('all')}
            className="rounded-full h-8"
        >
            All users ({allCount})
        </Button>
        <Button 
            variant={filterTab === 'rated' ? "default" : "outline"} 
            size="sm" 
            onClick={() => setFilterTab('rated')}
            className="rounded-full h-8"
        >
            You rated ({ratedCount})
        </Button>
        <Button 
            variant={filterTab === 'not_rated' ? "default" : "outline"} 
            size="sm" 
            onClick={() => setFilterTab('not_rated')}
            className="rounded-full h-8"
        >
            Not rated ({notRatedCount})
        </Button>
      </div>

      <div className="space-y-3">
        {filteredUsers.map(user => {
          // Check if current user has already rated this user
          const hasRated = user.reviews?.some(r => r.raterId === currentUser?.id);
          const userReviews = user.reviews || [];

          return (
            <div key={user.id} className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
              <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <UserAvatar src={user.profilePic} alt={user.name} className="w-12 h-12 rounded-full" size={24} />
                    <ModeIndicator mode={user.availabilityMode} className="absolute -top-1 -right-1" size="small" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{user.name}</h3>
                    <div className="flex items-center gap-1 text-yellow-500">
                      <div className="flex">
                        {[1, 2, 3, 4, 5].map(star => (
                          <Star key={star} className={`w-3 h-3 ${star <= Math.round(user.reviewRating) ? 'fill-current' : 'text-muted'}`} />
                        ))}
                      </div>
                      <span className="text-xs text-muted-foreground font-medium">
                         {user.reviewRating}/5 • {user.reviewCount} rates
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                    {/* Show toggle if user has reviews (or if user has rated them) */}
                    {(userReviews.length > 0 || hasRated) && (
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground"
                            onClick={() => toggleExpanded(user.id)}
                        >
                            {expandedUserId === user.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </Button>
                    )}

                    <Button 
                      size="sm" 
                      variant={hasRated ? "secondary" : "outline"}
                      disabled={hasRated}
                      onClick={() => setSelectedUser(user)}
                      className={hasRated ? "bg-muted text-muted-foreground border-border" : "text-foreground hover:bg-accent"}
                    >
                      {hasRated ? t('review.rated') : t('review.rate')}
                    </Button>
                </div>
              </div>
              
              {/* Reviews List - Only visible if expanded AND (user has rated OR we decide to show always) */}
              {/* Requirement: "after i rate let it show the users that rate a person" -> Only show if hasRated is true? */}
              {/* Interpreting "only after i rate": If I haven't rated, I can't see who else rated. */}
              {expandedUserId === user.id && (
                  <div className="bg-muted/30 px-4 py-3 border-t border-border">
                      <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">{t('review.rated_by')}</h4>
                      {!hasRated ? (
                          <p className="text-sm text-muted-foreground italic">Rate this user to see who else has reviewed them.</p>
                      ) : (
                          <div className="space-y-2">
                              {/* Reviews Search Input */}
                              {userReviews.length > 0 && (
                                <div className="relative mb-3">
                                    <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                                    <Input
                                        placeholder={t('review.search_raters', { defaultValue: 'Search raters...' })}
                                        value={reviewsSearchTerm}
                                        onChange={(e) => setReviewsSearchTerm(e.target.value)}
                                        className="pl-8 h-9 text-sm bg-background"
                                    />
                                </div>
                              )}

                              {userReviews.length === 0 ? (
                                  <p className="text-sm text-muted-foreground italic">No reviews yet.</p>
                              ) : (
                                  userReviews
                                    .filter(r => 
                                        !reviewsSearchTerm || 
                                        r.raterName.toLowerCase().includes(reviewsSearchTerm.toLowerCase())
                                    )
                                    .map((review, idx) => (
                                      <div 
                                        key={idx} 
                                        onClick={() => handleRaterClick(review.raterId)}
                                        className={`flex justify-between items-center text-sm p-2 bg-card rounded-lg border border-border shadow-sm transition-colors ${
                                            review.raterId !== currentUser?.id ? 'cursor-pointer hover:bg-accent hover:border-primary/30' : ''
                                        }`}
                                      >
                                          <div className="flex items-center gap-2">
                                            <UserAvatar 
                                              src={review.raterProfilePic} 
                                              alt={review.raterName} 
                                              className="w-6 h-6 rounded-full"
                                              size={12}
                                            />
                                            <span className="text-foreground font-medium flex items-center gap-1.5">
                                                {review.raterId === currentUser?.id ? "You" : review.raterName}
                                                {review.raterId !== currentUser?.id && (
                                                    <MessageSquare className="w-3 h-3 text-muted-foreground opacity-50" />
                                                )}
                                            </span>
                                          </div>
                                          <div className="flex items-center gap-1">
                                              <span className="text-yellow-600 font-bold">{review.rating}</span>
                                              <Star className="w-3 h-3 text-yellow-500 fill-current" />
                                          </div>
                                      </div>
                                  ))
                              )}
                              
                              {/* Empty state for filtered search */}
                              {userReviews.length > 0 && userReviews.filter(r => !reviewsSearchTerm || r.raterName.toLowerCase().includes(reviewsSearchTerm.toLowerCase())).length === 0 && (
                                  <p className="text-sm text-muted-foreground italic text-center py-2">No matching reviews found.</p>
                              )}
                          </div>
                      )}
                  </div>
              )}
            </div>
          );
        })}

        {rateableUsers.length === 0 && (
          <div className="text-center py-10 text-muted-foreground">
            {t('review.no_users')}
          </div>
        )}
      </div>

      {selectedUser && (
        <RatingModal 
          isOpen={!!selectedUser} 
          onClose={() => setSelectedUser(null)}
          onRate={handleRateSubmit}
          userName={selectedUser.name}
          title={t('review.rate_user', { name: selectedUser.name })}
          type="review"
        />
      )}
    </div>
  );
};

export default ReviewPage;
