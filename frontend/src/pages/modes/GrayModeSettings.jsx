import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';
import { ChevronLeft, PauseCircle, Check } from 'lucide-react';
import { AvailabilityMode } from '../../data/mockData';

export default function GrayModeSettings() {
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser } = useAppContext();
  const [showConfirmation, setShowConfirmation] = useState(false);

  const wasActive = currentUser?.availabilityMode === AvailabilityMode.GRAY;

  const handleActivate = () => {
    setShowConfirmation(true);
  };

  const confirmPause = () => {
    setAvailabilityMode(AvailabilityMode.GRAY, {});
    setShowConfirmation(false);
    navigate('/profile');
  };

  const handleDeactivate = () => {
    setAvailabilityMode(AvailabilityMode.GREEN, {});
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
            <h1 className="text-xl font-semibold">Pause Mode</h1>
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

      {/* Warning Section */}
      <div className="px-6 py-8">
        <div className="w-20 h-20 mx-auto bg-gray-100 rounded-full flex items-center justify-center text-5xl mb-6">
          ⚪
        </div>
        
        <div className="bg-gray-100 border-2 border-gray-300 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <PauseCircle className="w-6 h-6 text-gray-600 flex-shrink-0" />
            <h3 className="text-lg font-bold text-gray-900">PAUSED</h3>
          </div>
          <p className="text-gray-900 leading-relaxed">
            This will temporarily pause messaging.
          </p>
        </div>

        <p className="text-center text-gray-600 mb-6">
          Use this when you want to take a break.
        </p>

        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-3">Effects:</h4>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-gray-500">•</span>
              Messaging paused temporarily
            </li>
            <li className="flex items-start gap-2">
              <span className="text-gray-500">•</span>
              Profile shows &quot;Paused&quot; status
            </li>
          </ul>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="px-4 mt-8 space-y-3">
        {/* Activate Button */}
        <button
          onClick={handleActivate}
          className="w-full py-4 bg-gray-600 hover:bg-gray-700 text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
        >
          {wasActive ? (
            <>
              <Check className="w-5 h-5" />
              UPDATE PAUSE
            </>
          ) : (
            'PAUSE ACCOUNT'
          )}
        </button>

        {/* Deactivate Button */}
        {wasActive && (
          <button
            onClick={handleDeactivate}
            className="w-full py-4 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-all shadow-sm"
          >
            RESUME MESSAGING
          </button>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-xl">
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Pause your account?
            </h3>
            <p className="text-gray-600 mb-6">
              You won&apos;t be able to receive any messages until you resume.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmation(false)}
                className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={confirmPause}
                className="flex-1 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700"
              >
                Pause
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
