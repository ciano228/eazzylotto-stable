import React, { useState } from 'react';
import { Button, Form, Input, Card, message } from 'antd';
import axios from 'axios';

const AuthTest = () => {
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token'));

  const onLogin = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/auth/login', values);
      const { access_token, user_id } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user_id', user_id);
      setToken(access_token);
      
      message.success('Connexion réussie !');
    } catch (error) {
      message.error('Erreur de connexion');
    }
    setLoading(false);
  };

  const testProtectedEndpoint = async () => {
    try {
      const response = await axios.get('/api/session/test', {
        headers: { Authorization: `Bearer ${token}` }
      });
      message.success('Endpoint protégé accessible !');
      console.log(response.data);
    } catch (error) {
      message.error('Accès refusé');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    setToken(null);
    message.info('Déconnecté');
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <Card title="Test d'Authentification">
        {!token ? (
          <Form onFinish={onLogin} layout="vertical">
            <Form.Item name="email" label="Email" rules={[{ required: true }]}>
              <Input placeholder="test@example.com" />
            </Form.Item>
            <Form.Item name="password" label="Mot de passe" rules={[{ required: true }]}>
              <Input.Password placeholder="testpassword123" />
            </Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Se connecter
            </Button>
          </Form>
        ) : (
          <div>
            <p>✅ Connecté avec succès !</p>
            <p>Token: {token.substring(0, 20)}...</p>
            <Button onClick={testProtectedEndpoint} style={{ marginRight: '10px' }}>
              Tester API
            </Button>
            <Button onClick={logout} danger>
              Déconnexion
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default AuthTest;