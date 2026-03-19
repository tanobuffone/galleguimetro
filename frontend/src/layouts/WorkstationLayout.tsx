import React, { useState } from 'react';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import { COLORS } from '../theme/darkTheme';
import TopBar from '../components/TopBar';
import OptionsChainPanel from '../components/options/OptionsChainPanel';
import PortfolioPanel from '../components/portfolio/PortfolioPanel';
import StrategyBuilderPanel from '../components/strategy/StrategyBuilderPanel';
import PayoffDiagramPanel from '../components/charts/PayoffDiagramPanel';

type PanelId = 'chain' | 'portfolio' | 'strategy' | 'payoff';

interface PanelConfig {
  id: PanelId;
  label: string;
  component: React.ReactNode;
}

const PANELS: PanelConfig[] = [
  { id: 'chain', label: 'Option Chain', component: <OptionsChainPanel /> },
  { id: 'portfolio', label: 'Portfolio', component: <PortfolioPanel /> },
  { id: 'strategy', label: 'Strategy Builder', component: <StrategyBuilderPanel /> },
  { id: 'payoff', label: 'Payoff Diagram', component: <PayoffDiagramPanel /> },
];

const WorkstationLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [layout, setLayout] = useState<'full' | 'split'>('split');

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: COLORS.bg.primary, overflow: 'hidden' }}>
      <TopBar />

      {layout === 'split' ? (
        // Split layout: 2x2 grid
        <Box sx={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: '1px', bgcolor: COLORS.border, overflow: 'hidden' }}>
          {PANELS.map((panel) => (
            <Box key={panel.id} sx={{ bgcolor: COLORS.bg.paper, display: 'flex', flexDirection: 'column', overflow: 'hidden', minHeight: 0 }}>
              {panel.component}
            </Box>
          ))}
        </Box>
      ) : (
        // Tab layout: one panel at a time
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}
            sx={{ px: 1, borderBottom: `1px solid ${COLORS.border}`, bgcolor: COLORS.bg.secondary }}>
            {PANELS.map((p, i) => (
              <Tab key={p.id} label={p.label} />
            ))}
          </Tabs>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            {PANELS[activeTab].component}
          </Box>
        </Box>
      )}

      {/* Bottom status bar */}
      <Box sx={{
        height: 24, px: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        bgcolor: COLORS.bg.secondary, borderTop: `1px solid ${COLORS.border}`,
      }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="caption" sx={{ color: COLORS.text.muted, cursor: 'pointer' }}
            onClick={() => setLayout(layout === 'split' ? 'full' : 'split')}>
            [{layout === 'split' ? '4 Panels' : 'Tabs'}] Click para cambiar
          </Typography>
        </Box>
        <Typography variant="caption" sx={{ color: COLORS.text.muted }}>
          Galleguimetro v0.2.0 | GGAL $637.47
        </Typography>
      </Box>
    </Box>
  );
};

export default WorkstationLayout;
