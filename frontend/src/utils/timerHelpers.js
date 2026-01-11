/**
 * Timer and Rating System Utilities
 * Implements the 5-hour timer with turn-based response tracking
 */

const FIVE_HOURS = 5 * 60 * 60 * 1000; // 5 hours in milliseconds

/**
 * Check if timer has expired and determine if rating should be shown
 * @param {Object} conversation - The conversation object
 * @param {string} currentUserId - ID of the current user
 * @returns {Object} - {expired, shouldShowRating, reason}
 */
export function checkTimerExpiry(conversation, currentUserId) {
  if (!conversation || !conversation.timerStarted) {
    return { expired: false, shouldShowRating: false, reason: '' };
  }

  const elapsed = Date.now() - conversation.timerStarted;
  const isExpired = elapsed >= FIVE_HOURS;

  if (!isExpired) {
    return { expired: false, shouldShowRating: false, reason: '' };
  }

  // Timer expired - check if we should show rating
  
  // RULE 1: Only show rating if YOU sent the last message
  // RULE 2: Only show rating if THEY haven't responded yet
  
  const youSentLast = conversation.lastMessageSenderId === currentUserId;
  const waitingForTheirResponse = conversation.waitingForResponse === true;
  
  if (youSentLast && waitingForTheirResponse && !conversation.theyRespondedLast) {
    return {
      expired: true,
      shouldShowRating: true,
      reason: 'The other person did not respond to your last message'
    };
  }

  // Timer expired but no rating needed
  if (!youSentLast) {
    return {
      expired: true,
      shouldShowRating: false,
      reason: 'Your turn to respond'
    };
  }

  if (conversation.theyRespondedLast) {
    return {
      expired: true,
      shouldShowRating: false,
      reason: 'They already responded'
    };
  }

  return { expired: true, shouldShowRating: false, reason: 'No rating needed' };
}

/**
 * Calculate remaining time for timer display
 * @param {number} timerStarted - Timestamp when timer started
 * @returns {number} - Remaining time in milliseconds (or 0 if expired)
 */
export function calculateRemainingTime(timerStarted) {
  if (!timerStarted) return 0;
  
  const elapsed = Date.now() - timerStarted;
  const remaining = FIVE_HOURS - elapsed;
  
  return Math.max(0, remaining);
}

/**
 * Format remaining time as HH:MM:SS
 * @param {number} milliseconds - Time in milliseconds
 * @returns {string} - Formatted time string
 */
export function formatRemainingTime(milliseconds) {
  if (milliseconds <= 0) return '00:00:00';
  
  const hours = Math.floor(milliseconds / (60 * 60 * 1000));
  const minutes = Math.floor((milliseconds % (60 * 60 * 1000)) / (60 * 1000));
  const seconds = Math.floor((milliseconds % (60 * 1000)) / 1000);
  
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Check if mode change should trigger rating prompt
 * @param {Object} conversation - The conversation object
 * @param {string} currentUserId - ID of the current user
 * @param {string} oldMode - Previous availability mode
 * @param {string} newMode - New availability mode
 * @returns {Object} - {shouldShowRating, reason}
 */
export function checkModeChangeRating(conversation, currentUserId, oldMode, newMode) {
  // Check if user became unavailable (Red or Gray mode)
  const unavailableModes = ['red', 'gray'];
  const becameUnavailable = unavailableModes.includes(newMode) && !unavailableModes.includes(oldMode);
  
  if (!becameUnavailable) {
    return { shouldShowRating: false, reason: '' };
  }

  // Check if YOU were waiting for THEIR response
  const youSentLast = conversation.lastMessageSenderId === currentUserId;
  const waitingForTheirResponse = conversation.waitingForResponse === true;
  
  if (youSentLast && waitingForTheirResponse && !conversation.theyRespondedLast) {
    const modeText = newMode === 'red' ? 'locked' : 'paused';
    return {
      shouldShowRating: true,
      reason: `User ${modeText} their account before replying to your message`
    };
  }

  return { shouldShowRating: false, reason: '' };
}

/**
 * Get rating penalties for bad reply reasons
 * @returns {Array} - Array of {label, penalty} objects
 */
export function getBadReplyReasons() {
  return [
    { label: 'No response / Ghosted', penalty: -15 },
    { label: 'Rude or disrespectful', penalty: -20 },
    { label: 'Spam messages', penalty: -25 },
    { label: 'Inappropriate content', penalty: -30 },
    { label: 'One-word answers', penalty: -10 }
  ];
}

/**
 * Calculate penalty for a bad reply reason
 * @param {string} reason - The reason label
 * @returns {number} - Penalty value (negative number)
 */
export function getPenaltyForReason(reason) {
  const reasons = getBadReplyReasons();
  const match = reasons.find(r => r.label === reason);
  return match ? match.penalty : -10; // Default to -10 if not found
}
