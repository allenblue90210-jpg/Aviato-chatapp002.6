import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';
import { ChevronLeft, Check } from 'lucide-react';
import { AvailabilityMode } from '../../data/mockData';

export default function GreenModeSettings() {
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser } = useAppContext();

  const wasActive = currentUser?.availabilityMode === AvailabilityMode.GREEN;

  const handleActivate = () => {
    // No settings needed for green mode
    setAvailabilityMode(AvailabilityMode.GREEN, {});
    
    // Navigate back to profile
    navigate('/profile');
  };

  const handleDeactivate = () => {
    // Deactivating Green Mode -> Switch to Invisible (null)
    setAvailabilityMode(null, {});
    navigate('/profile');
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/profile')} className="p-2 hover:bg-gray-100 rounded-full">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-semibold">Available Mode</h1>
          </div>

          {/* Activation Status Badge */}
          {wasActive ? (
            <div className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white rounded-full shadow-sm">
              <Check className="w-3 h-3" />
              <span className="text-xs font-bold uppercase tracking-wide">ACTIVATED</span>
            </div>
          ) : (
            <div className="px-3 py-1 bg-gray-300 text-gray-600 rounded-full">
              <span className="text-xs font-bold uppercase tracking-wide">DEACTIVATED</span>
            </div>
          )}
        </div>
      </div>

      {/* Icon & Description */}
      <div className="px-6 py-12 text-center">
        <div className="w-24 h-24 mx-auto bg-green-100 rounded-full flex items-center justify-center text-6xl mb-6">
          🟢
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-3">
          Broadcast your online status
        </h2>
        <p className="text-gray-600 max-w-sm mx-auto">
          When active, you appear as "Online now" to everyone.
        </p>
        <p className="text-gray-500 text-sm mt-4">
          Deactivate to go Invisible 👻 (still receive messages, but appear offline).
        </p>
      </div>

      {/* Status Info */}
      <div className="mx-4 bg-green-50 border-2 border-green-200 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
            <Check className="w-6 h-6 text-white" />
          </div>
          <span className="text-lg font-semibold text-green-900">
            Visibility: Public
          </span>
        </div>
        <div className="space-y-2 text-green-900">
          <p>• You appear as "Online now"</p>
          <p>• Green dot visible on your profile</p>
          <p>• Best for getting immediate replies</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="px-4 mt-8 space-y-3">
        {/* Activate Button */}
        <button
          onClick={handleActivate}
          disabled={wasActive} // Already active, no params to update
          className={`
            w-full py-4 rounded-xl font-semibold shadow-md transition-all flex items-center justify-center gap-2
            ${wasActive 
               ? 'bg-green-600 text-white cursor-default' // Style as "Already Active"
               : 'bg-green-600 hover:bg-green-700 text-white hover:shadow-lg'
            }
          `}
        >
          <Check className="w-5 h-5" />
          {wasActive ? 'CURRENTLY ACTIVE' : 'ACTIVATE MODE'}
        </button>

        {/* Deactivate Button */}
        {wasActive && (
          <button
            onClick={handleDeactivate}
            className="w-full py-4 bg-gray-500 text-white rounded-xl font-semibold hover:bg-gray-600 transition-all shadow-sm"
          >
            DEACTIVATE (GO INVISIBLE)
          </button>
        )}
      </div>
    </div>
  );
}
