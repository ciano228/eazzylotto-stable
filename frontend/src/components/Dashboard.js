import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, message, Avatar, Dropdown } from 'antd';
import { 
  DashboardOutlined, 
  CalculatorOutlined, 
  BarChartOutlined, 
  HistoryOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined
} from '@ant-design/icons';
import SessionManager from './SessionManager';
import Analytics from './Analytics';
import MLPredictions from './MLPredictions';
import axios from 'axios';

const { Header, Sider, Content } = Layout;

const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '/login.html';
      return;
    }

    try {
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      message.error('Session expirée');
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
      window.location.href = '/login.html';
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    message.success('Déconnexion réussie');
    window.location.href = '/login.html';
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        Profil
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        Paramètres
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        Déconnexion
      </Menu.Item>
    </Menu>
  );

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Tableau de bord',
    },
    {
      key: 'sessions',
      icon: <CalculatorOutlined />,
      label: 'Sessions',
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
    },
    {
      key: 'ml',
      icon: <HistoryOutlined />,
      label: 'Prédictions ML',
    },
  ];

  const renderContent = () => {
    switch (currentView) {
      case 'sessions':
        return <SessionManager />;
      case 'analytics':
        return <Analytics />;
      case 'ml':
        return <MLPredictions />;
      default:
        return (
          <div style={{ padding: '24px' }}>
            <h1>Bienvenue {user?.username}</h1>
            <p>Tableau de bord EazzyCalculator</p>
          </div>
        );
    }
  };

  if (loading) {
    return <div>Chargement...</div>;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.3)' }} />
        <Menu
          theme="dark"
          defaultSelectedKeys={['dashboard']}
          mode="inline"
          items={menuItems}
          onClick={({ key }) => setCurrentView(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            type="text"
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <Dropdown overlay={userMenu} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.username}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
};

export default Dashboard;