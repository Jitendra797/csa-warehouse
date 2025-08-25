import React from 'react';

type StreamlitDashboardProps = {
  src: string;
  title?: string;
  allowFullScreen?: boolean;
  height?: number | string;
  className?: string;
  style?: React.CSSProperties;
};

const StreamlitDashboard: React.FC<StreamlitDashboardProps> = ({
  src,
  title = 'Dashboard',
  allowFullScreen = true,
  height,
  className,
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    width: '100%',
    height: height ?? '100vh',
    overflow: 'hidden',
    ...style,
  };

  return (
    <div style={containerStyle} className={className}>
      <iframe
        src={src}
        title={title}
        style={{ width: '100%', height: '100%', border: 'none' }}
        allowFullScreen={allowFullScreen}
      />
    </div>
  );
};

export default StreamlitDashboard;


