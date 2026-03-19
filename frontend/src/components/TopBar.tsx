import React, { useState } from 'react';
import { Box, Typography, IconButton, Menu, MenuItem, Chip } from '@mui/material';
import { AccountCircle, Logout } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { logout } from '../store/authSlice';
import { useNavigate } from 'react-router-dom';
import { COLORS } from '../theme/darkTheme';
import ConnectionStatus from './common/ConnectionStatus';
import PriceCell from './common/PriceCell';

const TopBar: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/auth');
  };

  return (
    <Box sx={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      height: 40, px: 2, bgcolor: COLORS.bg.secondary, borderBottom: `1px solid ${COLORS.border}`,
    }}>
      {/* Left */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography sx={{ fontWeight: 700, fontSize: '0.9rem', color: COLORS.primary, letterSpacing: '-0.02em' }}>
          GALLEGUIMETRO
        </Typography>
        <Chip label="GGAL" size="small" sx={{ bgcolor: COLORS.bg.elevated, color: COLORS.text.primary, fontWeight: 600 }} />
        <PriceCell value={637.47} prefix="$" size="md" />
      </Box>

      {/* Right */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <ConnectionStatus connected={false} />
        <Typography variant="caption" sx={{ color: COLORS.text.muted }}>
          {user?.username}
        </Typography>
        <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ color: COLORS.text.secondary }}>
          <AccountCircle fontSize="small" />
        </IconButton>
        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
          <MenuItem onClick={handleLogout}>
            <Logout fontSize="small" sx={{ mr: 1 }} /> Cerrar Sesión
          </MenuItem>
        </Menu>
      </Box>
    </Box>
  );
};

export default TopBar;
