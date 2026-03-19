import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Helper: extraer data de ApiResponse
function extractData<T>(response: any): T {
  const apiResp = response.data;
  if (apiResp && apiResp.success !== undefined) {
    return apiResp.data as T;
  }
  return response.data;
}

// --- Auth ---
export const AuthService = {
  login: async (credentials: { username: string; password: string }) => {
    const response = await api.post('/auth/login', credentials);
    const data = extractData<{ access_token: string; user: any }>(response);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  },

  register: async (userData: { username: string; email: string; password: string; full_name?: string }) => {
    const response = await api.post('/auth/register', userData);
    const data = extractData<{ access_token: string; user: any }>(response);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: () => !!localStorage.getItem('token'),
};

// --- Portfolios ---
export const PortfolioService = {
  getPortfolios: async (page = 1, pageSize = 20) => {
    const response = await api.get('/portfolios', { params: { page, page_size: pageSize } });
    return extractData<any>(response);
  },

  getPortfolio: async (id: string) => {
    const response = await api.get(`/portfolios/${id}`);
    return extractData<any>(response);
  },

  createPortfolio: async (data: { name: string; description?: string }) => {
    const response = await api.post('/portfolios', data);
    return extractData<any>(response);
  },

  updatePortfolio: async (id: string, data: { name?: string; description?: string }) => {
    const response = await api.put(`/portfolios/${id}`, data);
    return extractData<any>(response);
  },

  deletePortfolio: async (id: string) => {
    await api.delete(`/portfolios/${id}`);
  },

  addPosition: async (portfolioId: string, data: any) => {
    const response = await api.post(`/portfolios/${portfolioId}/positions`, data);
    return extractData<any>(response);
  },

  updatePosition: async (portfolioId: string, positionId: string, data: any) => {
    const response = await api.put(`/portfolios/${portfolioId}/positions/${positionId}`, data);
    return extractData<any>(response);
  },

  removePosition: async (portfolioId: string, positionId: string) => {
    await api.delete(`/portfolios/${portfolioId}/positions/${positionId}`);
  },

  syncWithExcel: async (portfolioId: string, workbookName: string, portfolioExcelId: string) => {
    await api.post(`/portfolios/${portfolioId}/sync`, { workbookName, portfolioExcelId });
  },
};

// --- Options ---
export const OptionsService = {
  getOptions: async (page = 1, pageSize = 50) => {
    const response = await api.get('/options', { params: { page, page_size: pageSize } });
    return extractData<any>(response);
  },

  getOption: async (id: string) => {
    const response = await api.get(`/options/${id}`);
    return extractData<any>(response);
  },

  createOption: async (data: any) => {
    const response = await api.post('/options', data);
    return extractData<any>(response);
  },

  updateOption: async (id: string, data: any) => {
    const response = await api.put(`/options/${id}`, data);
    return extractData<any>(response);
  },

  deleteOption: async (id: string) => {
    await api.delete(`/options/${id}`);
  },

  calculateGreeks: async (request: any) => {
    const response = await api.post('/options/calculate-greeks', request);
    return extractData<any>(response);
  },

  getOptionChain: async (symbol: string) => {
    const response = await api.get(`/options/chain/${symbol}`);
    return extractData<any>(response);
  },
};

// --- Strategies ---
export const StrategyService = {
  getStrategies: async (portfolioId?: string) => {
    const params: any = {};
    if (portfolioId) params.portfolio_id = portfolioId;
    const response = await api.get('/strategies', { params });
    return extractData<any>(response);
  },

  createStrategy: async (data: any) => {
    const response = await api.post('/strategies', data);
    return extractData<any>(response);
  },

  deleteStrategy: async (id: string) => {
    await api.delete(`/strategies/${id}`);
  },
};

// --- Alerts ---
export const AlertService = {
  getAlerts: async (portfolioId?: string) => {
    const params: any = {};
    if (portfolioId) params.portfolio_id = portfolioId;
    const response = await api.get('/alerts', { params });
    return extractData<any>(response);
  },

  createAlert: async (data: any) => {
    const response = await api.post('/alerts', data);
    return extractData<any>(response);
  },

  deleteAlert: async (id: string) => {
    await api.delete(`/alerts/${id}`);
  },
};

// --- WebSocket ---
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Map<string, (data: any) => void> = new Map();

  connect(url: string = WS_BASE_URL): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onerror = (error) => reject(error);

      this.ws.onclose = () => {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => this.connect(url), this.reconnectDelay * this.reconnectAttempts);
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const handler = this.messageHandlers.get(message.type);
          if (handler) handler(message.data);
        } catch (e) {
          console.error('WS message parse error:', e);
        }
      };
    });
  }

  subscribe(channel: string, callback: (data: any) => void): void {
    this.messageHandlers.set(channel, callback);
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'subscribe', channel }));
    }
  }

  unsubscribe(channel: string): void {
    this.messageHandlers.delete(channel);
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'unsubscribe', channel }));
    }
  }

  disconnect(): void {
    this.maxReconnectAttempts = 0; // prevent reconnect
    this.ws?.close();
    this.ws = null;
  }
}

export const wsService = new WebSocketService();
export default api;
