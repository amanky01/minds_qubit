import api from "../network/core/axiosInstance";
import config from "../network/config/config";

// Get all clients


export const getRoot = async () => {
  try {
    console.log('🔍 Attempting to fetch clients from:', `${config.API_BASE_URL}`);
    const response = await api.get("/");
    console.log('✅ Successfully fetched clients:', response.data);
    return response.data;

  } catch (error) {
    console.error("❌ Error fetching clients:", error);

  }

}

export const getClients = async () => {
  try {
    console.log('🔍 Attempting to fetch clients from:', `${config.API_BASE_URL}/clients`);
    const response = await api.get("/clients");
    console.log('✅ Successfully fetched clients:', response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching clients:", error);
    console.error("🔍 Error details:", {
      code: error.code,
      message: error.message,
      response: error.response,
      request: error.request,
      config: error.config
    });

    // Provide more specific error information
    if (error.code === 'ECONNREFUSED') {
      throw new Error(`Cannot connect to backend server. Please ensure your FastAPI server is running at ${config.API_BASE_URL}`);
    } else if (error.response) {
      // Server responded with error status
      throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check if your backend is running and accessible.');
    } else {
      // Something else happened
      throw new Error(`Network error: ${error.message}`);
    }
  }
};

// Get client by ID
export const getClientById = async (clientId) => {
  try {
    const response = await api.get(`/clients/${clientId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching client ${clientId}:`, error);
    throw error;
  }
};

// Sort clients
export const sortClients = async (sortBy, order = "asc") => {
  try {
    const response = await api.get("/sort", {
      params: { sort_by: sortBy, order }
    });
    return response.data;
  } catch (error) {
    console.error("Error sorting clients:", error);
    throw error;
  }
};

// Create new client
export const createClient = async (clientData) => {
  try {
    console.log('🔍 Attempting to create client at:', `${config.API_BASE_URL}/create`);
    console.log('📝 Client data:', clientData);
    const response = await api.post("/create", clientData);
    console.log('✅ Successfully created client:', response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Error creating client:", error);
    console.error("🔍 Error details:", {
      code: error.code,
      message: error.message,
      response: error.response,
      request: error.request,
      config: error.config
    });

    // Provide more specific error information
    if (error.code === 'ECONNREFUSED') {
      throw new Error(`Cannot connect to backend server. Please ensure your FastAPI server is running at ${config.API_BASE_URL}`);
    } else if (error.response) {
      // Server responded with error status
      throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check if your backend is running and accessible.');
    } else {
      // Something else happened
      throw new Error(`Network error: ${error.message}`);
    }
  }
};

// Update client
export const updateClient = async (clientId, updateData) => {
  try {
    const response = await api.put(`/edit/${clientId}`, updateData);
    return response.data;
  } catch (error) {
    console.error(`Error updating client ${clientId}:`, error);
    throw error;
  }
};

// Delete client
export const deleteClient = async (clientId) => {
  try {
    const response = await api.delete(`/delete/${clientId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting client ${clientId}:`, error);
    throw error;
  }
};

// Test API connection
export const testApiConnection = async () => {
  try {
    const response = await api.get("/");
    return { success: true, message: "API connection successful", data: response.data };
  } catch (error) {
    return {
      success: false,
      message: "API connection failed",
      error: error.message,
      details: error
    };
  }
};

export default {
  getClients,
  getClientById,
  sortClients,
  createClient,
  updateClient,
  deleteClient,
  testApiConnection
};