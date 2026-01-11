import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function ProfileSetRegulationPage() {
  const navigate = useNavigate();
  const { currentUser } = useAppContext();
  
  // Get current active mode
  const currentMode = currentUser?.availabilityMode || 'green';

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="px-4 py-3 flex items-center gap-3">
          <button 
            onClick={() => navigate('/settings')}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <h1 className="text-xl font-semibold text-gray-900">
            Profile Set Regulation
          </h1>
        </div>
      </div>

      {/* Title Section */}
      <div className="px-6 py-6 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Select Your Availability Mode
        </h2>
        <p className="text-gray-600">
          Control when people can message you
        </p>
      </div>

      {/* Current Mode Indicator (if any mode is active) */}
      {currentMode && (
        <div className="mx-4 mb-4 bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center text-2xl"
              style={{ backgroundColor: getModeColor(currentMode) }}
            >
              {getModeEmoji(currentMode)}
            </div>
            <div className="flex-1">
              <div className="text-sm text-gray-600">Currently Active:</div>
              <div className="font-semibold text-gray-900">
                {getModeName(currentMode)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mode Options List */}
      <div className="px-4 space-y-3">
        <ModeCard
          emoji="🔵"
          color="#0066FF"
          title="Open Mode"
          description="Available from specific date"
          isActive={currentMode === 'blue'}
          onClick={() => navigate('/profile/modes/blue')}
        />

        <ModeCard
          emoji="🟡"
          color="#FBBF24"
          title="Later Mode"
          description="Available for limited duration"
          isActive={currentMode === 'yellow'}
          onClick={() => navigate('/profile/modes/yellow')}
        />

        <ModeCard
          emoji="🟠"
          color="#F97316"
          title="Max Contact Mode"
          description="Limit number of contacts"
          isActive={currentMode === 'orange'}
          onClick={() => navigate('/profile/modes/orange')}
        />

        <ModeCard
          emoji="🟢"
          color="#10B981"
          title="Available Mode"
          description="Online and ready to chat"
          isActive={currentMode === 'green'}
          onClick={() => navigate('/profile/modes/green')}
        />

        <ModeCard
          emoji="🔴"
          color="#DC2626"
          title="Locked Mode"
          description="Completely unavailable"
          isActive={currentMode === 'red'}
          onClick={() => navigate('/profile/modes/red')}
        />

        <ModeCard
          emoji="⚪"
          color="#9CA3AF"
          title="Pause Mode"
          description="Temporarily paused"
          isActive={currentMode === 'gray'}
          onClick={() => navigate('/profile/modes/gray')}
        />

        {/* Brown Mode Removed */}
      </div>
    </div>
  );
}

// Mode Card Component
function ModeCard({ 
  emoji, 
  color, 
  title, 
  description, 
  isActive, 
  onClick 
}) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full bg-white rounded-xl p-4 flex items-center gap-4
        border-2 transition-all cursor-pointer
        ${isActive 
          ? 'border-blue-500 shadow-md' 
          : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
        }
      `}
    >
      <div 
        className="w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
        style={{ backgroundColor: color + '20' }}
      >
        {emoji}
      </div>
      
      <div className="flex-1 text-left">
        <div className="font-semibold text-gray-900 text-base flex items-center gap-2">
          {title}
          {isActive && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
              Active
            </span>
          )}
        </div>
        <div className="text-sm text-gray-600 mt-0.5">
          {description}
        </div>
      </div>
      
      <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
    </button>
  );
}

// Helper functions
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

function getModeName(mode) {
  const names = {
    blue: 'Open Mode',
    yellow: 'Later Mode',
    orange: 'Max Contact Mode',
    green: 'Available Mode',
    red: 'Locked Mode',
    gray: 'Pause Mode',
    brown: 'Timed Mode'
  };
  return names[mode] || 'Available Mode';
}
