import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';
import { ChevronLeft, Info, Check } from 'lucide-react';
import { AvailabilityMode } from '../../data/mockData';
import Counter from '../../components/common/Counter';

export default function OrangeModeSettings() {
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser, showToast } = useAppContext();
  
  const wasActive = currentUser?.availabilityMode === AvailabilityMode.ORANGE;
  const currentSettings = currentUser?.availability?.maxContact || 5;
  const currentContacts = currentUser?.availability?.currentContacts || 0;
  
  const [maxContacts, setMaxContacts] = useState(wasActive ? currentSettings : 5);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (wasActive) {
      setMaxContacts(currentSettings);
    }
  }, [wasActive, currentSettings]);

  const handleActivate = () => {
    setAvailabilityMode(AvailabilityMode.ORANGE, { 
      maxContact: maxContacts,
      suppressToast: true 
    });
    
    showToast(`✅ Orange Mode Activated!\nMax contacts set to ${maxContacts} ${maxContacts === 1 ? 'person' : 'people'}`, 'success');
    navigate('/profile');
  };

  const handleUpdate = () => {
    setAvailabilityMode(AvailabilityMode.ORANGE, { 
      maxContact: maxContacts,
      suppressToast: true
    });
    
    showToast(`✅ Max Contacts Updated!\nNew limit: ${maxContacts} ${maxContacts === 1 ? 'person' : 'people'}`, 'success');
    setIsEditing(false);
  };

  const handleDeactivate = () => {
    setAvailabilityMode(AvailabilityMode.GREEN, {
      suppressToast: true
    });
    showToast(`✅ Orange Mode Deactivated!\nYou are now Available (Green mode)`, 'success');
    navigate('/profile');
  };

  const slotsAvailable = Math.max(0, maxContacts - currentContacts);
  const isAtLimit = currentContacts >= maxContacts;

  // VIEW: Active Display
  if (wasActive && !isEditing) {
    return (
      <div className="min-h-screen bg-gray-50 pb-24">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
          <div className="px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => navigate('/profile')} className="p-2 hover:bg-gray-100 rounded-full">
                <ChevronLeft className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-semibold">Max Contact Mode</h1>
            </div>
            
            <div className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white rounded-full shadow-sm">
              <Check className="w-3 h-3" />
              <span className="text-xs font-bold uppercase tracking-wide">Toggle: ON</span>
            </div>
          </div>
        </div>

        <div className="p-4 space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="p-4 bg-orange-50 border-b border-orange-100 flex items-center gap-2">
               <Check className="w-5 h-5 text-orange-600" />
               <span className="font-semibold text-orange-900">Active</span>
            </div>
            
            <div className="p-5 space-y-4">
              <div className="flex justify-between items-center border-b border-gray-100 pb-3">
                <span className="text-gray-600">Max contacts allowed:</span>
                <span className="font-bold text-xl text-orange-600">{currentSettings}</span>
              </div>
              
              <div className="flex justify-between items-center border-b border-gray-100 pb-3">
                <span className="text-gray-600">Currently chatting with:</span>
                <span className="font-bold text-xl text-gray-900">{currentContacts}</span>
              </div>
              
              <div className="pt-1">
                {isAtLimit ? (
                   <div className="text-red-600 font-bold flex items-center gap-2">
                     <span>📊</span>
                     <span>LIMIT REACHED</span>
                   </div>
                ) : (
                   <div className="text-green-600 font-medium flex items-center gap-2">
                     <span>📊</span>
                     <span>You have {slotsAvailable} {slotsAvailable === 1 ? 'slot' : 'slots'} available</span>
                   </div>
                )}
              </div>
            </div>
          </div>
          
          {isAtLimit && (
             <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
                <Info className="w-5 h-5 text-red-700 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-900 font-medium">
                  ⚠️ Auto-switched to Pause mode
                </p>
             </div>
          )}

          <div className="space-y-3 mt-6">
            <button
              onClick={() => {
                setMaxContacts(currentSettings);
                setIsEditing(true);
              }}
              className="w-full py-4 bg-white border-2 border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all"
            >
              Edit Settings
            </button>
            
            <button
              onClick={handleDeactivate}
              className="w-full py-4 bg-red-50 text-red-600 border border-red-100 rounded-xl font-semibold hover:bg-red-100 transition-all"
            >
              Deactivate
            </button>
          </div>
        </div>
      </div>
    );
  }

  // VIEW: Settings / Editing
  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => isEditing ? setIsEditing(false) : navigate('/profile')} className="p-2 hover:bg-gray-100 rounded-full">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-semibold">
              {isEditing ? 'Edit Max Contact Mode' : 'Profile Set Regulation'}
            </h1>
          </div>
        </div>
      </div>

      <div className="p-6">
        <h2 className="text-2xl font-bold mb-2 text-gray-900">
          🟠 {isEditing ? 'Edit Limit' : 'Max Contact Mode'}
        </h2>
        
        {!isEditing && (
          <p className="text-gray-600 mb-8">
            Limit the number of people who can message you at once
          </p>
        )}

        {isEditing && (
           <div className="mb-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
             <div className="text-sm text-gray-500 mb-1">Current limit: <span className="font-bold text-gray-900">{currentSettings}</span></div>
             <div className="text-sm text-gray-500">Currently chatting with: <span className="font-bold text-gray-900">{currentContacts} people</span></div>
           </div>
        )}

        <div className="mb-8 flex flex-col items-center">
          <Counter
             label={isEditing ? 'New Maximum Contacts' : 'Maximum Contacts'}
             value={maxContacts}
             onChange={setMaxContacts}
             min={1}
             max={10000}
          />
          <p className="text-sm text-gray-500 mt-4 text-center">
             💡 When limit is reached, messaging will automatically pause
          </p>
        </div>

        <div className="flex gap-3">
          <button 
            onClick={() => isEditing ? setIsEditing(false) : navigate('/profile')}
            className="flex-1 px-6 py-4 border-2 border-gray-200 rounded-xl hover:bg-gray-50 font-semibold text-gray-700"
          >
            Cancel
          </button>
          <button 
            onClick={isEditing ? handleUpdate : handleActivate}
            className="flex-1 px-6 py-4 bg-orange-500 text-white rounded-xl hover:bg-orange-600 font-semibold shadow-md"
          >
            {isEditing ? 'Update' : 'Activate'}
          </button>
        </div>
      </div>
    </div>
  );
}
