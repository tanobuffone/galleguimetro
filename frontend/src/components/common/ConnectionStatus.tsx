import React from 'react';
import { Box, Tooltip } from '@mui/material';
import { COLORS } from '../../theme/darkTheme';

interface ConnectionStatusProps {
  connected: boolean;
  label?: string;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ connected, label = 'WebSocket' }) => (
  <Tooltip title={`${label}: ${connected ? 'Conectado' : 'Desconectado'}`}>
    <Box sx={{
      width: 8, height: 8, borderRadius: '50%',
      bgcolor: connected ? COLORS.profit : COLORS.loss,
      boxShadow: connected ? `0 0 6px ${COLORS.profit}` : `0 0 6px ${COLORS.loss}`,
    }} />
  </Tooltip>
);

export default ConnectionStatus;
