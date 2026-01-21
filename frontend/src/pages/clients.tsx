import React, { useState, useEffect } from 'react';
import {
  getClientById,
  sortClients,
  createClient,
  updateClient,
  deleteClient,
  testApiConnection,
  getClients
} from '../services/getService';
import styles from '../styles/Clients.module.css';

interface Client {
  id: string;
  name: string;
  email: string;
  age: number;
  phone: string;
  address: string;

}

const ClientsPage: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Form states
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    email: '',
    age: '',
    phone: ''
  });

  // Fetch all clients
  const fetchClients = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getClients();
      const clientsArray = Object.values(data) as Client[];
      setClients(clientsArray);
    } catch (err) {
      setError('Failed to fetch clients');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Sort clients
  const handleSort = async () => {
    setLoading(true);
    setError(null);
    try {
      const sortedData = await sortClients(sortBy, sortOrder);
      setClients(sortedData);
    } catch (err) {
      setError('Failed to sort clients');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Create client
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createClient({
        id: formData.id,
        name: formData.name,
        email: formData.email,
        age: formData.age ? parseInt(formData.age) : undefined,
        phone: formData.phone || undefined
      });
      setShowCreateForm(false);
      setFormData({ id: '', name: '', email: '', age: '', phone: '' });
      fetchClients();
    } catch (err) {
      setError('Failed to create client');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Update client
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClient) return;

    setLoading(true);
    setError(null);
    try {
      await updateClient(selectedClient.id, {
        name: formData.name,
        email: formData.email,
        age: formData.age ? parseInt(formData.age) : undefined,
        phone: formData.phone || undefined
      });
      setShowEditForm(false);
      setSelectedClient(null);
      setFormData({ id: '', name: '', email: '', age: '', phone: '' });
      fetchClients();
    } catch (err) {
      setError('Failed to update client');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Delete client
  const handleDelete = async (clientId: string) => {
    if (!confirm('Are you sure you want to delete this client?')) return;

    setLoading(true);
    setError(null);
    try {
      await deleteClient(clientId);
      fetchClients();
    } catch (err) {
      setError('Failed to delete client');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Edit client
  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setFormData({
      id: client.id,
      name: client.name,
      email: client.email,
      age: client.age?.toString() || '',
      phone: client.phone || ''
    });
    setShowEditForm(true);
  };

  // Test API connection on component mount
  useEffect(() => {
    const checkConnection = async () => {
      const result = await testApiConnection();
      if (result.success) {
        setConnectionStatus('connected');
        fetchClients();
      } else {
        setConnectionStatus('disconnected');
        setError(result.message);
      }
    };

    checkConnection();
  }, []);

  return (
    <div className={styles.clientsContainer}>
      <h1 className={styles.title}>Client Management</h1>

      {/* Connection Status */}
      <div className={styles.connectionStatus}>
        {connectionStatus === 'checking' && (
          <div className={styles.statusChecking}>
            🔍 Checking API connection...
          </div>
        )}
        {connectionStatus === 'connected' && (
          <div className={styles.statusConnected}>
            ✅ Connected to API
          </div>
        )}
        {connectionStatus === 'disconnected' && (
          <div className={styles.statusDisconnected}>
            ❌ API Connection Failed
          </div>
        )}
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* Controls */}
      <div className={styles.controls}>
        <button
          onClick={() => setShowCreateForm(true)}
          className={styles.btnPrimary}
        >
          Add New Client
        </button>

        <button
          onClick={async () => {
            setError(null);
            const result = await testApiConnection();
            if (result.success) {
              setConnectionStatus('connected');
              setError(null);
            } else {
              setConnectionStatus('disconnected');
              setError(result.message);
            }
          }}
          className={styles.btnSecondary}
        >
          Test API Connection
        </button>

        <div className={styles.sortControls}>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className={styles.select}
          >
            <option value="name">Name</option>
            <option value="age">Age</option>
            <option value="email">Email</option>
          </select>

          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
            className={styles.select}
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>

          <button onClick={handleSort} className={styles.btnSecondary}>
            Sort
          </button>
        </div>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h2>Create New Client</h2>
            <form onSubmit={handleCreate} className={styles.form}>
              <input
                type="text"
                placeholder="ID"
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                required
                className={styles.input}
              />
              <input
                type="text"
                placeholder="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className={styles.input}
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                className={styles.input}
              />
              <input
                type="number"
                placeholder="Age"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className={styles.input}
              />
              <input
                type="text"
                placeholder="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className={styles.input}
              />
              <div className={styles.formActions}>
                <button type="submit" className={styles.btnPrimary} disabled={loading}>
                  {loading ? 'Creating...' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className={styles.btnSecondary}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Form */}
      {showEditForm && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h2>Edit Client</h2>
            <form onSubmit={handleUpdate} className={styles.form}>
              <input
                type="text"
                placeholder="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className={styles.input}
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                className={styles.input}
              />
              <input
                type="number"
                placeholder="Age"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className={styles.input}
              />
              <input
                type="text"
                placeholder="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className={styles.input}
              />
              <div className={styles.formActions}>
                <button type="submit" className={styles.btnPrimary} disabled={loading}>
                  {loading ? 'Updating...' : 'Update'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowEditForm(false)}
                  className={styles.btnSecondary}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Clients List */}
      <div className={styles.clientsList}>
        {loading ? (
          <div className={styles.loading}>Loading...</div>
        ) : clients.length === 0 ? (
          <div className={styles.empty}>No clients found</div>
        ) : (
          clients.map((client) => (
            <div key={client.id} className={styles.clientCard}>
              <div className={styles.clientInfo}>
                <h3>{client.name}</h3>
                <p><strong>ID:</strong> {client.id}</p>
                <p><strong>Email:</strong> {client.email}</p>
                {client.age && <p><strong>Age:</strong> {client.age}</p>}
                {client.phone && <p><strong>Phone:</strong> {client.phone}</p>}
              </div>
              <div className={styles.clientActions}>
                <button
                  onClick={() => handleEdit(client)}
                  className={styles.btnEdit}
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(client.id)}
                  className={styles.btnDelete}
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ClientsPage; 