import React, { useRef } from 'react';
import { useFileUpload } from '../hooks/useData';
import { useNotifications } from './ui/notification';

export default function FileUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const { isUploading, progress, error, uploadedFile, upload, reset } = useFileUpload();
  const { addNotification } = useNotifications();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await upload(file);
      addNotification({
        type: 'success',
        title: 'File Uploaded',
        message: `${file.name} uploaded successfully.`,
      });
    } catch (err: any) {
      addNotification({
        type: 'error',
        title: 'Upload Error',
        message: err?.detail || 'File upload failed.',
      });
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    try {
      await upload(file);
      addNotification({
        type: 'success',
        title: 'File Uploaded',
        message: `${file.name} uploaded successfully.`,
      });
    } catch (err: any) {
      addNotification({
        type: 'error',
        title: 'Upload Error',
        message: err?.detail || 'File upload failed.',
      });
    }
  };

  return (
    <div className="w-full max-w-md mx-auto my-6">
      <div
        className="border-2 border-dashed border-accent-primary rounded-lg p-6 text-center cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent-primary"
        tabIndex={0}
        role="button"
        aria-label="Upload file"
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          onChange={handleFileChange}
          aria-label="File input"
        />
        <p className="text-text-primary mb-2">Drag and drop a file here, or <span className="underline text-accent-primary">browse</span></p>
        {isUploading && (
          <div className="mt-2 text-accent-secondary" aria-live="polite">
            Uploading... {progress.toFixed(0)}%
          </div>
        )}
        {error && (
          <div className="mt-2 text-accent-error" role="alert" aria-live="assertive">
            {error}
          </div>
        )}
        {uploadedFile && (
          <div className="mt-2 text-accent-tertiary" aria-live="polite">
            Uploaded: {uploadedFile.filename}
            <button className="ml-2 underline text-accent-error" onClick={reset} aria-label="Remove uploaded file">Remove</button>
          </div>
        )}
      </div>
    </div>
  );
}
