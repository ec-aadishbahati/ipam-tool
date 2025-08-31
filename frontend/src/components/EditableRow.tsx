import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { getErrorMessage } from "../utils/errorHandling";

interface EditableRowProps {
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
  onUpdate?: () => void;
  onDelete?: () => void;
}


export function EditableRow({ entity, entityType, fields, onUpdate, onDelete }: EditableRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState(entity);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const qc = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: async (data: any) => (await api.patch(`/api/${entityType}/${entity.id}`, data)).data,
    onSuccess: () => {
      setIsEditing(false);
      qc.invalidateQueries({ queryKey: [entityType] });
      onUpdate?.();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async () => (await api.delete(`/api/${entityType}/${entity.id}`)).data,
    onSuccess: () => {
      setShowDeleteConfirm(false);
      qc.invalidateQueries({ queryKey: [entityType] });
      onDelete?.();
    },
  });

  const handleSave = () => {
    const changes: any = {};
    fields.forEach(field => {
      if (field.editable !== false && editForm[field.key] !== entity[field.key]) {
        changes[field.key] = editForm[field.key];
      }
    });
    if (Object.keys(changes).length > 0) {
      updateMutation.mutate(changes);
    } else {
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditForm(entity);
    setIsEditing(false);
  };

  return (
    <>
      <tr key={entity.id}>
        {fields.map((field) => (
          <td key={field.key} className="p-2 border">
            {isEditing && field.editable !== false ? (
              field.type === 'select' ? (
                <select 
                  className="border p-1 rounded w-full text-xs"
                  value={editForm[field.key] || ""}
                  onChange={(e) => setEditForm({...editForm, [field.key]: e.target.value})}
                >
                  <option value="">Select...</option>
                  {field.options?.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              ) : (
                <input
                  className="border p-1 rounded w-full text-xs"
                  type={field.type || 'text'}
                  value={editForm[field.key] || ""}
                  onChange={(e) => setEditForm({...editForm, [field.key]: field.type === 'number' ? Number(e.target.value) : e.target.value})}
                />
              )
            ) : (
              field.render ? field.render(entity[field.key], entity) : entity[field.key]
            )}
          </td>
        ))}
        <td className="p-2 border">
          {isEditing ? (
            <div className="flex gap-1">
              <button 
                className="text-green-600 hover:underline text-sm"
                onClick={handleSave}
                disabled={updateMutation.isPending}
              >
                Save
              </button>
              <button 
                className="text-gray-600 hover:underline text-sm"
                onClick={handleCancel}
              >
                Cancel
              </button>
            </div>
          ) : (
            <div className="flex gap-1">
              <button 
                className="text-blue-600 hover:underline text-sm mr-2"
                onClick={() => setIsEditing(true)}
              >
                Edit
              </button>
              <button 
                className="text-red-600 hover:underline text-sm"
                onClick={() => setShowDeleteConfirm(true)}
              >
                Delete
              </button>
            </div>
          )}
        </td>
      </tr>
      {updateMutation.error && (
        <tr>
          <td colSpan={fields.length + 1} className="p-2 border bg-red-50">
            <div className="text-sm text-red-600">{getErrorMessage(updateMutation.error)}</div>
          </td>
        </tr>
      )}
      {showDeleteConfirm && (
        <tr>
          <td colSpan={fields.length + 1} className="p-2 border bg-yellow-50">
            <div className="text-sm">
              Are you sure you want to delete this {entityType}? 
              <button 
                className="text-red-600 hover:underline ml-2"
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
              >
                Yes, Delete
              </button>
              <button 
                className="text-gray-600 hover:underline ml-2"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
              {deleteMutation.error && (
                <div className="text-red-600 mt-1">{getErrorMessage(deleteMutation.error)}</div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
