import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Progress, Tag, Space, Select, message, Spin } from 'antd';
import { RocketOutlined, BrainOutlined, ThunderboltOutlined } from '@ant-design/icons';
import axios from 'axios';

const MLPredictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modelType, setModelType] = useState('lstm');
  const [accuracy, setAccuracy] = useState(0);

  useEffect(() => {
    loadPredictions();
  }, [modelType]);

  const loadPredictions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/ml/predictions?model=${modelType}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPredictions(response.data.predictions);
      setAccuracy(response.data.accuracy);
    } catch (error) {
      // Données de test
      setPredictions([
        {
          id: 1,
          numbers: [7, 14, 21, 28, 35],
          confidence: 85,
          model: 'LSTM',
          date: '2024-01-15',
          status: 'pending'
        },
        {
          id: 2,
          numbers: [3, 12, 19, 26, 42],
          confidence: 78,
          model: 'Random Forest',
          date: '2024-01-14',
          status: 'verified'
        },
        {
          id: 3,
          numbers: [5, 11, 23, 31, 44],
          confidence: 92,
          model: 'Neural Network',
          date: '2024-01-13',
          status: 'success'
        }
      ]);
      setAccuracy(82.5);
      message.warning('Utilisation des données de test ML');
    } finally {
      setLoading(false);
    }
  };

  const generatePrediction = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/api/ml/generate', 
        { model: modelType },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      message.success('Nouvelle prédiction générée');
      loadPredictions();
    } catch (error) {
      message.error('Erreur lors de la génération');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Numéros Prédits',
      dataIndex: 'numbers',
      key: 'numbers',
      render: (numbers) => (
        <Space>
          {numbers.map((num, index) => (
            <Tag key={index} color="blue">{num}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Confiance',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence) => (
        <Progress 
          percent={confidence} 
          size="small" 
          status={confidence > 80 ? 'success' : confidence > 60 ? 'active' : 'exception'}
        />
      ),
    },
    {
      title: 'Modèle',
      dataIndex: 'model',
      key: 'model',
      render: (model) => <Tag color="purple">{model}</Tag>,
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          pending: 'orange',
          verified: 'blue',
          success: 'green',
          failed: 'red'
        };
        const labels = {
          pending: 'En attente',
          verified: 'Vérifié',
          success: 'Réussi',
          failed: 'Échoué'
        };
        return <Tag color={colors[status]}>{labels[status]}</Tag>;
      },
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Prédictions Machine Learning</h2>
        <Space>
          <Select
            value={modelType}
            onChange={setModelType}
            style={{ width: 200 }}
          >
            <Select.Option value="lstm">LSTM Neural Network</Select.Option>
            <Select.Option value="random_forest">Random Forest</Select.Option>
            <Select.Option value="neural_network">Neural Network</Select.Option>
          </Select>
          <Button 
            type="primary" 
            icon={<RocketOutlined />}
            onClick={generatePrediction}
            loading={loading}
          >
            Générer Prédiction
          </Button>
        </Space>
      </div>

      <Card 
        title={
          <Space>
            <BrainOutlined />
            Modèle Actuel: {modelType.toUpperCase()}
          </Space>
        }
        extra={
          <Space>
            <ThunderboltOutlined />
            Précision: {accuracy}%
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <div style={{ textAlign: 'center' }}>
          <Progress 
            type="circle" 
            percent={accuracy} 
            status={accuracy > 80 ? 'success' : 'active'}
            width={120}
          />
          <p style={{ marginTop: 16, color: '#666' }}>
            Basé sur {predictions.length} prédictions analysées
          </p>
        </div>
      </Card>

      <Card title="Historique des Prédictions">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Génération en cours...</p>
          </div>
        ) : (
          <Table
            columns={columns}
            dataSource={predictions}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        )}
      </Card>
    </div>
  );
};

export default MLPredictions;