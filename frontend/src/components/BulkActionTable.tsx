import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";
import { EditableRow } from "./EditableRow";

interface BulkActionTableProps {
  data: any[];
  entityType: string;
  fields: Array<{
    key: string;
    label: string;
    type?: 'text' | 'number' | 'select';
    options?: Array<{value: any, label: string}>;
    editable?: boolean;
    render?: (value: any, entity: any) => JSX.Element | string;
  }>;
  onUpdate?: () => void;
  onDelete?: () => void;
}

export function BulkActionTable({ data, entityType, fields, onUpdate, onDelete }: BulkActionTableProps) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [showBulkDeleteConfirm, setShowBulkDeleteConfirm] = useState(false);
  const qc = useQueryClient();

  const bulkDeleteMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      return (await api.delete(`/api/${entityType}/bulk`, { data: { ids } })).data;
    },
    onSuccess: () => {
      setSelectedIds(new Set());
      setShowBulkDeleteConfirm(false);
      qc.invalidateQueries({ queryKey: [entityType] });
      onDelete?.();
    },
  });

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(data.map(item => item.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectItem = (id: number, checked: boolean) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedIds(newSelected);
  };

  const handleBulkExport = async () => {
    try {
      const response = await api.post(`/api/${entityType}/export/selected`, 
        { ids: Array.from(selectedIds) },
        { responseType: 'blob' }
      );
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${entityType}-selected.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      const errorMsg = getErrorMessage(error, 'Export failed');
      alert(`Export failed: ${errorMsg}`);
    }
  };

  const selectedCount = selectedIds.size;
  const allSelected = selectedCount === data.length && data.length > 0;
  const someSelected = selectedCount > 0 && selectedCount < data.length;

  return (
    <>
      {selectedCount > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-800">
              {selectedCount} item{selectedCount !== 1 ? 's' : ''} selected
            </span>
            <div className="flex gap-2">
              <button
                onClick={handleBulkExport}
                className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
              >
                Export Selected
              </button>
              <button
                onClick={() => setShowBulkDeleteConfirm(true)}
                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
              >
                Delete Selected
              </button>
              <button
                onClick={() => setSelectedIds(new Set())}
                className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full text-xs border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 border">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={input => {
                    if (input) input.indeterminate = someSelected;
                  }}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="rounded"
                />
              </th>
              {fields.map((field) => (
                <th key={field.key} className="text-left p-2 border">{field.label}</th>
              ))}
              <th className="text-left p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <BulkSelectableRow
                key={item.id}
                entity={item}
                entityType={entityType}
                fields={fields}
                isSelected={selectedIds.has(item.id)}
                onSelect={(checked) => handleSelectItem(item.id, checked)}
                onUpdate={onUpdate}
                onDelete={onDelete}
              />
            ))}
          </tbody>
        </table>
      </div>

      {showBulkDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Confirm Bulk Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete {selectedCount} {entityType}{selectedCount !== 1 ? 's' : ''}? 
              This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowBulkDeleteConfirm(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => bulkDeleteMutation.mutate(Array.from(selectedIds))}
                disabled={bulkDeleteMutation.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                {bulkDeleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
            {bulkDeleteMutation.error && (
              <div className="mt-4 text-sm text-red-600">
                {getErrorMessage(bulkDeleteMutation.error)}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

interface BulkSelectableRowProps {
  entity: any;
  entityType: string;
  fields: Array<{
    key: string;
    label: string;
    type?: 'text' | 'number' | 'select';
    options?: Array<{value: any, label: string}>;
    editable?: boolean;
    render?: (value: any, entity: any) => JSX.Element | string;
  }>;
  isSelected: boolean;
  onSelect: (checked: boolean) => void;
  onUpdate?: () => void;
  onDelete?: () => void;
}

function BulkSelectableRow({ entity, entityType, fields, isSelected, onSelect, onUpdate, onDelete }: BulkSelectableRowProps) {
  return (
    <EditableRow
      entity={entity}
      entityType={entityType}
      fields={[
        {
          key: '_checkbox',
          label: '',
          editable: false,
          render: () => (
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => onSelect(e.target.checked)}
              className="rounded"
            />
          )
        },
        ...fields
      ]}
      onUpdate={onUpdate}
      onDelete={onDelete}
    />
  );
}
