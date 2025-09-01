import React from 'react';

interface AllocationBarProps {
  utilizationPercentage: number;
  className?: string;
  showPercentage?: boolean;
  allocatedRanges?: Array<{start: number, end: number}>;
  totalAddresses?: number;
}

export function AllocationBar({ 
  utilizationPercentage, 
  className = "", 
  showPercentage = true,
  allocatedRanges = [],
  totalAddresses = 0
}: AllocationBarProps) {
  const usedPercentage = Math.min(Math.max(utilizationPercentage || 0, 0), 100);
  const availablePercentage = 100 - usedPercentage;

  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex-1 h-4 bg-green-500 rounded-full overflow-hidden border relative">
        {/* Green background represents available space */}
        {usedPercentage > 0 && (
          <div 
            className="bg-red-500 h-full transition-all duration-300 absolute left-0 top-0"
            style={{ width: `${usedPercentage}%` }}
            title={`${usedPercentage.toFixed(1)}% allocated`}
          />
        )}
      </div>
      {showPercentage && (
        <span className="text-xs text-gray-600 min-w-[3rem]">
          {usedPercentage.toFixed(1)}%
        </span>
      )}
    </div>
  );
}
