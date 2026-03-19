/**
 * Client-side Black-Scholes and payoff calculations for strategy analysis.
 */

// Standard normal CDF approximation (Abramowitz & Stegun)
function normCdf(x: number): number {
  const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741;
  const a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911;
  const sign = x < 0 ? -1 : 1;
  const t = 1.0 / (1.0 + p * Math.abs(x));
  const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x / 2);
  return 0.5 * (1 + sign * y);
}

function normPdf(x: number): number {
  return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
}

export function bsPrice(
  S: number, K: number, T: number, r: number, sigma: number, type: 'call' | 'put'
): number {
  if (T <= 0) return type === 'call' ? Math.max(0, S - K) : Math.max(0, K - S);
  if (sigma <= 0) return type === 'call' ? Math.max(0, S * Math.exp(-r * T) - K) : Math.max(0, K - S * Math.exp(-r * T));

  const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
  const d2 = d1 - sigma * Math.sqrt(T);

  if (type === 'call') {
    return S * normCdf(d1) - K * Math.exp(-r * T) * normCdf(d2);
  } else {
    return K * Math.exp(-r * T) * normCdf(-d2) - S * normCdf(-d1);
  }
}

export function bsDelta(S: number, K: number, T: number, r: number, sigma: number, type: 'call' | 'put'): number {
  if (T <= 0 || sigma <= 0) return type === 'call' ? (S > K ? 1 : 0) : (S < K ? -1 : 0);
  const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
  return type === 'call' ? normCdf(d1) : normCdf(d1) - 1;
}

export function bsGamma(S: number, K: number, T: number, r: number, sigma: number): number {
  if (T <= 0 || sigma <= 0) return 0;
  const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
  return normPdf(d1) / (S * sigma * Math.sqrt(T));
}

export function bsTheta(S: number, K: number, T: number, r: number, sigma: number, type: 'call' | 'put'): number {
  if (T <= 0 || sigma <= 0) return 0;
  const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
  const d2 = d1 - sigma * Math.sqrt(T);
  const term1 = -(S * normPdf(d1) * sigma) / (2 * Math.sqrt(T));
  if (type === 'call') {
    return (term1 - r * K * Math.exp(-r * T) * normCdf(d2)) / 365;
  } else {
    return (term1 + r * K * Math.exp(-r * T) * normCdf(-d2)) / 365;
  }
}

export function bsVega(S: number, K: number, T: number, r: number, sigma: number): number {
  if (T <= 0 || sigma <= 0) return 0;
  const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
  return S * normPdf(d1) * Math.sqrt(T) / 100;
}

export interface PayoffLeg {
  type: 'call' | 'put';
  strike: number;
  quantity: number; // positive = long, negative = short
  premium: number; // price paid/received per contract
  iv?: number;
}

export interface PayoffPoint {
  price: number;
  pnl: number;
  pnlToday?: number;
}

export function calculatePayoff(
  legs: PayoffLeg[],
  spotPrice: number,
  priceRange?: { min: number; max: number; steps: number },
): PayoffPoint[] {
  const range = priceRange || {
    min: spotPrice * 0.6,
    max: spotPrice * 1.4,
    steps: 200,
  };
  const step = (range.max - range.min) / range.steps;
  const points: PayoffPoint[] = [];

  for (let i = 0; i <= range.steps; i++) {
    const price = range.min + step * i;
    let pnl = 0;

    for (const leg of legs) {
      let legValue: number;
      if (leg.type === 'call') {
        legValue = Math.max(0, price - leg.strike);
      } else {
        legValue = Math.max(0, leg.strike - price);
      }
      pnl += (legValue - leg.premium) * leg.quantity;
    }

    points.push({ price: Math.round(price * 100) / 100, pnl: Math.round(pnl * 100) / 100 });
  }

  return points;
}

export function calculatePayoffAtDate(
  legs: PayoffLeg[],
  spotPrice: number,
  daysToExpiry: number,
  riskFreeRate: number = 0.40,
  priceRange?: { min: number; max: number; steps: number },
): PayoffPoint[] {
  const range = priceRange || {
    min: spotPrice * 0.6,
    max: spotPrice * 1.4,
    steps: 200,
  };
  const step = (range.max - range.min) / range.steps;
  const T = Math.max(0.001, daysToExpiry / 365);
  const points: PayoffPoint[] = [];

  for (let i = 0; i <= range.steps; i++) {
    const price = range.min + step * i;
    let pnlToday = 0;
    let pnlExpiry = 0;

    for (const leg of legs) {
      const iv = leg.iv || 0.55;
      const optionValue = bsPrice(price, leg.strike, T, riskFreeRate, iv, leg.type);
      pnlToday += (optionValue - leg.premium) * leg.quantity;

      const expiryValue = leg.type === 'call' ? Math.max(0, price - leg.strike) : Math.max(0, leg.strike - price);
      pnlExpiry += (expiryValue - leg.premium) * leg.quantity;
    }

    points.push({
      price: Math.round(price * 100) / 100,
      pnl: Math.round(pnlExpiry * 100) / 100,
      pnlToday: Math.round(pnlToday * 100) / 100,
    });
  }

  return points;
}

export function findBreakevens(points: PayoffPoint[]): number[] {
  const breakevens: number[] = [];
  for (let i = 1; i < points.length; i++) {
    if ((points[i - 1].pnl <= 0 && points[i].pnl >= 0) ||
        (points[i - 1].pnl >= 0 && points[i].pnl <= 0)) {
      // Linear interpolation
      const ratio = Math.abs(points[i - 1].pnl) / (Math.abs(points[i - 1].pnl) + Math.abs(points[i].pnl));
      breakevens.push(Math.round((points[i - 1].price + ratio * (points[i].price - points[i - 1].price)) * 100) / 100);
    }
  }
  return breakevens;
}

export function getMaxProfit(points: PayoffPoint[]): number {
  return Math.max(...points.map(p => p.pnl));
}

export function getMaxLoss(points: PayoffPoint[]): number {
  return Math.min(...points.map(p => p.pnl));
}
