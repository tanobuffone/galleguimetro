import React from 'react';
import { Box, Typography } from '@mui/material';
import { COLORS } from '../../theme/darkTheme';

interface MetricCardProps {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  colored?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({
  label, value, prefix = '$', suffix = '', decimals = 2, colored = true,
}) => {
  const color = colored
    ? value > 0 ? COLORS.profit : value < 0 ? COLORS.loss : COLORS.text.primary
    : COLORS.text.primary;

  return (
    <Box sx={{
      p: 1.5,
      borderRadius: 1,
      bgcolor: COLORS.bg.secondary,
      border: `1px solid ${COLORS.border}`,
      minWidth: 120,
    }}>
      <Typography variant="caption" sx={{ color: COLORS.text.muted, textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.65rem' }}>
        {label}
      </Typography>
      <Typography sx={{
        color,
        fontFamily: '"Roboto Mono", monospace',
        fontWeight: 600,
        fontSize: '1.1rem',
        mt: 0.25,
      }}>
        {prefix}{value >= 0 && colored ? '+' : ''}{value.toFixed(decimals)}{suffix}
      </Typography>
    </Box>
  );
};

export default MetricCard;
