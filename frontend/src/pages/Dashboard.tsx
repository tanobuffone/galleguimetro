import React, { useEffect, useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, AppBar, Toolbar,
  IconButton, Menu, MenuItem, Avatar
} from '@mui/material';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { logout } from '../store/authSlice';
import { setPortfolios, setLoading } from '../store/portfolioSlice';
import { PortfolioService } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useSelector((state: RootState) => state.auth);
  const { portfolios } = useSelector((state: RootState) => state.portfolio);
  const [performanceData] = useState([
    { date: '2026-01', value: 10000 },
    { date: '2026-02', value: 12000 },
    { date: '2026-03', value: 15000 },
  ]);
  const [portfolioDistribution, setPortfolioDistribution] = useState<any[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        dispatch(setLoading(true));
        const response = await PortfolioService.getPortfolios();
        if (response?.items) {
          dispatch(setPortfolios(response.items));
          setPortfolioDistribution(
            response.items.map((p: any) => ({ name: p.name, value: p.total_market_value || 0 }))
          );
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        dispatch(setLoading(false));
      }
    };
    fetchData();
  }, [dispatch]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/auth');
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Galleguimetro Dashboard
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.username}
          </Typography>
          <IconButton size="large" onClick={(e) => setAnchorEl(e.currentTarget)} color="inherit"
            aria-label="cuenta de usuario" aria-controls="menu-appbar" aria-haspopup="true">
            <Avatar>{user?.username?.[0]?.toUpperCase() || 'U'}</Avatar>
          </IconButton>
          <Menu id="menu-appbar" anchorEl={anchorEl}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
            <MenuItem onClick={handleLogout}>Cerrar Sesión</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box sx={{ mt: 2, p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>Rendimiento del Portfolio</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>Distribución</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={portfolioDistribution} cx="50%" cy="50%" outerRadius={80}
                      fill="#8884d8" dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {portfolioDistribution.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>Resumen</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">Portfolios</Typography>
                    <Typography variant="h6">{portfolios.length}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">P&L Total</Typography>
                    <Typography variant="h6" color={
                      portfolios.reduce((s, p) => s + p.total_unrealized_pnl, 0) >= 0 ? 'green' : 'red'
                    }>
                      ${portfolios.reduce((s, p) => s + p.total_unrealized_pnl, 0).toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>Acciones Rápidas</Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Button variant="contained" color="primary" onClick={() => navigate('/portfolio')}>
                    Gestionar Portfolios
                  </Button>
                  <Button variant="contained" color="secondary" onClick={() => navigate('/options')}>
                    Ver Opciones
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard;
