import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Portfolio, PortfolioPosition } from '../types/portfolio';

interface PortfolioState {
  portfolios: Portfolio[];
  selectedPortfolio: Portfolio | null;
  loading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  portfolios: [],
  selectedPortfolio: null,
  loading: false,
  error: null,
};

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setPortfolios: (state, action: PayloadAction<Portfolio[]>) => {
      state.portfolios = action.payload;
    },
    setSelectedPortfolio: (state, action: PayloadAction<Portfolio>) => {
      state.selectedPortfolio = action.payload;
    },
    addPortfolio: (state, action: PayloadAction<Portfolio>) => {
      state.portfolios.push(action.payload);
    },
    updatePortfolio: (state, action: PayloadAction<Portfolio>) => {
      const index = state.portfolios.findIndex(p => p.id === action.payload.id);
      if (index !== -1) {
        state.portfolios[index] = action.payload;
        if (state.selectedPortfolio?.id === action.payload.id) {
          state.selectedPortfolio = action.payload;
        }
      }
    },
    removePortfolio: (state, action: PayloadAction<string>) => {
      state.portfolios = state.portfolios.filter(p => p.id !== action.payload);
      if (state.selectedPortfolio?.id === action.payload) {
        state.selectedPortfolio = null;
      }
    },
    addPosition: (state, action: PayloadAction<{ portfolioId: string; position: PortfolioPosition }>) => {
      const portfolio = state.portfolios.find(p => p.id === action.payload.portfolioId);
      if (portfolio) {
        if (!portfolio.positions) portfolio.positions = [];
        portfolio.positions.push(action.payload.position);
        if (state.selectedPortfolio?.id === action.payload.portfolioId) {
          state.selectedPortfolio = { ...portfolio };
        }
      }
    },
    updatePosition: (state, action: PayloadAction<{ portfolioId: string; positionId: string; position: PortfolioPosition }>) => {
      const portfolio = state.portfolios.find(p => p.id === action.payload.portfolioId);
      if (portfolio?.positions) {
        const idx = portfolio.positions.findIndex(p => p.id === action.payload.positionId);
        if (idx !== -1) {
          portfolio.positions[idx] = action.payload.position;
          if (state.selectedPortfolio?.id === action.payload.portfolioId) {
            state.selectedPortfolio = { ...portfolio };
          }
        }
      }
    },
    removePosition: (state, action: PayloadAction<{ portfolioId: string; positionId: string }>) => {
      const portfolio = state.portfolios.find(p => p.id === action.payload.portfolioId);
      if (portfolio?.positions) {
        portfolio.positions = portfolio.positions.filter(p => p.id !== action.payload.positionId);
        if (state.selectedPortfolio?.id === action.payload.portfolioId) {
          state.selectedPortfolio = { ...portfolio };
        }
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setPortfolios,
  setSelectedPortfolio,
  addPortfolio,
  updatePortfolio,
  removePortfolio,
  addPosition,
  updatePosition,
  removePosition,
  setLoading,
  setError,
  clearError,
} = portfolioSlice.actions;

export default portfolioSlice.reducer;
