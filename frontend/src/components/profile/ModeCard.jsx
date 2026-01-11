import React from 'react';
import { Switch } from '../ui/switch';

const ModeCard = ({
  mode,
  icon,
  name,
  description,
  isActive,
  settings,
  onToggle,
  onEdit
}) => {
  return (
    <div 
      className={`
        w-full text-left p-4 rounded-lg border-2 transition-all duration-200
        ${isActive 
          ? 'border-primary bg-primary/10 shadow-md' 
          : 'border-border bg-card hover:border-accent hover:shadow-sm'
        }
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-3">
          {/* Mode Icon */}
          <span className="text-3xl leading-none">{icon}</span>
          
          {/* Mode Info */}
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              {name}
            </h3>
            <p className="text-sm text-muted-foreground">
              {description}
            </p>
          </div>
        </div>
        
        {/* Toggle Switch */}
        <div className="flex flex-col items-end gap-2">
          <Switch 
            checked={isActive}
            onCheckedChange={(checked) => onToggle(mode, checked)}
            className={isActive ? "bg-primary" : "bg-muted"}
          />
          {isActive ? (
            <span className="px-3 py-1 rounded-full font-bold text-xs bg-green-100 text-green-700 border border-green-500 dark:bg-green-900 dark:text-green-100 dark:border-green-700">
              ACTIVE
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full font-bold text-xs bg-muted text-muted-foreground border border-border">
              INACTIVE
            </span>
          )}
        </div>
      </div>

      {/* Active State Content */}
      {isActive && settings && (
        <div className="mt-3 pt-3 border-t border-border">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="text-sm text-green-600 font-medium flex items-center gap-1 dark:text-green-400">
              ✓ {settings}
            </span>
            
            {onEdit && (
              <button
                onClick={() => onEdit(mode)}
                className="text-sm text-primary hover:text-primary/80 font-medium hover:underline"
              >
                Edit
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Active but no settings text (e.g. Green Mode) */}
      {isActive && !settings && (
        <div className="mt-3 pt-3 border-t border-border">
           <span className="text-sm text-green-600 font-medium dark:text-green-400">
              ✓ Active
           </span>
        </div>
      )}
    </div>
  );
};

export default ModeCard;
