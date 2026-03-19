import React, { useEffect, useState, useMemo } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab, Chip, CircularProgress,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store/store';
import { setOptions, setLoading } from '../../store/optionsSlice';
import { OptionsService } from '../../services/api';
import { COLORS } from '../../theme/darkTheme';
import PriceCell from '../common/PriceCell';
import { Option } from '../../types/options';

interface ChainRow {
  strike: number;
  call?: Option;
  put?: Option;
}

const OptionsChainPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { options, loading } = useSelector((state: RootState) => state.options);
  const [selectedExpiry, setSelectedExpiry] = useState(0);
  const spotPrice = 637.47; // TODO: from store

  useEffect(() => {
    const fetch = async () => {
      dispatch(setLoading(true));
      try {
        const resp = await OptionsService.getOptions(1, 500);
        if (resp?.items) dispatch(setOptions(resp.items));
      } catch (e) { console.error(e); }
      finally { dispatch(setLoading(false)); }
    };
    fetch();
  }, [dispatch]);

  // Group by expiration
  const expirations = useMemo(() => {
    const dates = Array.from(new Set(options.map(o => o.expiration_date?.split('T')[0]))).sort();
    return dates;
  }, [options]);

  // Build chain rows for selected expiration
  const chainRows = useMemo(() => {
    const expiry = expirations[selectedExpiry];
    if (!expiry) return [];

    const filtered = options.filter(o => o.expiration_date?.startsWith(expiry));
    const byStrike = new Map<number, ChainRow>();

    filtered.forEach(o => {
      const strike = o.strike_price;
      if (!byStrike.has(strike)) byStrike.set(strike, { strike });
      const row = byStrike.get(strike)!;
      if (o.option_type === 'call') row.call = o;
      else row.put = o;
    });

    return Array.from(byStrike.values()).sort((a, b) => a.strike - b.strike);
  }, [options, expirations, selectedExpiry]);

  const getMoneyness = (strike: number, type: 'call' | 'put') => {
    if (type === 'call') return strike < spotPrice ? 'itm' : strike === spotPrice ? 'atm' : 'otm';
    return strike > spotPrice ? 'itm' : strike === spotPrice ? 'atm' : 'otm';
  };

  const getRowBg = (strike: number) => {
    const diff = Math.abs(strike - spotPrice) / spotPrice;
    if (diff < 0.02) return COLORS.atm;
    if (strike < spotPrice) return COLORS.itm;
    return COLORS.otm;
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>;

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ px: 1.5, py: 0.75, display: 'flex', alignItems: 'center', gap: 1, borderBottom: `1px solid ${COLORS.border}` }}>
        <Typography variant="h6" sx={{ fontSize: '0.85rem', mr: 1 }}>Option Chain</Typography>
        <Chip label={`${options.length} opciones`} size="small" variant="outlined" />
      </Box>

      {/* Expiration Tabs */}
      {expirations.length > 0 && (
        <Tabs value={selectedExpiry} onChange={(_, v) => setSelectedExpiry(v)}
          sx={{ minHeight: 30, px: 1, borderBottom: `1px solid ${COLORS.border}` }}>
          {expirations.map((exp, i) => (
            <Tab key={exp} label={new Date(exp + 'T12:00:00').toLocaleDateString('es-AR', { month: 'short', year: '2-digit' })}
              sx={{ minHeight: 30, py: 0, fontSize: '0.7rem' }} />
          ))}
        </Tabs>
      )}

      {/* Chain Table */}
      <TableContainer sx={{ flex: 1, overflow: 'auto' }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell colSpan={5} align="center" sx={{ bgcolor: `${COLORS.call}15`, color: COLORS.call, fontWeight: 700 }}>
                CALLS
              </TableCell>
              <TableCell align="center" sx={{ bgcolor: COLORS.bg.elevated, fontWeight: 700 }}>STRIKE</TableCell>
              <TableCell colSpan={5} align="center" sx={{ bgcolor: `${COLORS.put}15`, color: COLORS.put, fontWeight: 700 }}>
                PUTS
              </TableCell>
            </TableRow>
            <TableRow>
              {/* Call headers */}
              <TableCell align="right">Bid</TableCell>
              <TableCell align="right">Ask</TableCell>
              <TableCell align="right">Last</TableCell>
              <TableCell align="right">IV</TableCell>
              <TableCell align="right">&Delta;</TableCell>
              {/* Strike */}
              <TableCell align="center" sx={{ fontWeight: 700 }}>Strike</TableCell>
              {/* Put headers */}
              <TableCell align="right">&Delta;</TableCell>
              <TableCell align="right">IV</TableCell>
              <TableCell align="right">Last</TableCell>
              <TableCell align="right">Bid</TableCell>
              <TableCell align="right">Ask</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {chainRows.map((row) => (
              <TableRow key={row.strike} sx={{ bgcolor: getRowBg(row.strike) }}>
                {/* Call side */}
                <TableCell align="right"><PriceCell value={row.call?.bid} /></TableCell>
                <TableCell align="right"><PriceCell value={row.call?.ask} /></TableCell>
                <TableCell align="right"><PriceCell value={row.call?.last_price} /></TableCell>
                <TableCell align="right">
                  <PriceCell value={row.call?.implied_volatility ? row.call.implied_volatility * 100 : null} decimals={1} />
                </TableCell>
                <TableCell align="right" sx={{ color: COLORS.call }}>
                  <PriceCell value={row.call ? parseFloat((bsDeltaApprox(spotPrice, row.strike, 'call')).toFixed(3)) : null} decimals={3} />
                </TableCell>
                {/* Strike */}
                <TableCell align="center" sx={{
                  fontWeight: 700, bgcolor: COLORS.bg.elevated,
                  fontFamily: '"Roboto Mono", monospace', fontSize: '0.8rem',
                  borderLeft: `2px solid ${COLORS.borderLight}`, borderRight: `2px solid ${COLORS.borderLight}`,
                }}>
                  {row.strike.toFixed(2)}
                </TableCell>
                {/* Put side */}
                <TableCell align="right" sx={{ color: COLORS.put }}>
                  <PriceCell value={row.put ? parseFloat((bsDeltaApprox(spotPrice, row.strike, 'put')).toFixed(3)) : null} decimals={3} />
                </TableCell>
                <TableCell align="right">
                  <PriceCell value={row.put?.implied_volatility ? row.put.implied_volatility * 100 : null} decimals={1} />
                </TableCell>
                <TableCell align="right"><PriceCell value={row.put?.last_price} /></TableCell>
                <TableCell align="right"><PriceCell value={row.put?.bid} /></TableCell>
                <TableCell align="right"><PriceCell value={row.put?.ask} /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

// Quick delta approximation for display (no QuantLib needed)
function bsDeltaApprox(spot: number, strike: number, type: 'call' | 'put'): number {
  const moneyness = Math.log(spot / strike);
  const approxDelta = 0.5 + 0.5 * Math.tanh(moneyness * 3);
  return type === 'call' ? approxDelta : approxDelta - 1;
}

export default OptionsChainPanel;
