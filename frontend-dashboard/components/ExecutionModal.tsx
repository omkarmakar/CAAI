'use client';

import { useState, useEffect } from 'react';
import APIClient from '@/lib/apiClient';

interface ExecutionModalProps {
  agentName: string;
  agentData: any;
  onClose: () => void;
  apiBaseUrl: string;
  authToken: string | null;
}

export default function ExecutionModal({ agentName, agentData, onClose, apiBaseUrl, authToken }: ExecutionModalProps) {
  const [selectedAction, setSelectedAction] = useState('');
  const [parameters, setParameters] = useState<any>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<{[key: string]: File}>({});
  const [uploadingFiles, setUploadingFiles] = useState<{[key: string]: boolean}>({});

  const actions = agentData?.actions || {};

  useEffect(() => {
    // Reset when action changes
    setParameters({});
    setResult(null);
    setError(null);
    setUploadedFiles({});
    setUploadingFiles({});
  }, [selectedAction]);

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters((prev: any) => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleFileUpload = async (paramName: string, file: File) => {
    setUploadingFiles(prev => ({ ...prev, [paramName]: true }));
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${apiBaseUrl}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('File upload failed');
      }

      const data = await response.json();
      setUploadedFiles(prev => ({ ...prev, [paramName]: file }));
      handleParameterChange(paramName, data.path);
    } catch (err: any) {
      setError(`File upload failed: ${err.message}`);
    } finally {
      setUploadingFiles(prev => ({ ...prev, [paramName]: false }));
    }
  };

  const handleExecute = async () => {
    if (!authToken) {
      setError('Please login to execute agents');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await APIClient.post('/agents/execute', {
        agent: agentName,
        action: selectedAction,
        params: parameters
      });
      
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderParameterInput = (param: any) => {
    const { name, label, type, placeholder, required, options } = param;

    if (type === 'select') {
      return (
        <select
          value={parameters[name] || ''}
          onChange={(e) => handleParameterChange(name, e.target.value)}
          className="w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 bg-white text-gray-900"
          style={{ fontSize: '16px', lineHeight: '1.5' }}
          required={required}
        >
          <option value="" className="text-gray-500">-- Select {label} --</option>
          {options?.map((opt: string) => (
            <option key={opt} value={opt} className="text-gray-900 py-2">{opt}</option>
          ))}
        </select>
      );
    }

    if (type === 'number') {
      return (
        <input
          type="number"
          value={parameters[name] || ''}
          onChange={(e) => handleParameterChange(name, parseFloat(e.target.value))}
          placeholder={placeholder}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
          required={required}
        />
      );
    }

    if (type === 'text' || type === 'string') {
      return (
        <textarea
          value={parameters[name] || ''}
          onChange={(e) => handleParameterChange(name, e.target.value)}
          placeholder={placeholder}
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
          required={required}
        />
      );
    }

    if (type === 'json') {
      return (
        <textarea
          value={parameters[name] || ''}
          onChange={(e) => handleParameterChange(name, e.target.value)}
          placeholder={placeholder || 'Enter JSON data'}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 font-mono text-sm"
          required={required}
        />
      );
    }

    if (type === 'file') {
      return (
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <label className="flex-1">
              <input
                type="file"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileUpload(name, file);
                }}
                className="hidden"
                id={`file-${name}`}
                required={required && !parameters[name]}
              />
              <div className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition cursor-pointer bg-gray-50 hover:bg-blue-50">
                <div className="flex items-center justify-center gap-2 text-gray-600">
                  {uploadingFiles[name] ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                      <span>Uploading...</span>
                    </>
                  ) : uploadedFiles[name] ? (
                    <>
                      <span className="text-green-600">✓</span>
                      <span className="text-green-600 font-medium">{uploadedFiles[name].name}</span>
                    </>
                  ) : (
                    <>
                      <span className="text-2xl">📁</span>
                      <span>Click to upload file</span>
                    </>
                  )}
                </div>
              </div>
            </label>
            {uploadedFiles[name] && (
              <button
                type="button"
                onClick={() => {
                  setUploadedFiles(prev => {
                    const newFiles = { ...prev };
                    delete newFiles[name];
                    return newFiles;
                  });
                  handleParameterChange(name, '');
                }}
                className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                title="Remove file"
              >
                🗑️
              </button>
            )}
          </div>
          {uploadedFiles[name] && (
            <p className="text-xs text-gray-500">
              File uploaded: {parameters[name]}
            </p>
          )}
        </div>
      );
    }

    if (type === 'files') {
      return (
        <div className="space-y-2">
          <label>
            <input
              type="file"
              multiple
              onChange={async (e) => {
                const files = Array.from(e.target.files || []);
                if (files.length > 0) {
                  setUploadingFiles(prev => ({ ...prev, [name]: true }));
                  const uploadedPaths: string[] = [];
                  
                  for (const file of files) {
                    try {
                      const formData = new FormData();
                      formData.append('file', file);
                      const response = await fetch(`${apiBaseUrl}/upload`, {
                        method: 'POST',
                        body: formData
                      });
                      const data = await response.json();
                      uploadedPaths.push(data.path);
                    } catch (err) {
                      console.error('Upload failed:', err);
                    }
                  }
                  
                  handleParameterChange(name, uploadedPaths);
                  setUploadingFiles(prev => ({ ...prev, [name]: false }));
                }
              }}
              className="hidden"
              id={`files-${name}`}
            />
            <div className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition cursor-pointer bg-gray-50 hover:bg-blue-50">
              <div className="flex items-center justify-center gap-2 text-gray-600">
                {uploadingFiles[name] ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                    <span>Uploading files...</span>
                  </>
                ) : parameters[name]?.length > 0 ? (
                  <>
                    <span className="text-green-600">✓</span>
                    <span className="text-green-600 font-medium">{parameters[name].length} file(s) uploaded</span>
                  </>
                ) : (
                  <>
                    <span className="text-2xl">📁</span>
                    <span>Click to upload multiple files</span>
                  </>
                )}
              </div>
            </div>
          </label>
          {parameters[name]?.length > 0 && (
            <div className="text-xs text-gray-500 space-y-1">
              {parameters[name].map((path: string, idx: number) => (
                <div key={idx}>• {path}</div>
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <input
        type="text"
        value={parameters[name] || ''}
        onChange={(e) => handleParameterChange(name, e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
        required={required}
      />
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">{agentData.display || agentName}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-3xl w-10 h-10 flex items-center justify-center leading-none hover:bg-gray-100 rounded-full transition"
            title="Close"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {/* Action Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Action *
            </label>
            <select
              value={selectedAction}
              onChange={(e) => setSelectedAction(e.target.value)}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 bg-white text-gray-900"
              style={{ fontSize: '16px', lineHeight: '1.5' }}
            >
              <option value="" className="text-gray-500">-- Choose an action --</option>
              {Object.entries(actions).map(([actionKey, actionData]: any) => (
                <option key={actionKey} value={actionKey} className="text-gray-900 py-2">
                  {actionData.label || actionKey}
                </option>
              ))}
            </select>
          </div>

          {/* Parameters Form */}
          {selectedAction && actions[selectedAction]?.params && (
            <div className="space-y-4 mb-6">
              <h3 className="font-semibold text-gray-700 text-lg">Parameters</h3>
              {actions[selectedAction].params.map((param: any) => (
                <div key={param.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {param.label} {param.required && <span className="text-red-500">*</span>}
                  </label>
                  {renderParameterInput(param)}
                </div>
              ))}
            </div>
          )}

          {/* Execute Button */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={handleExecute}
              disabled={!selectedAction || loading}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                !selectedAction || loading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {loading ? ' Executing...' : ' Execute Agent'}
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition"
            >
              Cancel
            </button>
          </div>

          {/* Loading Indicator */}
          {loading && (
            <div className="flex items-center justify-center py-8 bg-blue-50 rounded-lg">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Executing agent...</span>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <div className="flex items-start">
                <span className="text-2xl mr-3"></span>
                <div>
                  <h4 className="text-red-800 font-semibold mb-1">Execution Failed</h4>
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Result Display */}
          {result && !loading && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <span></span> Execution Result
              </h3>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 max-h-96 overflow-y-auto">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
