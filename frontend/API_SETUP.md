# API Integration Setup Guide

This guide explains how to use the API functions and the clients page that integrates with your FastAPI backend.

## Setup

### 1. Backend Setup
Make sure your FastAPI backend is running on `http://localhost:8000`. The backend should have the following endpoints:

- `GET /clients` - Get all clients
- `GET /clients/{client_id}` - Get client by ID
- `GET /sort` - Sort clients by field
- `POST /create` - Create new client
- `PUT /edit/{client_id}` - Update client
- `DELETE /delete/{client_id}` - Delete client

### 2. Environment Configuration
The API base URL is read from `NEXT_PUBLIC_API_BASE_URL` in `src/network/config/config.js` (default: `http://127.0.0.1:8000/`).

Copy `.env.example` to `.env` and set your backend URL:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/
```

For production (e.g. Vercel), set the same variable in your hosting dashboard.

## API Functions

All API functions are available in `src/services/getService.jsx`:

### `getClients()`
Fetches all clients from the backend.

### `getClientById(clientId)`
Fetches a specific client by ID.

### `sortClients(sortBy, order)`
Sorts clients by a specific field. 
- `sortBy`: Field to sort by (name, age, email)
- `order`: Sort order ('asc' or 'desc')

### `createClient(clientData)`
Creates a new client. The `clientData` should include:
- `id`: Unique identifier
- `name`: Client name
- `email`: Client email
- `age`: Client age (optional)
- `phone`: Client phone (optional)

### `updateClient(clientId, updateData)`
Updates an existing client. Only include fields that need to be updated.

### `deleteClient(clientId)`
Deletes a client by ID.

## Usage Example

```jsx
import { getClients, createClient } from '../services/getService';

// Fetch all clients
const clients = await getClients();

// Create a new client
const newClient = await createClient({
  id: 'client4',
  name: 'Alice Brown',
  email: 'alice.brown@example.com',
  age: 28,
  phone: '+1-555-0126'
});
```

## Clients Page

The `src/pages/clients.tsx` page demonstrates all API functions with a modern UI:

### Features:
- **View all clients** in a responsive grid layout
- **Create new clients** with a modal form
- **Edit existing clients** with inline editing
- **Delete clients** with confirmation
- **Sort clients** by name, age, or email
- **Responsive design** for mobile and desktop

### Navigation:
To access the clients page, navigate to `/clients` in your Next.js application.

## Error Handling

All API functions include proper error handling:
- Network errors are caught and logged
- User-friendly error messages are displayed
- Loading states are managed automatically

## Data Structure

The expected client data structure:
```json
{
  "client_id": {
    "name": "Client Name",
    "email": "client@example.com",
    "age": 30,
    "phone": "+1-555-0123"
  }
}
```

## Troubleshooting

1. **CORS Issues**: Ensure your FastAPI backend allows requests from your frontend domain
2. **Connection Errors**: Verify the backend is running and accessible at the configured URL
3. **Data Format**: Ensure the backend returns data in the expected format

## Next Steps

1. Start your FastAPI backend
2. Navigate to `/clients` in your Next.js app
3. Test the CRUD operations
4. Customize the UI and functionality as needed 