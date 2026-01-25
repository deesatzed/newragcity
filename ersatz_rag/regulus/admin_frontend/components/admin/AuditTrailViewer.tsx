import React, { useState, useEffect } from 'react';

interface AuditEntry {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  details: string;
  confidence?: number;
  citations?: string[];
}

export default function AuditTrailViewer() {
  const [auditEntries, setAuditEntries] = useState<AuditEntry[]>([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch real audit events from Regulus transparency API if available
  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const res = await fetch('http://localhost:8000/transparency/audit/events?limit=100');
        if (!res.ok) {
          console.error('Failed to fetch audit events', res.status);
          setAuditEntries([]);
          return;
        }
        const data = await res.json();
        const events = (data?.events || []).map((e: any) => {
          const id = e.event_id || `${Date.now()}_${Math.random().toString(16).slice(2)}`;
          const ts = e.timestamp || new Date().toISOString();
          const user = e.user_id || 'unknown';
          const action = e.action_performed || e.event_type || 'event';
          const resource = e.resource_accessed || '';
          // Choose a representative detail field
          const details = e.request_data?.query || e.request_data?.search_query || e.action_performed || '';
          const confidence = e.response_data?.confidence_score ?? null;
          const citations = e.response_data?.sources_used || [];
          return {
            id,
            timestamp: ts,
            user,
            action,
            resource,
            details,
            confidence,
            citations
          } as AuditEntry;
        });
        setAuditEntries(events);
      } catch (err) {
        console.error('Audit fetch error', err);
        setAuditEntries([]);
      }
    };
    fetchAudit();
    const interval = setInterval(fetchAudit, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredEntries = auditEntries.filter(entry => {
    const matchesFilter = filter === 'all' || entry.action === filter;
    const matchesSearch = searchTerm === '' ||
      entry.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.resource.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'query':
        return '🔍';
      case 'document_upload':
        return '📤';
      case 'system_maintenance':
        return '⚙️';
      case 'document_archive':
        return '📁';
      default:
        return '📝';
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'query':
        return 'text-blue-600 bg-blue-100';
      case 'document_upload':
        return 'text-green-600 bg-green-100';
      case 'system_maintenance':
        return 'text-yellow-600 bg-yellow-100';
      case 'document_archive':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Filter Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Audit Trail</h2>

        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search audit entries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex space-x-2">
            {['all', 'query', 'document_upload', 'system_maintenance', 'document_archive'].map((action) => (
              <button
                key={action}
                onClick={() => setFilter(action)}
                className={`px-3 py-2 text-sm rounded-md ${
                  filter === action
                    ? 'bg-blue-100 text-blue-800 border-blue-300'
                    : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
                } border`}
              >
                {action === 'all' ? 'All' : action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </button>
            ))}
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{auditEntries.filter(e => e.action === 'query').length}</div>
            <div className="text-sm text-blue-600">Policy Queries</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{auditEntries.filter(e => e.action === 'document_upload').length}</div>
            <div className="text-sm text-green-600">Document Uploads</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">{auditEntries.filter(e => e.action === 'system_maintenance').length}</div>
            <div className="text-sm text-yellow-600">System Events</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {auditEntries.filter(e => e.confidence !== null).length > 0
                ? (auditEntries.filter(e => e.confidence !== null).reduce((sum, e) => sum + (e.confidence || 0), 0) /
                   auditEntries.filter(e => e.confidence !== null).length * 100).toFixed(1) + '%'
                : 'N/A'}
            </div>
            <div className="text-sm text-purple-600">Avg Confidence</div>
          </div>
        </div>
      </div>

      {/* Audit Entries */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Activity Log</h3>
        </div>

        <div className="divide-y divide-gray-200">
          {filteredEntries.map((entry) => (
            <div key={entry.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-start space-x-4">
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${getActionColor(entry.action)}`}>
                  <span className="text-sm">{getActionIcon(entry.action)}</span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{entry.user}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(entry.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {entry.confidence && (
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          entry.confidence >= 0.8
                            ? 'bg-green-100 text-green-800'
                            : entry.confidence >= 0.6
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {(entry.confidence * 100).toFixed(0)}% confidence
                        </span>
                      )}
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(entry.action)}`}>
                        {entry.action.replace('_', ' ')}
                      </span>
                    </div>
                  </div>

                  <div className="mt-2">
                    <p className="text-sm text-gray-700">{entry.details}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Resource: <span className="font-medium">{entry.resource}</span>
                    </p>
                  </div>

                  {entry.citations && entry.citations.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-600 font-medium">Citations:</p>
                      <ul className="text-xs text-gray-500 mt-1 space-y-1">
                        {entry.citations.map((citation, index) => (
                          <li key={index} className="flex items-center">
                            <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                            {citation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredEntries.length === 0 && (
          <div className="px-6 py-12 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No audit entries found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search or filter criteria.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
