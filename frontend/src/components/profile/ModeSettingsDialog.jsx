import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../ui/dialog";
import { Button } from "../ui/button";
import Counter from "../common/Counter";
import { AvailabilityMode } from "../../data/mockData";
import { useAppContext } from "../../contexts/AppContext";
import { Calendar } from 'lucide-react';

export default function ModeSettingsDialog({ mode, isOpen, onClose }) {
  const { setAvailabilityMode, currentUser, showToast } = useAppContext();
  
  const [maxContacts, setMaxContacts] = useState(5);
  const [duration, setDuration] = useState(60);
  const [hour, setHour] = useState(16);
  const [minute, setMinute] = useState(0);
  const [date, setDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);

  // Reset state when opening or mode changes
  useEffect(() => {
    if (isOpen && currentUser) {
      const avail = currentUser.availability || {};
      
      if (mode === AvailabilityMode.ORANGE) {
         setMaxContacts(avail.maxContact || 5);
      } else if (mode === AvailabilityMode.YELLOW) {
         setDuration(avail.laterMinutes || 60);
      } else if (mode === AvailabilityMode.BROWN) {
         setHour(avail.timedHour ?? 16);
         setMinute(avail.timedMinute ?? 0);
      } else if (mode === AvailabilityMode.BLUE) {
         if (avail.openDate) {
             setDate(new Date(avail.openDate));
         } else {
             const d = new Date();
             d.setDate(d.getDate() + 1);
             setDate(d);
         }
      }
    }
  }, [isOpen, mode, currentUser]);

  const handleSave = () => {
    if (mode === AvailabilityMode.ORANGE) {
        setAvailabilityMode(AvailabilityMode.ORANGE, { maxContact: maxContacts, suppressToast: true });
        showToast(`✅ Orange Mode is now ACTIVE!\nMax contacts set to ${maxContacts}`, 'success');
    } else if (mode === AvailabilityMode.YELLOW) {
        setAvailabilityMode(AvailabilityMode.YELLOW, { laterMinutes: duration, laterStartTime: Date.now(), suppressToast: true });
        showToast(`✅ Yellow Mode is now ACTIVE!\nExpires in ${duration} minutes`, 'success');
    } else if (mode === AvailabilityMode.BROWN) {
        setAvailabilityMode(AvailabilityMode.BROWN, { timedHour: hour, timedMinute: minute, suppressToast: true });
        const timeStr = `${hour > 12 ? hour - 12 : hour || 12}:${String(minute).padStart(2,'0')} ${hour >= 12 ? 'PM' : 'AM'}`;
        showToast(`✅ Brown Mode is now ACTIVE!\nOpens at ${timeStr}`, 'success');
    } else if (mode === AvailabilityMode.BLUE) {
        setAvailabilityMode(AvailabilityMode.BLUE, { openDate: date.toISOString().split('T')[0], suppressToast: true });
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        showToast(`✅ Blue Mode is now ACTIVE!\nOpens ${dateStr}`, 'success');
    }
    
    onClose();
  };

  const getModeName = () => {
      switch(mode) {
          case AvailabilityMode.ORANGE: return "Max Contact Settings";
          case AvailabilityMode.YELLOW: return "Later Mode Settings";
          case AvailabilityMode.BROWN: return "Timed Mode Settings";
          case AvailabilityMode.BLUE: return "Open Mode Settings";
          default: return "Settings";
      }
  };

  const renderContent = () => {
      if (mode === AvailabilityMode.ORANGE) {
          return (
              <div className="flex flex-col items-center py-4">
                  <div className="text-muted-foreground mb-4">Maximum Contacts</div>
                  <Counter 
                      value={maxContacts} 
                      onChange={setMaxContacts} 
                      min={1} 
                      max={1000}
                  />
              </div>
          );
      }
      if (mode === AvailabilityMode.YELLOW) {
          const getStep = (v) => v < 60 ? 5 : v < 120 ? 15 : 30;
          return (
              <div className="flex flex-col items-center py-4">
                  <div className="text-muted-foreground mb-4">Duration (minutes)</div>
                  <Counter 
                      value={duration} 
                      onChange={setDuration}
                      onIncrement={() => setDuration(d => Math.min(1440, d + getStep(d)))}
                      onDecrement={() => {
                          const step = duration <= 60 ? 5 : duration <= 120 ? 15 : 30;
                          setDuration(d => Math.max(5, d - step));
                      }}
                      min={5}
                      max={1440}
                  />
              </div>
          );
      }
      if (mode === AvailabilityMode.BROWN) {
          return (
              <div className="flex flex-col items-center py-4 gap-6">
                  <div>
                    <div className="text-muted-foreground mb-2 text-center">Hour</div>
                    <Counter 
                        value={hour} 
                        onChange={setHour}
                        onIncrement={() => setHour(h => h === 23 ? 0 : h + 1)}
                        onDecrement={() => setHour(h => h === 0 ? 23 : h - 1)}
                        displayValue={`${hour > 12 ? hour - 12 : hour || 12} ${hour >= 12 ? 'PM' : 'AM'}`}
                    />
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-2 text-center">Minute</div>
                    <Counter 
                        value={minute} 
                        onChange={setMinute}
                        onIncrement={() => setMinute(m => m >= 45 ? 0 : m + 15)}
                        onDecrement={() => setMinute(m => m <= 0 ? 45 : m - 15)}
                        displayValue={String(minute).padStart(2, '0')}
                    />
                  </div>
                  <div className="text-sm font-medium text-foreground">
                      Available at: {hour > 12 ? hour - 12 : hour || 12}:{String(minute).padStart(2,'0')} {hour >= 12 ? 'PM' : 'AM'}
                  </div>
              </div>
          );
      }
      if (mode === AvailabilityMode.BLUE) {
          return (
              <div className="flex flex-col items-center py-4">
                  <div className="text-muted-foreground mb-4">Available from date</div>
                  <Counter
                      value={0}
                      onChange={() => {}}
                      onIncrement={() => {
                          const next = new Date(date);
                          next.setDate(next.getDate() + 1);
                          setDate(next);
                      }}
                      onDecrement={() => {
                          const prev = new Date(date);
                          prev.setDate(prev.getDate() - 1);
                          // Don't allow past
                          const today = new Date();
                          today.setHours(0,0,0,0);
                          if (prev >= today) setDate(prev);
                      }}
                      displayValue={date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  />
                  <button 
                      onClick={() => setShowDatePicker(!showDatePicker)}
                      className="mt-4 flex items-center gap-2 text-sm text-primary"
                  >
                      <Calendar className="w-4 h-4" /> Pick from Calendar
                  </button>
                  {showDatePicker && (
                      <input 
                          type="date" 
                          className="mt-2 border border-border rounded p-2 bg-background text-foreground"
                          value={date.toISOString().split('T')[0]}
                          onChange={(e) => {
                              if (e.target.value) {
                                  setDate(new Date(e.target.value));
                                  setShowDatePicker(false);
                              }
                          }}
                          min={new Date().toISOString().split('T')[0]}
                      />
                  )}
              </div>
          );
      }
      return null;
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md bg-card rounded-xl border border-border">
        <DialogHeader>
          <DialogTitle className="text-center text-foreground">{getModeName()}</DialogTitle>
        </DialogHeader>
        
        {renderContent()}

        <DialogFooter className="flex-row gap-2 justify-end">
          <Button variant="outline" onClick={onClose} className="flex-1 border-border text-foreground hover:bg-accent">Cancel</Button>
          <Button onClick={handleSave} className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground">Done</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
