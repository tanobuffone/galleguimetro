export interface Option {
  id: string;
  symbol: string;
  underlying_id: string;
  option_type: 'call' | 'put';
  strike_price: number;
  expiration_date: string;
  implied_volatility?: number;
  dividend_yield: number;
  risk_free_rate: number;
  last_price?: number;
  bid?: number;
  ask?: number;
  created_at: string;
  updated_at: string;
}

export interface OptionGreeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

export interface OptionChain {
  symbol: string;
  options: Option[];
}

export interface CreateOptionRequest {
  symbol: string;
  underlying_symbol: string;
  option_type: 'call' | 'put';
  strike_price: number;
  expiration_date: string;
  implied_volatility?: number;
  dividend_yield?: number;
  risk_free_rate?: number;
  last_price?: number;
  bid?: number;
  ask?: number;
}

export interface UpdateOptionRequest {
  implied_volatility?: number;
  last_price?: number;
  bid?: number;
  ask?: number;
}

export interface CalculateGreeksRequest {
  option_data: {
    symbol: string;
    underlying_symbol: string;
    option_type: 'call' | 'put';
    strike_price: number;
    expiration_date: string;
    implied_volatility?: number;
  };
  spot_price: number;
  risk_free_rate: number;
  dividend_yield?: number;
  time_to_expiration_years: number;
}
