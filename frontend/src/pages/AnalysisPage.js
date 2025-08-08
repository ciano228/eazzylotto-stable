import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Select, 
  Button, 
  Table, 
  Tag, 
  Row, 
  Col, 
  Statistic,
  Typography,
  Space,
  message,
  Spin
} from 'antd';
import { BarChartOutlined, EyeOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import { lotteryAPI, analysisAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

function AnalysisPage() {
  const [searchParams] = useSearchParams();
  const [draws, setDraws] = useState([]);
  const [selectedDraw, setSelectedDraw] = useState(null);
  const [selectedUniverse, setSelectedUniverse] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [universes, setUniverses] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDraws();
    loadUniverses();
    
    // Si un drawId est passé en paramètre
    const drawId = searchParams.get('drawId');
    if (drawId) {
      setSelectedDraw(parseInt(drawId));
    }
  }, [searchParams]);

  useEffect(() => {
    if (selectedDraw) {
      analyzeSelectedDraw();
    }
  }, [selectedDraw, selectedUniverse]);

  const loadDraws = async () => {
    try {
      const response = await lotteryAPI.getDraws(50);
      setDraws(response.data);
    } catch (error) {
      message.error('Erreur lors du chargement des tirages');
    }
  };

  const loadUniverses = async () => {
    try {
      const response = await analysisAPI.getUniverses();
      setUniverses(response.data.universes);
    } catch (error) {
      message.error('Erreur lors du chargement des univers');
    }
  };

  const analyzeSelectedDraw = async () => {
    if (!selectedDraw) return;
    
    setLoading(true);
    try {
      const response = await analysisAPI.analyzeDraw(selectedDraw, selectedUniverse);
      setAnalysisResult(response.data);
    } catch (error) {
      message.error('Erreur lors de l\'analyse du tirage');
    } finally {
      setLoading(false);
    }
  };

  const getUniverseColor = (universe) => {
    const colors = {
      mundo: 'green',
      fruity: 'orange',
      trigga: 'magenta',
      roaster: 'purple',
      sunshine: 'gold'
    };
    return colors[universe] || 'blue';
  };

  const combinationColumns = [
    {
      title: 'Combinaison',
      dataIndex: 'combination',
      key: 'combination',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: 'Univers',
      dataIndex: 'univers',
      key: 'univers',
      render: (universe) => (
        <Tag color={getUniverseColor(universe)}>
          {universe.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Forme',
      dataIndex: 'forme',
      key: 'forme'
    },
    {
      title: 'Engine',
      dataIndex: 'engine',
      key: 'engine'
    },
    {
      title: 'Beastie',
      dataIndex: 'beastie',
      key: 'beastie'
    },
    {
      title: 'Tome',
      dataIndex: 'tome',
      key: 'tome'
    }
  ];

  const renderUniverseAnalysis = () => {
    if (!analysisResult?.universes) return null;

    return Object.entries(analysisResult.universes).map(([universe, combinations]) => (
      <Col xs={24} lg={12} key={universe}>
        <Card 
          className={`universe-card ${universe}`}
          title={
            <Space>
              <Tag color={getUniverseColor(universe)}>
                {universe.toUpperCase()}
              </Tag>
              <Text>{combinations.length} combinaisons</Text>
            </Space>
          }
        >
          {combinations.length > 0 ? (
            <div>
              {combinations.slice(0, 5).map((combo, index) => (
                <Tag key={index} style={{ margin: '2px' }}>
                  {combo.combination}
                </Tag>
              ))}
              {combinations.length > 5 && (
                <Text type="secondary"> +{combinations.length - 5} autres...</Text>
              )}
            </div>
          ) : (
            <Text type="secondary">Aucune combinaison dans cet univers</Text>
          )}
        </Card>
      </Col>
    ));
  };

  return (
    <div>
      <Title level={2}>📊 Analyse des Tirages</Title>
      
      <Card title="Sélection du Tirage" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Text strong>Tirage à analyser :</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="Sélectionner un tirage"
              value={selectedDraw}
              onChange={setSelectedDraw}
              showSearch
              optionFilterProp="children"
            >
              {draws.map(draw => (
                <Option key={draw.id} value={draw.id}>
                  {draw.lottery_name} - {draw.draw_date} ({draw.winning_numbers.join(', ')})
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={12} md={8}>
            <Text strong>Filtrer par univers :</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="Tous les univers"
              value={selectedUniverse}
              onChange={setSelectedUniverse}
              allowClear
            >
              {universes.map(universe => (
                <Option key={universe.id} value={universe.id}>
                  {universe.name}
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={24} md={8}>
            <Button
              type="primary"
              icon={<BarChartOutlined />}
              onClick={analyzeSelectedDraw}
              disabled={!selectedDraw}
              loading={loading}
              style={{ marginTop: 24 }}
            >
              Analyser
            </Button>
          </Col>
        </Row>
      </Card>

      {loading && (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>Analyse en cours...</Text>
            </div>
          </div>
        </Card>
      )}

      {analysisResult && !loading && (
        <>
          <Card title="Informations du Tirage" style={{ marginBottom: 24 }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Statistic
                  title="Nom de la Loterie"
                  value={analysisResult.draw_info.lottery_name}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic
                  title="Date du Tirage"
                  value={analysisResult.draw_info.draw_date}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic
                  title="Numéros Gagnants"
                  value={analysisResult.draw_info.winning_numbers.join(' - ')}
                />
              </Col>
            </Row>
          </Card>

          {selectedUniverse ? (
            <Card 
              title={`Analyse de l'Univers ${selectedUniverse.toUpperCase()}`}
              extra={
                <Tag color={getUniverseColor(selectedUniverse)}>
                  {analysisResult.total_combinations} combinaisons
                </Tag>
              }
            >
              <Table
                dataSource={analysisResult.combinations}
                columns={combinationColumns}
                rowKey="combination_id"
                pagination={{ pageSize: 10 }}
                size="small"
              />
            </Card>
          ) : (
            <>
              <Card title="Répartition par Univers" style={{ marginBottom: 24 }}>
                <Row gutter={[16, 16]}>
                  {renderUniverseAnalysis()}
                </Row>
              </Card>

              <Card title="Détail des Combinaisons">
                <Table
                  dataSource={Object.values(analysisResult.universes).flat()}
                  columns={combinationColumns}
                  rowKey="combination_id"
                  pagination={{ pageSize: 15 }}
                  size="small"
                />
              </Card>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default AnalysisPage;