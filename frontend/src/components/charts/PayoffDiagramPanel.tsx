import React, { useState, useMemo } from 'react';
import {
  Box, Typography, Slider, FormControlLabel, Switch, Chip,
} from '@mui/material';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, Line, ComposedChart,
} from 'recharts';
import { COLORS } from '../../theme/darkTheme';
import { PayoffLeg, calculatePayoffAtDate } from '../../utils/payoffCalculator';

interface PayoffDiagramPanelProps {
  legs?: PayoffLeg[];
  spotPrice?: number;
}

// Demo legs (Bull Call Spread) if none provided
const DEMO_LEGS: PayoffLeg[] = [
  { type: 'call', strike: 637.47, quantity: 10, premium: 45, iv: 0.55 },
  { type: 'call', strike: 717.47, quantity: -10, premium: 12, iv: 0.55 },
];

const PayoffDiagramPanel: React.FC<PayoffDiagramPanelProps> = ({
  legs = DEMO_LEGS,
  spotPrice = 637.47,
}) => {
  const [daysToExpiry, setDaysToExpiry] = useState(29);
  const [showToday, setShowToday] = useState(true);

  const data = useMemo(() =>
    calculatePayoffAtDate(legs, spotPrice, daysToExpiry, 0.40),
    [legs, spotPrice, daysToExpiry]
  );

  // Split into positive and negative for area coloring
  const chartData = useMemo(() =>
    data.map(d => ({
      price: d.price,
      pnlExpiry: d.pnl,
      pnlToday: showToday ? d.pnlToday : undefined,
      positive: d.pnl > 0 ? d.pnl : 0,
      negative: d.pnl < 0 ? d.pnl : 0,
    })),
    [data, showToday]
  );

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ px: 1.5, py: 0.75, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: `1px solid ${COLORS.border}` }}>
        <Typography variant="h6" sx={{ fontSize: '0.85rem' }}>Payoff Diagram</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FormControlLabel
            control={<Switch size="small" checked={showToday} onChange={(_, v) => setShowToday(v)} />}
            label={<Typography variant="caption">P&L Hoy</Typography>}
          />
        </Box>
      </Box>

      {/* Days slider */}
      <Box sx={{ px: 2, py: 0.5, display: 'flex', alignItems: 'center', gap: 2, borderBottom: `1px solid ${COLORS.border}` }}>
        <Typography variant="caption" sx={{ minWidth: 70, color: COLORS.text.muted }}>
          Días: {daysToExpiry}
        </Typography>
        <Slider size="small" value={daysToExpiry} onChange={(_, v) => setDaysToExpiry(v as number)}
          min={0} max={90} step={1}
          sx={{ color: COLORS.primary, '& .MuiSlider-thumb': { width: 12, height: 12 } }} />
      </Box>

      {/* Chart */}
      <Box sx={{ flex: 1, p: 1 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis
              dataKey="price" type="number" domain={['dataMin', 'dataMax']}
              tick={{ fill: COLORS.text.muted, fontSize: 10 }}
              stroke={COLORS.border}
              tickFormatter={(v) => `$${v.toFixed(0)}`}
            />
            <YAxis
              tick={{ fill: COLORS.text.muted, fontSize: 10 }}
              stroke={COLORS.border}
              tickFormatter={(v) => `$${v.toFixed(0)}`}
            />
            <Tooltip
              contentStyle={{ backgroundColor: COLORS.bg.elevated, border: `1px solid ${COLORS.border}`, borderRadius: 4, fontSize: '0.75rem' }}
              labelFormatter={(v) => `Subyacente: $${Number(v).toFixed(2)}`}
              formatter={(v: number, name: string) => [`$${v.toFixed(2)}`, name === 'pnlExpiry' ? 'P&L Vencimiento' : 'P&L Hoy']}
            />

            {/* Zero line */}
            <ReferenceLine y={0} stroke={COLORS.text.muted} strokeDasharray="3 3" />

            {/* Spot price line */}
            <ReferenceLine x={spotPrice} stroke={COLORS.warning} strokeDasharray="5 5" label={{
              value: `Spot $${spotPrice}`, fill: COLORS.warning, fontSize: 10, position: 'top',
            }} />

            {/* Strike lines */}
            {legs.map((leg, i) => (
              <ReferenceLine key={i} x={leg.strike} stroke={COLORS.borderLight} strokeDasharray="2 2" />
            ))}

            {/* P&L at expiry areas */}
            <Area type="monotone" dataKey="positive" fill={`${COLORS.profit}30`} stroke="none" />
            <Area type="monotone" dataKey="negative" fill={`${COLORS.loss}30`} stroke="none" />

            {/* P&L at expiry line */}
            <Line type="monotone" dataKey="pnlExpiry" stroke={COLORS.text.primary} strokeWidth={2} dot={false} />

            {/* P&L today line */}
            {showToday && (
              <Line type="monotone" dataKey="pnlToday" stroke={COLORS.primary} strokeWidth={1.5} strokeDasharray="4 2" dot={false} />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default PayoffDiagramPanel;
