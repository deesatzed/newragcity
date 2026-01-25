import React, { useState, useEffect } from 'react';
import DocumentManager from '../components/admin/DocumentManager';
import AuditTrailViewer from '../components/admin/AuditTrailViewer';
import SystemDashboard from '../components/admin/SystemDashboard';
import UserManagement from '../components/admin/UserManagement';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('documents');
  const [systemStatus, setSystemStatus] = useState({
    services: [],
    lastUpdated: null
  });

  const tabs = [
    { id: 'documents', name: 'Document Management', icon: '📄' },
    { id: 'audit', name: 'Audit Trail', icon: '📊' },
    { id: 'system', name: 'System Dashboard', icon: '⚙️' },
    { id: 'users', name: 'User Management', icon: '👥' }
  ];

  useEffect(() => {
    // Fetch system status periodically
    const fetchSystemStatus = async () => {
      try {
        const services = ['pageindex', 'leann', 'deepconf', 'thalamus'];
        const statusChecks = await Promise.all(
          services.map(async (service) => {
            try {
              const response = await fetch(`http://localhost:800${service === 'pageindex' ? 0 : service === 'leann' ? 1 : service === 'deepconf' ? 2 : 3}/health`);
              const data = await response.json();
              return {
                name: service,
                status: response.ok ? 'healthy' : 'unhealthy',
                lastChecked: new Date().toISOString()
              };
            } catch (error) {
              return {
                name: service,
                status: 'offline',
                lastChecked: new Date().toISOString()
              };
            }
          })
        );
        setSystemStatus({
          services: statusChecks,
          lastUpdated: new Date()
        });
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'documents':
        return <DocumentManager />;
      case 'audit':
        return <AuditTrailViewer />;
      case 'system':
        return <SystemDashboard systemStatus={systemStatus} />;
      case 'users':
        return <UserManagement />;
      default:
        return <DocumentManager />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🧠 Regulus Admin Dashboard
              </h1>
              <span className="ml-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                Policy & Compliance Management
              </span>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  systemStatus.services.every(s => s.status === 'healthy')
                    ? 'bg-green-500'
                    : 'bg-yellow-500'
                }`}></div>
                <span className="text-sm text-gray-600">
                  System Health: {systemStatus.services.filter(s => s.status === 'healthy').length}/{systemStatus.services.length}
                </span>
              </div>
              <span className="text-sm text-gray-600">
                Last updated: {systemStatus.lastUpdated?.toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveTab()}
      </main>
    </div>
  );
}
