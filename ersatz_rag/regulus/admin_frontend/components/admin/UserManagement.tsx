import React, { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'compliance_officer' | 'user';
  lastLogin: string;
  status: 'active' | 'inactive' | 'suspended';
  queriesCount: number;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    name: '',
    role: 'user' as const
  });

  // Mock user data for demonstration
  useEffect(() => {
    setUsers([
      {
        id: '1',
        email: 'admin@company.com',
        name: 'Admin User',
        role: 'admin',
        lastLogin: '2025-09-06T14:30:00Z',
        status: 'active',
        queriesCount: 45
      },
      {
        id: '2',
        email: 'compliance@company.com',
        name: 'Sarah Johnson',
        role: 'compliance_officer',
        lastLogin: '2025-09-06T13:15:00Z',
        status: 'active',
        queriesCount: 23
      },
      {
        id: '3',
        email: 'john.doe@company.com',
        name: 'John Doe',
        role: 'user',
        lastLogin: '2025-09-06T12:45:00Z',
        status: 'active',
        queriesCount: 12
      },
      {
        id: '4',
        email: 'mike.smith@company.com',
        name: 'Mike Smith',
        role: 'user',
        lastLogin: '2025-09-05T16:20:00Z',
        status: 'inactive',
        queriesCount: 5
      },
      {
        id: '5',
        email: 'suspended.user@company.com',
        name: 'Suspended User',
        role: 'user',
        lastLogin: '2025-09-01T10:00:00Z',
        status: 'suspended',
        queriesCount: 0
      }
    ]);
  }, []);

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'text-red-600 bg-red-100';
      case 'compliance_officer':
        return 'text-blue-600 bg-blue-100';
      case 'user':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'inactive':
        return 'text-yellow-600 bg-yellow-100';
      case 'suspended':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const handleAddUser = () => {
    if (newUser.email && newUser.name) {
      const user: User = {
        id: Date.now().toString(),
        email: newUser.email,
        name: newUser.name,
        role: newUser.role,
        lastLogin: 'Never',
        status: 'active',
        queriesCount: 0
      };
      setUsers(prev => [user, ...prev]);
      setNewUser({ email: '', name: '', role: 'user' });
      setIsAddingUser(false);
    }
  };

  const updateUserStatus = (userId: string, newStatus: 'active' | 'inactive' | 'suspended') => {
    setUsers(prev => prev.map(user =>
      user.id === userId ? { ...user, status: newStatus } : user
    ));
  };

  const updateUserRole = (userId: string, newRole: 'admin' | 'compliance_officer' | 'user') => {
    setUsers(prev => prev.map(user =>
      user.id === userId ? { ...user, role: newRole } : user
    ));
  };

  return (
    <div className="space-y-6">
      {/* User Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-2xl font-bold text-gray-900">{users.length}</div>
          <div className="text-sm text-gray-600">Total Users</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-2xl font-bold text-green-600">{users.filter(u => u.status === 'active').length}</div>
          <div className="text-sm text-gray-600">Active Users</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-2xl font-bold text-blue-600">{users.filter(u => u.role === 'compliance_officer').length}</div>
          <div className="text-sm text-gray-600">Compliance Officers</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-2xl font-bold text-purple-600">{users.reduce((sum, u) => sum + u.queriesCount, 0)}</div>
          <div className="text-sm text-gray-600">Total Queries</div>
        </div>
      </div>

      {/* Add User Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">User Management</h2>
          <button
            onClick={() => setIsAddingUser(!isAddingUser)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
          >
            {isAddingUser ? 'Cancel' : 'Add User'}
          </button>
        </div>

        {isAddingUser && (
          <div className="border border-gray-200 rounded-md p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter full name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter email address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="user">User</option>
                  <option value="compliance_officer">Compliance Officer</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end mt-4">
              <button
                onClick={handleAddUser}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
              >
                Add User
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Users List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Users</h3>
        </div>

        <div className="divide-y divide-gray-200">
          {users.map((user) => (
            <div key={user.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-600">
                          {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{user.name}</h4>
                      <p className="text-sm text-gray-500">{user.email}</p>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(user.role)}`}>
                          {user.role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(user.status)}`}>
                          {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {user.queriesCount} queries
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-900">
                      Last Login
                    </p>
                    <p className="text-sm text-gray-500">
                      {user.lastLogin === 'Never' ? 'Never' : new Date(user.lastLogin).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="flex space-x-2">
                    <select
                      value={user.role}
                      onChange={(e) => updateUserRole(user.id, e.target.value as any)}
                      className="text-xs border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="user">User</option>
                      <option value="compliance_officer">Compliance</option>
                      <option value="admin">Admin</option>
                    </select>

                    <select
                      value={user.status}
                      onChange={(e) => updateUserStatus(user.id, e.target.value as any)}
                      className="text-xs border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="suspended">Suspended</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
