
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Upload, Image as ImageIcon, Link as LinkIcon, X, MapPin } from 'lucide-react';

import UserAvatar from '../common/UserAvatar';

const ProfilePicDialog = ({ isOpen, onClose, currentPic, currentName, currentLocation, onSave }) => {
  const [url, setUrl] = useState(currentPic || '');
  const [name, setName] = useState(currentName || '');
  const [location, setLocation] = useState(currentLocation || '');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'link'

  useEffect(() => {
    setUrl(currentPic || '');
    setName(currentName || '');
    setLocation(currentLocation || '');
  }, [currentPic, currentName, currentLocation, isOpen]);

  const handleSave = () => {
    // Allow empty URL (implies removing profile picture)
    // if (!url.trim()) { ... } -> Removed validation
    
    if (!name.trim()) {
        setError('Name cannot be empty');
        return;
    }
    if (!location.trim()) {
        setError('Location cannot be empty');
        return;
    }
    // If url is empty, send null to remove
    onSave(url.trim() || null, name, location);
    onClose();
  };

  const handleRemovePhoto = () => {
    setUrl('');
    setError('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
          setError("File size too large (max 5MB)");
          return;
      }
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setUrl(reader.result);
        setError('');
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-card p-0 overflow-hidden max-h-[90vh] flex flex-col border border-border">
        <DialogHeader className="p-4 border-b border-border flex flex-row items-center justify-between shrink-0 bg-card">
          <DialogTitle className="text-foreground">Edit Profile</DialogTitle>
        </DialogHeader>
        
        <div className="p-4 space-y-6 overflow-y-auto flex-1 bg-card">
          {/* Preview Section */}
          <div className="flex flex-col items-center gap-3">
             <div className="w-28 h-28 rounded-full overflow-hidden border-4 border-background shadow-lg ring-1 ring-border relative group bg-muted">
                <UserAvatar 
                    src={url} 
                    alt="Preview" 
                    className="w-full h-full"
                    size={48}
                />
                {url && (
                    <div 
                        onClick={handleRemovePhoto}
                        className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                    >
                        <span className="text-white font-medium text-xs flex items-center gap-1">
                            <X className="w-4 h-4" /> Remove
                        </span>
                    </div>
                )}
             </div>
             {url ? (
                 <button onClick={handleRemovePhoto} className="text-xs text-destructive hover:underline">
                    Remove Photo
                 </button>
             ) : (
                 <p className="text-xs text-muted-foreground font-medium">Profile Picture</p>
             )}
          </div>

          {/* Name Input */}
          <div className="space-y-2">
            <Label htmlFor="profile-name" className="text-foreground">Display Name</Label>
            <Input 
                id="profile-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="bg-muted border-border text-foreground"
            />
          </div>

          {/* Location Input */}
          <div className="space-y-2">
            <Label htmlFor="profile-location" className="text-foreground">Location</Label>
            <div className="relative">
                <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input 
                    id="profile-location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="City, Country"
                    className="pl-9 bg-muted border-border text-foreground"
                />
            </div>
          </div>

          {/* Tabs */}
          <div className="flex p-1 bg-muted rounded-lg border border-border">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all ${
                activeTab === 'upload' 
                  ? 'bg-card text-foreground shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Upload className="w-4 h-4" />
              Upload Photo
            </button>
            <button
              onClick={() => setActiveTab('link')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all ${
                activeTab === 'link' 
                  ? 'bg-card text-foreground shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <LinkIcon className="w-4 h-4" />
              Image Link
            </button>
          </div>

          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <div className="border-2 border-dashed border-border rounded-xl p-8 hover:border-primary/50 hover:bg-primary/5 transition-colors cursor-pointer relative text-center">
              <input 
                  type="file" 
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="bg-primary/10 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 text-primary">
                <ImageIcon className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-semibold text-foreground">Click to upload image</h3>
              <p className="text-xs text-muted-foreground mt-1">SVG, PNG, JPG or GIF (max 5MB)</p>
            </div>
          )}

          {/* Link Tab */}
          {activeTab === 'link' && (
            <div className="space-y-3">
              <Label htmlFor="img-url" className="text-foreground">Paste image URL</Label>
              <Input 
                id="img-url"
                value={url.startsWith('data:') ? '' : url}
                onChange={(e) => {
                    setUrl(e.target.value);
                    setError('');
                }}
                placeholder="https://example.com/image.jpg"
                className="bg-muted border-border text-foreground"
              />
              <p className="text-xs text-muted-foreground">
                Works best with direct links to images (ending in .jpg, .png, etc.)
              </p>
            </div>
          )}
          
          {error && (
            <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-lg flex items-center justify-center">
              {error}
            </div>
          )}
        </div>

        <DialogFooter className="p-4 bg-muted/30 border-t border-border flex-row gap-2 shrink-0">
          <Button 
            variant="ghost" 
            onClick={onClose} 
            className="flex-1 bg-muted hover:bg-accent text-foreground border border-border"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-md"
          >
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ProfilePicDialog;
