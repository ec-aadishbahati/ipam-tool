import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

interface BackupItem {
  backup_id: string;
  filename: string;
  created_at: string;
  size_bytes: number;
  total_records: number;
  created_by_user_id: number;
}

interface RestoreResult {
  success: boolean;
  message: string;
  records_imported: Record<string, number>;
  errors: string[];
}

export default function Backup() {
  const [isCreating, setIsCreating] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);
  const [restoreFile, setRestoreFile] = useState<File | null>(null);
  const [confirmChecked, setConfirmChecked] = useState(false);
  const [restoreResult, setRestoreResult] = useState<RestoreResult | null>(null);
  
  const queryClient = useQueryClient();

  const { data: backups, refetch: refetchBackups } = useQuery({
    queryKey: ['backups'],
    queryFn: async () => {
      const response = await api.get('/api/backup/list');
      return response.data as BackupItem[];
    }
  });

  const createBackupMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/api/backup/create');
      return response.data;
    },
    onSuccess: () => {
      refetchBackups();
      setIsCreating(false);
    },
    onError: (error: any) => {
      console.error('Backup creation failed:', error);
      setIsCreating(false);
    }
  });

  const deleteBackupMutation = useMutation({
    mutationFn: async (backupId: string) => {
      const response = await api.delete(`/api/backup/${backupId}`);
      return response.data;
    },
    onSuccess: () => {
      refetchBackups();
    }
  });

  const restoreBackupMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/api/backup/restore', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data as RestoreResult;
    },
    onSuccess: (result) => {
      setRestoreResult(result);
      setIsRestoring(false);
      setRestoreFile(null);
      setConfirmChecked(false);
      queryClient.invalidateQueries();
    },
    onError: (error: any) => {
      console.error('Restore failed:', error);
      setIsRestoring(false);
    }
  });

  const handleCreateBackup = () => {
    setIsCreating(true);
    createBackupMutation.mutate();
  };

  const handleDownloadBackup = async (backupId: string, filename: string) => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        alert('Authentication token not found. Please log in again.');
        return;
      }

      const downloadUrl = `/api/backup/download/${backupId}?token=${encodeURIComponent(token)}`;
      window.open(downloadUrl, '_blank');
      
    } catch (error) {
      console.error('Download failed:', error);
      alert(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleDeleteBackup = (backupId: string) => {
    if (confirm('Are you sure you want to delete this backup?')) {
      deleteBackupMutation.mutate(backupId);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setRestoreFile(file);
    }
  };

  const handleFileDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && file.name.endsWith('.json')) {
      setRestoreFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleRestoreConfirm = () => {
    if (restoreFile && confirmChecked) {
      setIsRestoring(true);
      restoreBackupMutation.mutate(restoreFile);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Backup & Restore</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Create Backup</h2>
        <p className="text-gray-600 mb-4">
          Create a complete backup of all system data including users, categories, purposes, VLANs, subnets, devices, and IP assignments.
        </p>
        <button
          onClick={handleCreateBackup}
          disabled={isCreating}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {isCreating ? 'Creating Backup...' : 'Create New Backup'}
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Available Backups</h2>
        {backups && backups.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">Date Created</th>
                  <th className="px-4 py-2 text-left">Filename</th>
                  <th className="px-4 py-2 text-left">Size</th>
                  <th className="px-4 py-2 text-left">Records</th>
                  <th className="px-4 py-2 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {backups.map((backup) => (
                  <tr key={backup.backup_id} className="border-t">
                    <td className="px-4 py-2">{formatDate(backup.created_at)}</td>
                    <td className="px-4 py-2 font-mono text-sm">{backup.filename}</td>
                    <td className="px-4 py-2">{formatFileSize(backup.size_bytes)}</td>
                    <td className="px-4 py-2">{backup.total_records.toLocaleString()}</td>
                    <td className="px-4 py-2">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleDownloadBackup(backup.backup_id, backup.filename)}
                          className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                        >
                          Download
                        </button>
                        <button
                          onClick={() => handleDeleteBackup(backup.backup_id)}
                          className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No backups available</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Restore from Backup</h2>
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
          <div className="flex items-center">
            <div className="text-red-600 mr-2">⚠️</div>
            <div>
              <p className="font-semibold text-red-800">WARNING: This will completely replace all existing data!</p>
              <p className="text-red-700 text-sm">All current users, categories, purposes, VLANs, subnets, devices, and IP assignments will be permanently deleted and replaced with the backup data.</p>
            </div>
          </div>
        </div>

        {!restoreFile ? (
          <div
            onDrop={handleFileDrop}
            onDragOver={handleDragOver}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400"
          >
            <div className="text-gray-500 mb-4">
              <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <p className="text-lg mb-2">Drop backup file here or</p>
            <label className="bg-blue-500 text-white px-4 py-2 rounded cursor-pointer hover:bg-blue-600">
              Browse Files
              <input
                type="file"
                accept=".json"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
            <p className="text-sm text-gray-500 mt-2">Only JSON backup files are accepted</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded">
              <p className="font-semibold">Selected File:</p>
              <p className="text-sm text-gray-600">{restoreFile.name}</p>
              <p className="text-sm text-gray-600">Size: {formatFileSize(restoreFile.size)}</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="confirmRestore"
                checked={confirmChecked}
                onChange={(e) => setConfirmChecked(e.target.checked)}
                className="h-4 w-4"
              />
              <label htmlFor="confirmRestore" className="text-sm">
                I understand this will delete all existing data and cannot be undone
              </label>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={handleRestoreConfirm}
                disabled={!confirmChecked || isRestoring}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:opacity-50"
              >
                {isRestoring ? 'Restoring...' : 'Restore Data'}
              </button>
              <button
                onClick={() => {
                  setRestoreFile(null);
                  setConfirmChecked(false);
                }}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {restoreResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {restoreResult.success ? 'Restore Successful' : 'Restore Failed'}
            </h3>
            
            <p className="mb-4">{restoreResult.message}</p>
            
            {restoreResult.success && Object.keys(restoreResult.records_imported).length > 0 && (
              <div className="mb-4">
                <p className="font-semibold mb-2">Records Imported:</p>
                <ul className="text-sm space-y-1">
                  {Object.entries(restoreResult.records_imported).map(([entity, count]) => (
                    <li key={entity} className="flex justify-between">
                      <span className="capitalize">{entity}:</span>
                      <span>{count}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {restoreResult.errors && restoreResult.errors.length > 0 && (
              <div className="mb-4">
                <p className="font-semibold mb-2 text-red-600">Errors:</p>
                <ul className="text-sm text-red-600 space-y-1 max-h-32 overflow-y-auto">
                  {restoreResult.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
            
            <button
              onClick={() => setRestoreResult(null)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
