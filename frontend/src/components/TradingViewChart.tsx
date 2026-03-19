import React, { useEffect, useRef } from 'react';

declare global {
  interface Window {
    TradingView: any;
  }
}

interface TradingViewChartProps {
  symbol: string;
  interval?: string;
  width?: number | string;
  height?: number;
  theme?: 'light' | 'dark';
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  interval = '1d',
  width = '100%',
  height = 400,
  theme = 'light'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetId = useRef(`tv_chart_${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    if (!containerRef.current) return;

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.type = 'text/javascript';
    script.async = true;

    script.onload = () => {
      if (window.TradingView && containerRef.current) {
        new window.TradingView.widget({
          autosize: typeof width === 'string',
          width: typeof width === 'number' ? width : undefined,
          height: height,
          symbol: symbol,
          interval: interval,
          timezone: 'America/Argentina/Buenos_Aires',
          theme: theme,
          style: '1',
          locale: 'es',
          toolbar_bg: '#f1f3f6',
          enable_publishing: false,
          allow_symbol_change: true,
          save_image: false,
          container_id: widgetId.current,
        });
      }
    };

    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol, interval, width, height, theme]);

  return (
    <div
      ref={containerRef}
      id={widgetId.current}
      style={{ width: typeof width === 'number' ? `${width}px` : '100%', height: `${height}px` }}
    />
  );
};

export default TradingViewChart;
