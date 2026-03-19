import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useSelector } from 'react-redux';
import { RootState } from './store/store';
import darkTheme from './theme/darkTheme';
import AuthPage from './pages/AuthPage';
import WorkstationLayout from './layouts/WorkstationLayout';

const App: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/auth" element={!user ? <AuthPage /> : <Navigate to="/workstation" />} />
          <Route path="/workstation" element={user ? <WorkstationLayout /> : <Navigate to="/auth" />} />
          <Route path="/*" element={user ? <Navigate to="/workstation" /> : <Navigate to="/auth" />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};

export default App;
