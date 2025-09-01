import React from 'react';

interface AllocationSegment {
  start: number;
  end: number;
  type: 'allocated' | 'available';
  label?: string;
}

interface AllocationBarProps {
  utilizationPercentage: number;
  className?: string;
  showPercentage?: boolean;
  spatialSegments?: AllocationSegment[];
}

export function AllocationBar({ 
  utilizationPercentage, 
  className = "", 
  showPercentage = true,
  spatialSegments = []
}: AllocationBarProps) {
  const usedPercentage = Math.min(Math.max(utilizationPercentage || 0, 0), 100);

  if (spatialSegments.length > 0) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden border">
          <div className="h-full flex">
            {spatialSegments.map((segment, index) => (
              <div
                key={index}
                className={`h-full transition-all duration-300 ${
                  segment.type === 'allocated' ? 'bg-red-500' : 'bg-green-500'
                }`}
                style={{ width: `${segment.end - segment.start}%` }}
                title={segment.label || `${segment.type} ${(segment.end - segment.start).toFixed(1)}%`}
              />
            ))}
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

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex-1 h-4 bg-green-500 rounded-full overflow-hidden border relative">
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
