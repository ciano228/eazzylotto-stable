import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { 
  HomeOutlined, 
  PlusOutlined, 
  BarChartOutlined, 
  FileTextOutlined,
  HistoryOutlined 
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

import HomePage from './pages/HomePage';
import CreateDrawPage from './pages/CreateDrawPage';
import AnalysisPage from './pages/AnalysisPage';
import StatisticalJournalPage from './pages/StatisticalJournalPage';
import DrawHistoryPage from './pages/DrawHistoryPage';

const { Header, Content, Sider } = Layout;

function App() {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">Accueil</Link>,
    },
    {
      key: '/create-draw',
      icon: <PlusOutlined />,
      label: <Link to="/create-draw">Nouveau Tirage</Link>,
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: <Link to="/analysis">Analyse</Link>,
    },
    {
      key: '/journal',
      icon: <FileTextOutlined />,
      label: <Link to="/journal">Journal Statistique</Link>,
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: <Link to="/history">Historique</Link>,
    },
  ];

  return (
    <Layout className="app-container">
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold',
          lineHeight: '64px'
        }}>
          🎯 EazzyCalculator
        </div>
      </Header>
      
      <Layout>
        <Sider width={250} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
          />
        </Sider>
        
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content className="main-content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/create-draw" element={<CreateDrawPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/journal" element={<StatisticalJournalPage />} />
              <Route path="/history" element={<DrawHistoryPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;