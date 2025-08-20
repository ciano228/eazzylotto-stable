import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Tabs } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import axios from 'axios';

const Login = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');

  const handleLogin = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/auth/login', values);
      const { access_token, user_id } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user_id', user_id);
      
      message.success('Connexion réussie');
      onLogin();
    } catch (error) {
      message.error('Identifiants incorrects');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values) => {
    if (values.password !== values.confirmPassword) {
      message.error('Les mots de passe ne correspondent pas');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/api/auth/register', {
        username: values.username,
        email: values.email,
        password: values.password
      });
      
      message.success('Inscription réussie, vous pouvez maintenant vous connecter');
      setActiveTab('login');
    } catch (error) {
      message.error('Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  const loginForm = (
    <Form onFinish={handleLogin} size="large">
      <Form.Item
        name="username"
        rules={[{ required: true, message: 'Nom d\'utilisateur requis' }]}
      >
        <Input prefix={<UserOutlined />} placeholder="Nom d'utilisateur" />
      </Form.Item>
      <Form.Item
        name="password"
        rules={[{ required: true, message: 'Mot de passe requis' }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Mot de passe" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          Se connecter
        </Button>
      </Form.Item>
    </Form>
  );

  const registerForm = (
    <Form onFinish={handleRegister} size="large">
      <Form.Item
        name="username"
        rules={[{ required: true, message: 'Nom d\'utilisateur requis' }]}
      >
        <Input prefix={<UserOutlined />} placeholder="Nom d'utilisateur" />
      </Form.Item>
      <Form.Item
        name="email"
        rules={[
          { required: true, message: 'Email requis' },
          { type: 'email', message: 'Email invalide' }
        ]}
      >
        <Input prefix={<MailOutlined />} placeholder="Email" />
      </Form.Item>
      <Form.Item
        name="password"
        rules={[{ required: true, message: 'Mot de passe requis' }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Mot de passe" />
      </Form.Item>
      <Form.Item
        name="confirmPassword"
        rules={[{ required: true, message: 'Confirmation requise' }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Confirmer le mot de passe" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          S'inscrire
        </Button>
      </Form.Item>
    </Form>
  );

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h1>EazzyCalculator</h1>
          <p>Plateforme d'analyse de loterie</p>
        </div>
        
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          centered
          items={[
            {
              key: 'login',
              label: 'Connexion',
              children: loginForm
            },
            {
              key: 'register',
              label: 'Inscription',
              children: registerForm
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default Login;