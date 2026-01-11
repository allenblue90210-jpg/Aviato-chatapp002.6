
import React, { useState } from 'react';
import { X, ThumbsUp, ThumbsDown, CheckCircle, Star } from 'lucide-react';
import { Button } from '../ui/button';

const BAD_REPLY_REASONS = [
  { label: 'No response / Ghosted', penalty: -15 },
  { label: 'Rude or disrespectful', penalty: -20 },
  { label: 'Spam messages', penalty: -25 },
  { label: 'Inappropriate content', penalty: -30 },
  { label: 'One-word answers', penalty: -10 }
];

const RatingModal = ({ 
  userName, 
  onRate, // For Chat: (isGood, reason) => void; For Review: (rating) => void
  onClose,
  onGoBack,
  isOpen,
  type = 'chat', // 'chat' | 'review'
  title
}) => {
  const [showReasonSelector, setShowReasonSelector] = useState(false);
  const [selectedReason, setSelectedReason] = useState(null);
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [showSuccess, setShowSuccess] = useState(false);

  if (!isOpen) return null;

  const handleCancel = () => {
    setShowReasonSelector(false);
    setSelectedReason(null);
    onClose();
  };

  // Success Screen
  if (showSuccess) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl max-w-sm w-full p-6 animate-in fade-in zoom-in duration-200">
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-lg font-bold text-gray-900 mb-1">Thanks!</h2>
            <p className="text-sm text-gray-600 mb-4">
               {type === 'review' ? `You rated ${userName} ${rating} stars.` : 'Feedback submitted.'}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={onClose}
                className="flex-1"
              >
                Close
              </Button>
              {onGoBack && (
                <Button
                  onClick={() => {
                    onClose();
                    onGoBack();
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Go Back
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- REVIEW MODE (Stars) ---
  if (type === 'review') {
    return (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={(e) => {
            if (e.target === e.currentTarget) onClose();
          }}
        >
          <div className="bg-white rounded-xl max-w-sm w-full p-6 animate-in fade-in zoom-in duration-200 shadow-xl">
            <div className="text-center mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-2">{title || `Rate ${userName}`}</h2>
              <p className="text-sm text-gray-500">
                How was your experience with <span className="font-semibold text-gray-700">{userName}</span>?
              </p>
            </div>
    
            {/* Stars */}
            <div className="flex justify-center gap-2 mb-8">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className="transition-transform hover:scale-110 focus:outline-none"
                  onMouseEnter={() => setHoveredStar(star)}
                  onMouseLeave={() => setHoveredStar(0)}
                  onClick={() => setRating(star)}
                >
                  <Star 
                    className={`w-10 h-10 transition-colors duration-200 ${
                      star <= (hoveredStar || rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-200'
                    }`}
                  />
                </button>
              ))}
            </div>
    
            <div className="text-center h-6 mb-6">
              <span className="text-sm font-medium text-gray-600">
                {hoveredStar === 1 && "Terrible"}
                {hoveredStar === 2 && "Bad"}
                {hoveredStar === 3 && "Okay"}
                {hoveredStar === 4 && "Good"}
                {hoveredStar === 5 && "Excellent!"}
                {!hoveredStar && rating > 0 && (
                    <>
                        {rating === 1 && "Terrible"}
                        {rating === 2 && "Bad"}
                        {rating === 3 && "Okay"}
                        {rating === 4 && "Good"}
                        {rating === 5 && "Excellent!"}
                    </>
                )}
                {!hoveredStar && rating === 0 && "Tap a star to rate"}
              </span>
            </div>
    
            <div className="flex gap-3">
                <Button 
                    variant="ghost" 
                    className="flex-1 text-gray-500 hover:text-gray-700"
                    onClick={onClose}
                >
                    Cancel
                </Button>
                <Button 
                    className={`flex-1 ${rating > 0 ? 'bg-mode-blue text-white' : 'bg-gray-100 text-gray-400'}`}
                    disabled={rating === 0}
                    onClick={() => {
                        onRate(rating);
                        setShowSuccess(true);
                    }}
                >
                    Submit
                </Button>
            </div>
          </div>
        </div>
      );
  }

  // --- CHAT MODE (Good/Bad Reply) ---
  
  // Sub-screen: Bad Reply Reason Selector
  if (showReasonSelector) {
    return (
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={(e) => {
          if (e.target === e.currentTarget) handleCancel();
        }}
      >
        <div className="bg-white rounded-xl max-w-sm w-full p-4 animate-in fade-in zoom-in duration-200">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold text-gray-900">Select reason</h2>
            <button
              onClick={() => setShowReasonSelector(false)}
              className="text-gray-400 hover:text-gray-600 p-1"
              type="button"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-2 mb-3">
            {BAD_REPLY_REASONS.map((reason) => (
              <button
                key={reason.label}
                onClick={() => setSelectedReason(reason.label)}
                type="button"
                className={`w-full p-2.5 rounded-lg border text-left text-sm transition-all ${
                  selectedReason === reason.label
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{reason.label}</span>
                  <span className="text-xs text-red-600 font-semibold">
                    {reason.penalty}%
                  </span>
                </div>
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setShowReasonSelector(false)}
              type="button"
              className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 active:bg-gray-100 transition-colors"
            >
              Back
            </button>
            <button
              onClick={() => {
                if (selectedReason) {
                  onRate(false, selectedReason);
                  setShowSuccess(true);
                }
              }}
              type="button"
              disabled={!selectedReason}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedReason
                  ? 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main Screen: Good vs Bad
  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white rounded-xl max-w-sm w-full p-5 animate-in fade-in zoom-in duration-200">
        <div className="text-center mb-4">
          <h2 className="text-lg font-bold text-gray-900 mb-1">{title || "Timer Expired!"}</h2>
          <p className="text-sm text-gray-600">Rate this conversation</p>
        </div>

        <div className="flex gap-3">
          {/* Good Reply Button */}
          <button
            onClick={() => {
              onRate(true);
              setShowSuccess(true);
            }}
            type="button"
            className="flex-1 p-4 rounded-lg border-2 border-green-200 hover:border-green-500 hover:bg-green-50 active:bg-green-100 transition-all"
          >
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <ThumbsUp className="w-5 h-5 text-green-600" />
            </div>
            <span className="text-sm font-semibold text-gray-900 block">Good reply</span>
            <p className="text-xs text-green-600 mt-1">+10%</p>
          </button>

          {/* Bad Reply Button */}
          <button
            onClick={() => setShowReasonSelector(true)}
            type="button"
            className="flex-1 p-4 rounded-lg border-2 border-red-200 hover:border-red-500 hover:bg-red-50 active:bg-red-100 transition-all"
          >
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <ThumbsDown className="w-5 h-5 text-red-600" />
            </div>
            <span className="text-sm font-semibold text-gray-900 block">Bad reply</span>
            <p className="text-xs text-red-600 mt-1">-10 to -30%</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RatingModal;
