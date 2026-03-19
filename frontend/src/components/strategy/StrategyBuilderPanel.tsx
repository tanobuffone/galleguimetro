import React, { useState, useMemo } from 'react';
import {
  Box, Typography, Button, TextField, Select, MenuItem, FormControl, InputLabel,
  IconButton, Grid, Chip, Divider, ToggleButton, ToggleButtonGroup,
} from '@mui/material';
import { Add, Delete, Calculate } from '@mui/icons-material';
import { COLORS } from '../../theme/darkTheme';
import MetricCard from '../common/MetricCard';
import { PayoffLeg, calculatePayoff, findBreakevens, getMaxProfit, getMaxLoss } from '../../utils/payoffCalculator';

interface LegInput {
  id: number;
  action: 'buy' | 'sell';
  type: 'call' | 'put';
  strike: number;
  quantity: number;
  premium: number;
  iv: number;
}

const PRESETS = [
  { name: 'Bull Call Spread', legs: [
    { action: 'buy' as const, type: 'call' as const, strikeOffset: -1 },
    { action: 'sell' as const, type: 'call' as const, strikeOffset: 1 },
  ]},
  { name: 'Bear Put Spread', legs: [
    { action: 'buy' as const, type: 'put' as const, strikeOffset: 1 },
    { action: 'sell' as const, type: 'put' as const, strikeOffset: -1 },
  ]},
  { name: 'Straddle', legs: [
    { action: 'buy' as const, type: 'call' as const, strikeOffset: 0 },
    { action: 'buy' as const, type: 'put' as const, strikeOffset: 0 },
  ]},
  { name: 'Strangle', legs: [
    { action: 'buy' as const, type: 'call' as const, strikeOffset: 1 },
    { action: 'buy' as const, type: 'put' as const, strikeOffset: -1 },
  ]},
  { name: 'Iron Condor', legs: [
    { action: 'sell' as const, type: 'put' as const, strikeOffset: -1 },
    { action: 'buy' as const, type: 'put' as const, strikeOffset: -2 },
    { action: 'sell' as const, type: 'call' as const, strikeOffset: 1 },
    { action: 'buy' as const, type: 'call' as const, strikeOffset: 2 },
  ]},
  { name: 'Butterfly', legs: [
    { action: 'buy' as const, type: 'call' as const, strikeOffset: -1 },
    { action: 'sell' as const, type: 'call' as const, strikeOffset: 0 },
    { action: 'sell' as const, type: 'call' as const, strikeOffset: 0 },
    { action: 'buy' as const, type: 'call' as const, strikeOffset: 1 },
  ]},
];

const spotPrice = 637.47;
const strikeStep = 20;
let nextId = 1;

const StrategyBuilderPanel: React.FC = () => {
  const [legs, setLegs] = useState<LegInput[]>([]);
  const [strategyName, setStrategyName] = useState('');

  const addLeg = () => {
    setLegs([...legs, {
      id: nextId++, action: 'buy', type: 'call',
      strike: Math.round(spotPrice / strikeStep) * strikeStep,
      quantity: 1, premium: 30, iv: 0.55,
    }]);
  };

  const updateLeg = (id: number, field: string, value: any) => {
    setLegs(legs.map(l => l.id === id ? { ...l, [field]: value } : l));
  };

  const removeLeg = (id: number) => setLegs(legs.filter(l => l.id !== id));

  const applyPreset = (preset: typeof PRESETS[0]) => {
    const baseStrike = Math.round(spotPrice / strikeStep) * strikeStep;
    const newLegs = preset.legs.map((p, i) => ({
      id: nextId++,
      action: p.action,
      type: p.type,
      strike: baseStrike + p.strikeOffset * strikeStep,
      quantity: 1,
      premium: 30,
      iv: 0.55,
    }));
    setLegs(newLegs);
    setStrategyName(preset.name);
  };

  // Calculate metrics
  const payoffLegs: PayoffLeg[] = useMemo(() =>
    legs.map(l => ({
      type: l.type,
      strike: l.strike,
      quantity: l.action === 'buy' ? l.quantity : -l.quantity,
      premium: l.premium,
      iv: l.iv,
    })),
    [legs]
  );

  const payoffData = useMemo(() => calculatePayoff(payoffLegs, spotPrice), [payoffLegs]);
  const breakevens = useMemo(() => findBreakevens(payoffData), [payoffData]);
  const maxProfit = useMemo(() => legs.length > 0 ? getMaxProfit(payoffData) : 0, [payoffData, legs]);
  const maxLoss = useMemo(() => legs.length > 0 ? getMaxLoss(payoffData) : 0, [payoffData, legs]);
  const netCost = useMemo(() => legs.reduce((s, l) => s + l.premium * (l.action === 'buy' ? -l.quantity : l.quantity), 0), [legs]);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ px: 1.5, py: 0.75, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: `1px solid ${COLORS.border}` }}>
        <Typography variant="h6" sx={{ fontSize: '0.85rem' }}>Strategy Builder</Typography>
        <Button size="small" startIcon={<Add />} onClick={addLeg} variant="outlined">Leg</Button>
      </Box>

      {/* Presets */}
      <Box sx={{ display: 'flex', gap: 0.5, px: 1.5, py: 0.75, flexWrap: 'wrap', borderBottom: `1px solid ${COLORS.border}` }}>
        {PRESETS.map(p => (
          <Chip key={p.name} label={p.name} size="small" clickable onClick={() => applyPreset(p)}
            sx={{ fontSize: '0.65rem', bgcolor: COLORS.bg.elevated }} />
        ))}
      </Box>

      {/* Legs */}
      <Box sx={{ flex: 1, overflow: 'auto', px: 1.5, py: 1 }}>
        {legs.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4, color: COLORS.text.muted }}>
            <Typography variant="body2">Seleccioná un preset o agregá legs manualmente</Typography>
          </Box>
        ) : (
          legs.map((leg, i) => (
            <Box key={leg.id} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
              <ToggleButtonGroup size="small" exclusive value={leg.action}
                onChange={(_, v) => v && updateLeg(leg.id, 'action', v)}>
                <ToggleButton value="buy" sx={{ fontSize: '0.65rem', py: 0.25, color: COLORS.profit, '&.Mui-selected': { bgcolor: `${COLORS.profit}20`, color: COLORS.profit } }}>BUY</ToggleButton>
                <ToggleButton value="sell" sx={{ fontSize: '0.65rem', py: 0.25, color: COLORS.loss, '&.Mui-selected': { bgcolor: `${COLORS.loss}20`, color: COLORS.loss } }}>SELL</ToggleButton>
              </ToggleButtonGroup>

              <ToggleButtonGroup size="small" exclusive value={leg.type}
                onChange={(_, v) => v && updateLeg(leg.id, 'type', v)}>
                <ToggleButton value="call" sx={{ fontSize: '0.65rem', py: 0.25 }}>CALL</ToggleButton>
                <ToggleButton value="put" sx={{ fontSize: '0.65rem', py: 0.25 }}>PUT</ToggleButton>
              </ToggleButtonGroup>

              <TextField size="small" label="Strike" type="number" value={leg.strike}
                onChange={e => updateLeg(leg.id, 'strike', Number(e.target.value))}
                sx={{ width: 90 }} inputProps={{ step: strikeStep }} />

              <TextField size="small" label="Qty" type="number" value={leg.quantity}
                onChange={e => updateLeg(leg.id, 'quantity', Math.max(1, Number(e.target.value)))}
                sx={{ width: 60 }} />

              <TextField size="small" label="Prima" type="number" value={leg.premium}
                onChange={e => updateLeg(leg.id, 'premium', Number(e.target.value))}
                sx={{ width: 80 }} />

              <IconButton size="small" onClick={() => removeLeg(leg.id)} sx={{ color: COLORS.loss }}>
                <Delete fontSize="small" />
              </IconButton>
            </Box>
          ))
        )}

        {/* Metrics */}
        {legs.length > 0 && (
          <>
            <Divider sx={{ my: 1.5 }} />
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <MetricCard label="Costo Neto" value={netCost} />
              <MetricCard label="Max Profit" value={maxProfit} />
              <MetricCard label="Max Loss" value={maxLoss} />
              {breakevens.map((be, i) => (
                <MetricCard key={i} label={`Breakeven ${i + 1}`} value={be} colored={false} />
              ))}
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
};

export default StrategyBuilderPanel;
