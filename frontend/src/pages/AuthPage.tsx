import React, { useEffect, useState } from 'react';
import {
  Box, Card, CardContent, Typography, Button, TextField, Alert,
  CircularProgress, InputAdornment, IconButton,
} from '@mui/material';
import {
  Visibility as VisibilityIcon, VisibilityOff as VisibilityOffIcon,
  Email as EmailIcon, Lock as LockIcon, Person as PersonIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { login, register, clearError } from '../store/authSlice';
import { COLORS } from '../theme/darkTheme';
import { LoginRequest, RegisterRequest } from '../types/auth';

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { user, loading, error } = useSelector((state: RootState) => state.auth);
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loginForm, setLoginForm] = useState<LoginRequest>({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState<RegisterRequest>({ username: '', email: '', password: '', full_name: '' });

  useEffect(() => { if (user) navigate('/workstation'); }, [user, navigate]);
  useEffect(() => () => { dispatch(clearError()); }, [dispatch]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(clearError());
    try {
      if (isLogin) await dispatch(login(loginForm)).unwrap();
      else await dispatch(register(registerForm)).unwrap();
      navigate('/workstation');
    } catch {}
  };

  return (
    <Box sx={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      bgcolor: COLORS.bg.primary,
      backgroundImage: `radial-gradient(circle at 25% 25%, ${COLORS.primary}08 0%, transparent 50%), radial-gradient(circle at 75% 75%, ${COLORS.secondary}08 0%, transparent 50%)`,
      p: 2,
    }}>
      <Card sx={{ maxWidth: 380, width: '100%', bgcolor: COLORS.bg.paper, border: `1px solid ${COLORS.border}` }}>
        <CardContent sx={{ p: 3.5 }}>
          <Typography variant="h5" align="center" gutterBottom sx={{ fontWeight: 700, color: COLORS.primary, letterSpacing: '-0.02em' }}>
            GALLEGUIMETRO
          </Typography>
          <Typography variant="body2" align="center" sx={{ mb: 3, color: COLORS.text.muted }}>
            {isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2, fontSize: '0.8rem' }}>{error}</Alert>}

          <form onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <TextField fullWidth margin="dense" label="Nombre completo" size="small"
                  value={registerForm.full_name}
                  onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
                  InputProps={{ startAdornment: <InputAdornment position="start"><PersonIcon sx={{ fontSize: 18, color: COLORS.text.muted }} /></InputAdornment> }}
                />
                <TextField fullWidth margin="dense" label="Email" type="email" size="small"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  InputProps={{ startAdornment: <InputAdornment position="start"><EmailIcon sx={{ fontSize: 18, color: COLORS.text.muted }} /></InputAdornment> }}
                />
              </>
            )}

            <TextField fullWidth margin="dense" label="Usuario" size="small"
              value={isLogin ? loginForm.username : registerForm.username}
              onChange={(e) => isLogin ? setLoginForm({ ...loginForm, username: e.target.value }) : setRegisterForm({ ...registerForm, username: e.target.value })}
              InputProps={{ startAdornment: <InputAdornment position="start"><PersonIcon sx={{ fontSize: 18, color: COLORS.text.muted }} /></InputAdornment> }}
            />

            <TextField fullWidth margin="dense" label="Contraseña" size="small"
              type={showPassword ? 'text' : 'password'}
              value={isLogin ? loginForm.password : registerForm.password}
              onChange={(e) => isLogin ? setLoginForm({ ...loginForm, password: e.target.value }) : setRegisterForm({ ...registerForm, password: e.target.value })}
              InputProps={{
                startAdornment: <InputAdornment position="start"><LockIcon sx={{ fontSize: 18, color: COLORS.text.muted }} /></InputAdornment>,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                      {showPassword ? <VisibilityOffIcon sx={{ fontSize: 18 }} /> : <VisibilityIcon sx={{ fontSize: 18 }} />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button type="submit" fullWidth variant="contained" sx={{ mt: 2.5, mb: 1.5, py: 1 }}
              disabled={loading} startIcon={loading ? <CircularProgress size={16} /> : undefined}>
              {loading ? 'Procesando...' : (isLogin ? 'Ingresar' : 'Registrarse')}
            </Button>
          </form>

          <Box sx={{ textAlign: 'center' }}>
            <Button onClick={() => setIsLogin(!isLogin)} variant="text" size="small" sx={{ color: COLORS.text.secondary }}>
              {isLogin ? 'Crear cuenta nueva' : 'Ya tengo cuenta'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuthPage;
