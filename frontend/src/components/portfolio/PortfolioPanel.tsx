import React, { useEffect, useState } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Chip, CircularProgress,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store/store';
import { setPortfolios, setLoading, setSelectedPortfolio } from '../../store/portfolioSlice';
import { PortfolioService } from '../../services/api';
import { COLORS } from '../../theme/darkTheme';
import MetricCard from '../common/MetricCard';
import PriceCell from '../common/PriceCell';
import { Portfolio } from '../../types/portfolio';

const PortfolioPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { portfolios, selectedPortfolio, loading } = useSelector((state: RootState) => state.portfolio);

  useEffect(() => {
    const fetch = async () => {
      dispatch(setLoading(true));
      try {
        const resp = await PortfolioService.getPortfolios();
        if (resp?.items) {
          dispatch(setPortfolios(resp.items));
          if (resp.items.length > 0 && !selectedPortfolio) {
            dispatch(setSelectedPortfolio(resp.items[0]));
          }
        }
      } catch (e) { console.error(e); }
      finally { dispatch(setLoading(false)); }
    };
    fetch();
  }, [dispatch]);

  const portfolio = selectedPortfolio;
  const positions = portfolio?.positions || [];
  const totalPnl = positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0);
  const totalValue = positions.reduce((s, p) => s + ((p.current_price || 0) * (p.quantity || 0)), 0);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>;

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ px: 1.5, py: 0.75, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: `1px solid ${COLORS.border}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" sx={{ fontSize: '0.85rem' }}>Portfolio</Typography>
          {portfolios.map(p => (
            <Chip key={p.id} label={p.name} size="small"
              variant={p.id === portfolio?.id ? 'filled' : 'outlined'}
              onClick={() => dispatch(setSelectedPortfolio(p))}
              sx={{ cursor: 'pointer', fontSize: '0.7rem' }} />
          ))}
        </Box>
      </Box>

      {/* Metrics */}
      <Box sx={{ display: 'flex', gap: 1, px: 1.5, py: 1, borderBottom: `1px solid ${COLORS.border}`, overflow: 'auto' }}>
        <MetricCard label="Valor" value={totalValue} />
        <MetricCard label="P&L No Realizado" value={totalPnl} />
        <MetricCard label="Posiciones" value={positions.length} prefix="" decimals={0} colored={false} />
      </Box>

      {/* Positions Table */}
      <TableContainer sx={{ flex: 1, overflow: 'auto' }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Opción</TableCell>
              <TableCell align="right">Qty</TableCell>
              <TableCell align="right">Entrada</TableCell>
              <TableCell align="right">Actual</TableCell>
              <TableCell align="right">P&L</TableCell>
              <TableCell>Estado</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {positions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ color: COLORS.text.muted, py: 4 }}>
                  Sin posiciones abiertas
                </TableCell>
              </TableRow>
            ) : positions.map(pos => (
              <TableRow key={pos.id}>
                <TableCell sx={{ fontFamily: '"Roboto Mono", monospace', fontSize: '0.75rem' }}>
                  {pos.option_id?.slice(0, 8)}...
                </TableCell>
                <TableCell align="right">
                  <PriceCell value={pos.quantity} decimals={0} prefix="" colored />
                </TableCell>
                <TableCell align="right"><PriceCell value={pos.entry_price} prefix="$" /></TableCell>
                <TableCell align="right"><PriceCell value={pos.current_price} prefix="$" /></TableCell>
                <TableCell align="right"><PriceCell value={pos.unrealized_pnl} prefix="$" colored /></TableCell>
                <TableCell>
                  <Chip label={pos.status} size="small"
                    sx={{ fontSize: '0.65rem', height: 20,
                      bgcolor: pos.status === 'open' ? `${COLORS.profit}20` : `${COLORS.text.muted}20`,
                      color: pos.status === 'open' ? COLORS.profit : COLORS.text.muted,
                    }} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PortfolioPanel;
