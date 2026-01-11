
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

const EditNameDialog = ({ isOpen, onClose, currentName, onSave }) => {
  const [name, setName] = useState(currentName || '');
  const [error, setError] = useState('');

  const handleSave = () => {
    if (!name.trim()) {
      setError('Name cannot be empty');
      return;
    }
    if (name.length > 30) {
      setError('Name must be less than 30 characters');
      return;
    }
    onSave(name);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-white">
        <DialogHeader>
          <DialogTitle>Edit Name</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Display Name</Label>
            <Input 
              id="name"
              value={name}
              onChange={(e) => {
                  setName(e.target.value);
                  setError('');
              }}
              placeholder="Your name"
              autoFocus
            />
            <p className="text-xs text-gray-500">
              This is how you will appear to other users.
            </p>
          </div>
          
          {error && <p className="text-sm text-red-500">{error}</p>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave} className="bg-mode-blue text-white">Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EditNameDialog;
