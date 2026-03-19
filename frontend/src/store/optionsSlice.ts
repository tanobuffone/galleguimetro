import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Option, OptionGreeks } from '../types/options';

interface OptionsState {
  options: Option[];
  selectedOption: Option | null;
  greeks: OptionGreeks | null;
  loading: boolean;
  error: string | null;
}

const initialState: OptionsState = {
  options: [],
  selectedOption: null,
  greeks: null,
  loading: false,
  error: null,
};

const optionsSlice = createSlice({
  name: 'options',
  initialState,
  reducers: {
    setOptions: (state, action: PayloadAction<Option[]>) => {
      state.options = action.payload;
    },
    setSelectedOption: (state, action: PayloadAction<Option>) => {
      state.selectedOption = action.payload;
    },
    addOption: (state, action: PayloadAction<Option>) => {
      state.options.push(action.payload);
    },
    updateOption: (state, action: PayloadAction<Option>) => {
      const index = state.options.findIndex(o => o.id === action.payload.id);
      if (index !== -1) {
        state.options[index] = action.payload;
        if (state.selectedOption?.id === action.payload.id) {
          state.selectedOption = action.payload;
        }
      }
    },
    removeOption: (state, action: PayloadAction<string>) => {
      state.options = state.options.filter(o => o.id !== action.payload);
      if (state.selectedOption?.id === action.payload) {
        state.selectedOption = null;
      }
    },
    setGreeks: (state, action: PayloadAction<OptionGreeks>) => {
      state.greeks = action.payload;
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
  setOptions,
  setSelectedOption,
  addOption,
  updateOption,
  removeOption,
  setGreeks,
  setLoading,
  setError,
  clearError,
} = optionsSlice.actions;

export default optionsSlice.reducer;
