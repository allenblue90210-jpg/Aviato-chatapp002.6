import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Button } from "../ui/button";

export default function ModeInfoDialog({ isOpen, onClose }) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md bg-white rounded-xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Profile Set Regulation</DialogTitle>
        </DialogHeader>
        
        <div className="flex flex-col gap-4 py-4">
          <p className="text-sm text-gray-600 mb-2">
            Mode Rules & Information
          </p>
          
          <ModeInfoItem
            icon="🔵"
            name="Open Mode"
            description="Set a future date when you'll become available. This is the starting point of your availability chain."
          />
          
          <ModeInfoItem
            icon="🟡"
            name="Later Mode"
            description="Set a duration for availability (e.g., 2 hours). Activates after Open Mode date arrives."
          />
          
          <ModeInfoItem
            icon="🟠"
            name="Max Contact Mode"
            description="Limit the number of contacts (e.g., max 5 people). Auto-switches when limit is reached."
          />
          
          <ModeInfoItem
            icon="🟢"
            name="Available Mode"
            description="Online and ready to chat. This is the final permanent state after all modes complete."
          />
          
          <ModeInfoItem
            icon="🔴"
            name="Locked Mode"
            description="Completely unavailable. Cancels all scheduled modes and locks messaging indefinitely."
          />
          
          <ModeInfoItem
            icon="⚪"
            name="Pause Mode"
            description="Temporarily paused. Cancels all scheduled modes until you unpause manually."
          />
          
          {/* Timed Mode Removed */}
          
          {/* How it works section */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
            <h3 className="font-semibold mb-2 text-blue-900">How Sequential Chain Works:</h3>
            <ol className="text-sm space-y-1 text-blue-800">
              <li>1. Set Open Mode (required first step)</li>
              <li>2. Optional: Add Later Mode</li>
              <li>3. Optional: Add Max Contact Mode</li>
              <li>4. System auto-switches to Available</li>
            </ol>
            <p className="text-xs text-blue-700 mt-3 font-medium">
              Note: Locked/Pause modes cancel all other modes
            </p>
          </div>
          
          <Button 
            onClick={onClose}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white mt-4"
          >
            Got It
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function ModeInfoItem({ icon, name, description }) {
  return (
    <div className="p-3 border border-gray-200 rounded-lg bg-gray-50/50">
      <div className="flex items-start gap-3">
        <span className="text-2xl mt-0.5">{icon}</span>
        <div>
          <h4 className="font-medium text-gray-900 text-sm">{name}</h4>
          <p className="text-xs text-gray-500 mt-1 leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );
}
