import React from 'react';

interface AllocationBarProps {
  utilizationPercentage: number;
  className?: string;
  showPercentage?: boolean;
}

export function AllocationBar({ utilizationPercentage, className = "", showPercentage = true }: AllocationBarProps) {
  const usedPercentage = Math.min(Math.max(utilizationPercentage || 0, 0), 100);
  const availablePercentage = 100 - usedPercentage;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden border">
        <div className="h-full flex">
          {usedPercentage > 0 && (
            <div 
              className="bg-red-500 h-full transition-all duration-300"
              style={{ width: `${usedPercentage}%` }}
              title={`${usedPercentage.toFixed(1)}% allocated`}
            />
          )}
          {availablePercentage > 0 && (
            <div 
              className="bg-green-500 h-full transition-all duration-300"
              style={{ width: `${availablePercentage}%` }}
              title={`${availablePercentage.toFixed(1)}% available`}
            />
          )}
        </div>
      </div>
      {showPercentage && (
        <span className="text-xs text-gray-600 min-w-[3rem]">
          {usedPercentage.toFixed(1)}%
        </span>
      )}
    </div>
  );
}
