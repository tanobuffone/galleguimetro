export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  owner_id?: string;
  total_market_value: number;
  total_unrealized_pnl: number;
  total_realized_pnl: number;
  created_at: string;
  updated_at: string;
  positions: PortfolioPosition[];
}

export interface PortfolioPosition {
  id: string;
  portfolio_id: string;
  option_id: string;
  symbol?: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  status: string;
  entry_date: string;
  exit_date?: string;
  fees: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioMetrics {
  totalPositions: number;
  totalUnrealizedPnl: number;
  totalRealizedPnl: number;
  totalMarketValue: number;
}

export interface CreatePortfolioRequest {
  name: string;
  description?: string;
}

export interface UpdatePortfolioRequest {
  name?: string;
  description?: string;
}

export interface CreatePositionRequest {
  option_id: string;
  quantity: number;
  entry_price: number;
  current_price?: number;
  fees?: number;
}

export interface UpdatePositionRequest {
  quantity?: number;
  current_price?: number;
  status?: string;
  fees?: number;
}
