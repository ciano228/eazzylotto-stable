import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Typography, Space } from 'antd';
import { 
  TrophyOutlined, 
  BarChartOutlined, 
  PlusOutlined,
  FileTextOutlined 
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { lotteryAPI, analysisAPI } from '../services/api';

const { Title, Paragraph } = Typography;

function HomePage() {
  const [stats, setStats] = useState({
    totalDraws: 0,
    totalCombinations: 0,
    universes: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [drawsResponse, universesResponse] = await Promise.all([
        lotteryAPI.getDraws(100),
        analysisAPI.getUniverses()
      ]);

      setStats({
        totalDraws: drawsResponse.data.length,
        totalCombinations: 4005, // Nombre total de combinaisons dans votre DB
        universes: universesResponse.data.universes.length
      });
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <Title level={1}>
          🎯 EazzyCalculator
        </Title>
        <Paragraph style={{ fontSize: '18px', color: '#666' }}>
          Système d'analyse et de prédiction des numéros gagnants au loto
        </Paragraph>
      </div>

      <Row gutter={[24, 24]} style={{ marginBottom: 40 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Tirages Analysés"
              value={stats.totalDraws}
              prefix={<TrophyOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Combinaisons en Base"
              value={stats.totalCombinations}
              prefix={<BarChartOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Univers Disponibles"
              value={stats.universes}
              prefix={<FileTextOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Plage de Numéros"
              value="1-90"
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} md={12}>
          <Card 
            title="🎲 Nouveau Tirage" 
            extra={<Link to="/create-draw">Commencer</Link>}
          >
            <Paragraph>
              Saisissez les numéros gagnants d'un tirage pour générer les combinaisons 
              et les classifier selon leurs univers respectifs.
            </Paragraph>
            <Space>
              <Button type="primary" icon={<PlusOutlined />}>
                <Link to="/create-draw">Créer un Tirage</Link>
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card 
            title="📊 Analyse Statistique" 
            extra={<Link to="/analysis">Analyser</Link>}
          >
            <Paragraph>
              Analysez les tirages existants pour identifier les tendances 
              et les fréquences d'apparition des différents attributs.
            </Paragraph>
            <Space>
              <Button icon={<BarChartOutlined />}>
                <Link to="/analysis">Voir les Analyses</Link>
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card 
            title="📋 Journal Statistique" 
            extra={<Link to="/journal">Consulter</Link>}
          >
            <Paragraph>
              Consultez le journal détaillé des combinaisons gagnantes 
              avec leurs attributs pour dégager les tendances.
            </Paragraph>
            <Space>
              <Button icon={<FileTextOutlined />}>
                <Link to="/journal">Ouvrir le Journal</Link>
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card 
            title="🕒 Historique des Tirages" 
            extra={<Link to="/history">Voir tout</Link>}
          >
            <Paragraph>
              Parcourez l'historique complet de tous les tirages 
              enregistrés dans le système.
            </Paragraph>
            <Space>
              <Button icon={<TrophyOutlined />}>
                <Link to="/history">Voir l'Historique</Link>
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 40, textAlign: 'center' }}>
        <Title level={3}>Les 5 Univers de Classification</Title>
        <Row gutter={[16, 16]} style={{ marginTop: 20 }}>
          {['Mundo', 'Fruity', 'Trigga', 'Roaster', 'Sunshine'].map((universe, index) => (
            <Col key={universe} xs={24} sm={12} md={4}>
              <div className={`universe-card ${universe.toLowerCase()}`} style={{
                padding: '16px',
                borderRadius: '8px',
                background: '#f9f9f9',
                textAlign: 'center'
              }}>
                <Title level={4} style={{ margin: 0 }}>
                  {universe}
                </Title>
              </div>
            </Col>
          ))}
        </Row>
      </Card>
    </div>
  );
}

export default HomePage;