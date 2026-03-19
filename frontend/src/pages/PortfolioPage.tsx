import React, { useEffect, useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Alert
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import {
  setPortfolios, setSelectedPortfolio, setLoading, addPortfolio,
  updatePortfolio, removePortfolio, removePosition
} from '../store/portfolioSlice';
import { PortfolioService } from '../services/api';
import { Portfolio, CreatePortfolioRequest } from '../types/portfolio';

const PortfolioPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { portfolios, selectedPortfolio, loading } = useSelector((state: RootState) => state.portfolio);
  const [openDialog, setOpenDialog] = useState(false);
  const [portfolioForm, setPortfolioForm] = useState<CreatePortfolioRequest>({ name: '', description: '' });
  const [editingPortfolio, setEditingPortfolio] = useState<Portfolio | null>(null);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        dispatch(setLoading(true));
        const response = await PortfolioService.getPortfolios();
        if (response?.items) {
          dispatch(setPortfolios(response.items));
        }
      } catch (error) {
        setMessage({ text: 'Error al cargar portfolios', type: 'error' });
      } finally {
        dispatch(setLoading(false));
      }
    };
    fetchPortfolios();
  }, [dispatch]);

  const handleCreatePortfolio = async () => {
    try {
      const response = await PortfolioService.createPortfolio(portfolioForm);
      if (response) {
        dispatch(addPortfolio(response));
        setPortfolioForm({ name: '', description: '' });
        setOpenDialog(false);
        setMessage({ text: 'Portfolio creado exitosamente', type: 'success' });
      }
    } catch {
      setMessage({ text: 'Error al crear portfolio', type: 'error' });
    }
  };

  const handleUpdatePortfolio = async () => {
    if (!editingPortfolio) return;
    try {
      const response = await PortfolioService.updatePortfolio(editingPortfolio.id, portfolioForm);
      if (response) {
        dispatch(updatePortfolio(response));
        setEditingPortfolio(null);
        setPortfolioForm({ name: '', description: '' });
        setOpenDialog(false);
        setMessage({ text: 'Portfolio actualizado', type: 'success' });
      }
    } catch {
      setMessage({ text: 'Error al actualizar portfolio', type: 'error' });
    }
  };

  const handleDeletePortfolio = async (id: string) => {
    if (window.confirm('¿Eliminar este portfolio?')) {
      try {
        await PortfolioService.deletePortfolio(id);
        dispatch(removePortfolio(id));
        setMessage({ text: 'Portfolio eliminado', type: 'success' });
      } catch {
        setMessage({ text: 'Error al eliminar portfolio', type: 'error' });
      }
    }
  };

  const handleDeletePosition = async (positionId: string) => {
    if (!selectedPortfolio || !window.confirm('¿Eliminar esta posición?')) return;
    try {
      await PortfolioService.removePosition(selectedPortfolio.id, positionId);
      dispatch(removePosition({ portfolioId: selectedPortfolio.id, positionId }));
      setMessage({ text: 'Posición eliminada', type: 'success' });
    } catch {
      setMessage({ text: 'Error al eliminar posición', type: 'error' });
    }
  };

  const openEditDialog = (portfolio: Portfolio) => {
    setEditingPortfolio(portfolio);
    setPortfolioForm({ name: portfolio.name, description: portfolio.description || '' });
    setOpenDialog(true);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>Gestión de Portfolios</Typography>

      {message && <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage(null)}>{message.text}</Alert>}

      <Box sx={{ mb: 2 }}>
        <Button variant="contained" color="primary" startIcon={<AddIcon />}
          onClick={() => { setEditingPortfolio(null); setPortfolioForm({ name: '', description: '' }); setOpenDialog(true); }}
          sx={{ mr: 1 }}>
          Nuevo Portfolio
        </Button>
        <Button variant="outlined" onClick={() => navigate('/dashboard')}>
          Volver al Dashboard
        </Button>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Portfolios</Typography>
              {loading ? <Typography>Cargando...</Typography> : (
                <Box>
                  {portfolios.map((portfolio) => (
                    <Box key={portfolio.id}
                      sx={{
                        p: 1, mb: 1, cursor: 'pointer', borderRadius: 1,
                        border: selectedPortfolio?.id === portfolio.id ? '2px solid #1976d2' : '1px solid #ccc',
                      }}
                      onClick={() => dispatch(setSelectedPortfolio(portfolio))}>
                      <Typography variant="subtitle1">{portfolio.name}</Typography>
                      <Typography variant="body2">Valor: ${(portfolio.total_market_value || 0).toFixed(2)}</Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); openEditDialog(portfolio); }}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleDeletePortfolio(portfolio.id); }}>
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  ))}
                  {portfolios.length === 0 && <Typography variant="body2">No hay portfolios. Crea uno nuevo.</Typography>}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          {selectedPortfolio ? (
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>{selectedPortfolio.name}</Typography>
                {selectedPortfolio.description && (
                  <Typography variant="body2" color="textSecondary" gutterBottom>{selectedPortfolio.description}</Typography>
                )}
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Posiciones</Typography>
                  {selectedPortfolio.positions?.length > 0 ? (
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Opción ID</TableCell>
                            <TableCell>Cantidad</TableCell>
                            <TableCell>Precio Entrada</TableCell>
                            <TableCell>Precio Actual</TableCell>
                            <TableCell>P&L</TableCell>
                            <TableCell>Estado</TableCell>
                            <TableCell>Acciones</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {selectedPortfolio.positions.map((pos) => (
                            <TableRow key={pos.id}>
                              <TableCell>{pos.option_id?.slice(0, 8)}...</TableCell>
                              <TableCell>{pos.quantity}</TableCell>
                              <TableCell>${(pos.entry_price || 0).toFixed(2)}</TableCell>
                              <TableCell>${(pos.current_price || 0).toFixed(2)}</TableCell>
                              <TableCell sx={{ color: (pos.unrealized_pnl || 0) >= 0 ? 'green' : 'red' }}>
                                ${(pos.unrealized_pnl || 0).toFixed(2)}
                              </TableCell>
                              <TableCell>{pos.status}</TableCell>
                              <TableCell>
                                <IconButton size="small" onClick={() => handleDeletePosition(pos.id)}>
                                  <DeleteIcon />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Typography>No hay posiciones en este portfolio</Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent>
                <Typography variant="h6">Selecciona un portfolio para ver detalles</Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingPortfolio ? 'Editar Portfolio' : 'Nuevo Portfolio'}</DialogTitle>
        <DialogContent>
          <TextField autoFocus margin="dense" label="Nombre" fullWidth variant="outlined"
            value={portfolioForm.name}
            onChange={(e) => setPortfolioForm({ ...portfolioForm, name: e.target.value })} sx={{ mb: 2 }} />
          <TextField margin="dense" label="Descripción" fullWidth variant="outlined"
            value={portfolioForm.description}
            onChange={(e) => setPortfolioForm({ ...portfolioForm, description: e.target.value })} sx={{ mb: 2 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button onClick={editingPortfolio ? handleUpdatePortfolio : handleCreatePortfolio} variant="contained">
            {editingPortfolio ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PortfolioPage;
