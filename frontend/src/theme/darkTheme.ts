import { createTheme } from '@mui/material/styles';

export const COLORS = {
  bg: {
    primary: '#0a0e17',
    secondary: '#111827',
    paper: '#1a1f2e',
    elevated: '#1f2937',
    hover: '#252d3d',
  },
  profit: '#10b981',
  loss: '#ef4444',
  neutral: '#6b7280',
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  warning: '#f59e0b',
  call: '#3b82f6',
  put: '#f97316',
  itm: 'rgba(16, 185, 129, 0.08)',
  atm: 'rgba(245, 158, 11, 0.15)',
  otm: 'transparent',
  border: '#1f2937',
  borderLight: '#374151',
  text: {
    primary: '#f3f4f6',
    secondary: '#9ca3af',
    muted: '#6b7280',
  },
  chart: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899'],
};

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: COLORS.primary },
    secondary: { main: COLORS.secondary },
    success: { main: COLORS.profit },
    error: { main: COLORS.loss },
    warning: { main: COLORS.warning },
    background: {
      default: COLORS.bg.primary,
      paper: COLORS.bg.paper,
    },
    text: {
      primary: COLORS.text.primary,
      secondary: COLORS.text.secondary,
    },
    divider: COLORS.border,
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    fontSize: 13,
    h4: { fontWeight: 600, fontSize: '1.5rem' },
    h5: { fontWeight: 600, fontSize: '1.15rem' },
    h6: { fontWeight: 600, fontSize: '1rem' },
    body1: { fontSize: '0.875rem' },
    body2: { fontSize: '0.8rem' },
    caption: { fontSize: '0.7rem', color: COLORS.text.muted },
  },
  shape: { borderRadius: 6 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: COLORS.bg.primary },
        '*::-webkit-scrollbar': { width: '6px', height: '6px' },
        '*::-webkit-scrollbar-track': { background: COLORS.bg.secondary },
        '*::-webkit-scrollbar-thumb': { background: COLORS.borderLight, borderRadius: '3px' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: COLORS.bg.paper,
          border: `1px solid ${COLORS.border}`,
          boxShadow: 'none',
          '&:hover': { borderColor: COLORS.borderLight },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 500, fontSize: '0.8rem' },
        sizeSmall: { padding: '4px 10px', fontSize: '0.75rem' },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: '6px 12px',
          fontSize: '0.8rem',
          borderColor: COLORS.border,
        },
        head: {
          backgroundColor: COLORS.bg.secondary,
          fontWeight: 600,
          fontSize: '0.7rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: COLORS.text.secondary,
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:hover': { backgroundColor: `${COLORS.bg.hover} !important` },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 500, minHeight: 36, fontSize: '0.8rem' },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: { minHeight: 36 },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: { backgroundColor: COLORS.bg.elevated, border: `1px solid ${COLORS.border}` },
      },
    },
    MuiTextField: {
      defaultProps: { size: 'small' },
    },
    MuiSelect: {
      defaultProps: { size: 'small' },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontSize: '0.7rem', height: 24 },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: COLORS.bg.secondary, boxShadow: 'none', borderBottom: `1px solid ${COLORS.border}` },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: { backgroundColor: COLORS.bg.elevated, border: `1px solid ${COLORS.border}`, fontSize: '0.75rem' },
      },
    },
  },
});

export default darkTheme;
