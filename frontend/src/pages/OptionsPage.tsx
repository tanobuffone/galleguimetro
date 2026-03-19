import React, { useEffect, useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem, Alert, Tabs, Tab, InputAdornment
} from '@mui/material';
import {
  Add as AddIcon, Delete as DeleteIcon, Calculate as CalculateIcon, Search as SearchIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { setOptions, setLoading as setOptionsLoading, addOption, removeOption, setGreeks } from '../store/optionsSlice';
import { OptionsService } from '../services/api';
import { CalculateGreeksRequest, OptionGreeks } from '../types/options';

const OptionsPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { options, loading } = useSelector((state: RootState) => state.options);
  const [createDialog, setCreateDialog] = useState(false);
  const [calculateDialog, setCalculateDialog] = useState(false);
  const [createForm, setCreateForm] = useState({
    symbol: '', underlying_symbol: '', option_type: 'call' as 'call' | 'put',
    strike_price: 0, expiration_date: '', implied_volatility: 0.2,
    last_price: 0, bid: 0, ask: 0,
  });
  const [greeksForm, setGreeksForm] = useState({
    symbol: '', underlying_symbol: '', option_type: 'call' as 'call' | 'put',
    strike_price: 150, expiration_date: '', spot_price: 155,
    risk_free_rate: 0.03, implied_volatility: 0.2, time_to_expiration_years: 0.25,
  });
  const [calculatedGreeks, setCalculatedGreeks] = useState<OptionGreeks | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [tabValue, setTabValue] = useState(0);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        dispatch(setOptionsLoading(true));
        const response = await OptionsService.getOptions();
        if (response?.items) {
          dispatch(setOptions(response.items));
        }
      } catch (error) {
        console.error('Error fetching options:', error);
      } finally {
        dispatch(setOptionsLoading(false));
      }
    };
    fetchOptions();
  }, [dispatch]);

  const handleCreateOption = async () => {
    try {
      const response = await OptionsService.createOption(createForm);
      if (response) {
        dispatch(addOption(response));
        setCreateDialog(false);
        setMessage({ text: 'Opción creada', type: 'success' });
      }
    } catch {
      setMessage({ text: 'Error al crear opción', type: 'error' });
    }
  };

  const handleDeleteOption = async (id: string) => {
    if (!window.confirm('¿Eliminar esta opción?')) return;
    try {
      await OptionsService.deleteOption(id);
      dispatch(removeOption(id));
    } catch {
      setMessage({ text: 'Error al eliminar opción', type: 'error' });
    }
  };

  const handleCalculateGreeks = async () => {
    try {
      const request: CalculateGreeksRequest = {
        option_data: {
          symbol: greeksForm.symbol || 'CALC',
          underlying_symbol: greeksForm.underlying_symbol || 'TEST',
          option_type: greeksForm.option_type,
          strike_price: greeksForm.strike_price,
          expiration_date: greeksForm.expiration_date,
          implied_volatility: greeksForm.implied_volatility,
        },
        spot_price: greeksForm.spot_price,
        risk_free_rate: greeksForm.risk_free_rate,
        time_to_expiration_years: greeksForm.time_to_expiration_years,
      };
      const response = await OptionsService.calculateGreeks(request);
      if (response?.greeks) {
        setCalculatedGreeks(response.greeks);
        dispatch(setGreeks(response.greeks));
      }
    } catch {
      setMessage({ text: 'Error al calcular griegas', type: 'error' });
    }
  };

  const filteredOptions = options.filter(option => {
    const matchesSearch = option.symbol.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || option.option_type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>Gestión de Opciones</Typography>

      {message && <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage(null)}>{message.text}</Alert>}

      <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setCreateDialog(true)}>
          Nueva Opción
        </Button>
        <Button variant="contained" color="secondary" startIcon={<CalculateIcon />} onClick={() => setCalculateDialog(true)}>
          Calcular Griegas
        </Button>
        <Button variant="outlined" onClick={() => navigate('/dashboard')}>
          Volver al Dashboard
        </Button>
      </Box>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <TextField label="Buscar opción" variant="outlined" value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)} sx={{ flex: 1 }}
              InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }} />
            <FormControl variant="outlined" sx={{ minWidth: 150 }}>
              <InputLabel>Tipo</InputLabel>
              <Select value={filterType} onChange={(e) => setFilterType(e.target.value)} label="Tipo">
                <MenuItem value="all">Todos</MenuItem>
                <MenuItem value="call">Call</MenuItem>
                <MenuItem value="put">Put</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} aria-label="opciones tabs">
            <Tab label="Lista de Opciones" />
          </Tabs>
        </CardContent>
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Símbolo</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Strike</TableCell>
              <TableCell>Vencimiento</TableCell>
              <TableCell>Último Precio</TableCell>
              <TableCell>IV</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={7} align="center">Cargando...</TableCell></TableRow>
            ) : filteredOptions.length === 0 ? (
              <TableRow><TableCell colSpan={7} align="center">No hay opciones. Crea una nueva.</TableCell></TableRow>
            ) : (
              filteredOptions.map((option) => (
                <TableRow key={option.id}>
                  <TableCell>{option.symbol}</TableCell>
                  <TableCell>{option.option_type.toUpperCase()}</TableCell>
                  <TableCell>${option.strike_price.toFixed(2)}</TableCell>
                  <TableCell>{new Date(option.expiration_date).toLocaleDateString()}</TableCell>
                  <TableCell>${(option.last_price || 0).toFixed(2)}</TableCell>
                  <TableCell>{((option.implied_volatility || 0) * 100).toFixed(1)}%</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleDeleteOption(option.id)}><DeleteIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Option Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Nueva Opción</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={6}>
              <TextField fullWidth label="Símbolo" value={createForm.symbol}
                onChange={(e) => setCreateForm({ ...createForm, symbol: e.target.value })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Subyacente" value={createForm.underlying_symbol}
                onChange={(e) => setCreateForm({ ...createForm, underlying_symbol: e.target.value })} />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo</InputLabel>
                <Select value={createForm.option_type}
                  onChange={(e) => setCreateForm({ ...createForm, option_type: e.target.value as any })} label="Tipo">
                  <MenuItem value="call">Call</MenuItem>
                  <MenuItem value="put">Put</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Strike" type="number" value={createForm.strike_price}
                onChange={(e) => setCreateForm({ ...createForm, strike_price: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Fecha Vencimiento" type="date" value={createForm.expiration_date}
                onChange={(e) => setCreateForm({ ...createForm, expiration_date: e.target.value })}
                InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Volatilidad Implícita" type="number" value={createForm.implied_volatility}
                onChange={(e) => setCreateForm({ ...createForm, implied_volatility: Number(e.target.value) })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancelar</Button>
          <Button onClick={handleCreateOption} variant="contained">Crear</Button>
        </DialogActions>
      </Dialog>

      {/* Calculate Greeks Dialog */}
      <Dialog open={calculateDialog} onClose={() => setCalculateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Calcular Griegas</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={6}>
              <TextField fullWidth label="Símbolo" value={greeksForm.symbol}
                onChange={(e) => setGreeksForm({ ...greeksForm, symbol: e.target.value })} />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo</InputLabel>
                <Select value={greeksForm.option_type}
                  onChange={(e) => setGreeksForm({ ...greeksForm, option_type: e.target.value as any })} label="Tipo">
                  <MenuItem value="call">Call</MenuItem>
                  <MenuItem value="put">Put</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Precio Spot" type="number" value={greeksForm.spot_price}
                onChange={(e) => setGreeksForm({ ...greeksForm, spot_price: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Strike" type="number" value={greeksForm.strike_price}
                onChange={(e) => setGreeksForm({ ...greeksForm, strike_price: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Tiempo al Vencimiento (años)" type="number" value={greeksForm.time_to_expiration_years}
                onChange={(e) => setGreeksForm({ ...greeksForm, time_to_expiration_years: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Tasa Libre de Riesgo" type="number" value={greeksForm.risk_free_rate}
                onChange={(e) => setGreeksForm({ ...greeksForm, risk_free_rate: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Volatilidad" type="number" value={greeksForm.implied_volatility}
                onChange={(e) => setGreeksForm({ ...greeksForm, implied_volatility: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Fecha Vencimiento" type="date" value={greeksForm.expiration_date}
                onChange={(e) => setGreeksForm({ ...greeksForm, expiration_date: e.target.value })}
                InputLabelProps={{ shrink: true }} />
            </Grid>
          </Grid>

          {calculatedGreeks && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>Griegas Calculadas</Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}><Typography>Delta: {calculatedGreeks.delta?.toFixed(4)}</Typography></Grid>
                <Grid item xs={4}><Typography>Gamma: {calculatedGreeks.gamma?.toFixed(4)}</Typography></Grid>
                <Grid item xs={4}><Typography>Theta: {calculatedGreeks.theta?.toFixed(4)}</Typography></Grid>
                <Grid item xs={4}><Typography>Vega: {calculatedGreeks.vega?.toFixed(4)}</Typography></Grid>
                <Grid item xs={4}><Typography>Rho: {calculatedGreeks.rho?.toFixed(4)}</Typography></Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCalculateDialog(false)}>Cerrar</Button>
          <Button onClick={handleCalculateGreeks} variant="contained">Calcular</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OptionsPage;
