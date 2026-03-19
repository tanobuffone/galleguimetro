import React from 'react';
import { Box } from '@mui/material';
import { COLORS } from '../../theme/darkTheme';

interface PriceCellProps {
  value: number | null | undefined;
  decimals?: number;
  prefix?: string;
  colored?: boolean;
  mono?: boolean;
  flash?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const PriceCell: React.FC<PriceCellProps> = ({
  value, decimals = 2, prefix = '', colored = false, mono = true, size = 'md',
}) => {
  if (value == null) return <Box sx={{ color: COLORS.text.muted }}>-</Box>;

  const color = colored
    ? value > 0 ? COLORS.profit : value < 0 ? COLORS.loss : COLORS.text.secondary
    : COLORS.text.primary;

  const fontSize = size === 'sm' ? '0.7rem' : size === 'lg' ? '1.1rem' : '0.8rem';

  return (
    <Box
      component="span"
      sx={{
        color,
        fontFamily: mono ? '"Roboto Mono", monospace' : 'inherit',
        fontSize,
        fontWeight: size === 'lg' ? 600 : 400,
      }}
    >
      {prefix}{value >= 0 && colored ? '+' : ''}{value.toFixed(decimals)}
    </Box>
  );
};

export default PriceCell;
