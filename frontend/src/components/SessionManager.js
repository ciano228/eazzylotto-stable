import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, DatePicker, message, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const SessionManager = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSession, setEditingSession] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/sessions', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(response.data);
    } catch (error) {
      // Fallback avec données de test
      setSessions([
        {
          id: 1,
          name: 'Session Test 1',
          date: '2024-01-15',
          draws: [1, 5, 12, 23, 34],
          status: 'active'
        },
        {
          id: 2,
          name: 'Session Test 2',
          date: '2024-01-14',
          draws: [3, 8, 15, 27, 41],
          status: 'completed'
        }
      ]);
      message.warning('Utilisation des données de test');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      const token = localStorage.getItem('token');
      const sessionData = {
        ...values,
        date: values.date.format('YYYY-MM-DD')
      };

      if (editingSession) {
        await axios.put(`/api/sessions/${editingSession.id}`, sessionData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        message.success('Session mise à jour');
      } else {
        await axios.post('/api/sessions', sessionData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        message.success('Session créée');
      }
      
      setModalVisible(false);
      setEditingSession(null);
      form.resetFields();
      loadSessions();
    } catch (error) {
      message.error('Erreur lors de la sauvegarde');
    }
  };

  const handleDelete = async (id) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/sessions/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      message.success('Session supprimée');
      loadSessions();
    } catch (error) {
      message.error('Erreur lors de la suppression');
    }
  };

  const handleEdit = (session) => {
    setEditingSession(session);
    form.setFieldsValue({
      ...session,
      date: moment(session.date)
    });
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'Nom',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => moment(date).format('DD/MM/YYYY'),
    },
    {
      title: 'Tirages',
      dataIndex: 'draws',
      key: 'draws',
      render: (draws) => draws?.join(', ') || 'Aucun',
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'blue'}>
          {status === 'active' ? 'Actif' : 'Terminé'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            icon={<PlayCircleOutlined />} 
            size="small"
            onClick={() => window.open(`/advanced-journal.html?session=${record.id}`, '_blank')}
          >
            Ouvrir
          </Button>
          <Button 
            icon={<EditOutlined />} 
            size="small" 
            onClick={() => handleEdit(record)}
          />
          <Button 
            icon={<DeleteOutlined />} 
            size="small" 
            danger 
            onClick={() => handleDelete(record.id)}
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>Gestion des Sessions</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingSession(null);
            form.resetFields();
            setModalVisible(true);
          }}
        >
          Nouvelle Session
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={sessions}
        loading={loading}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editingSession ? 'Modifier Session' : 'Nouvelle Session'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingSession(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="Nom de la session"
            rules={[{ required: true, message: 'Nom requis' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="date"
            label="Date"
            rules={[{ required: true, message: 'Date requise' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingSession ? 'Mettre à jour' : 'Créer'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                Annuler
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SessionManager;