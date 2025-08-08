import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Select, 
  Button, 
  Tag, 
  Row, 
  Col, 
  Statistic,
  Typography,
  Space,
  message,
  Progress,
  Divider
} from 'antd';
import { FileTextOutlined, BarChartOutlined, DownloadOutlined } from '@ant-design/icons';
import { analysisAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

function StatisticalJournalPage() {
  const [journal, setJournal] = useState([]);
  const [frequencies, setFrequencies] = useState({});
  const [universes, setUniverses] = useState([]);
  const [selectedUniverse, setSelectedUniverse] = useState(null);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [totalEntries, setTotalEntries] = useState(0);

  useEffect(() => {
    loadUniverses();
    loadJournal();
  }, []);

  useEffect(() => {
    loadJournal();
  }, [selectedUniverse, limit]);

  const loadUniverses = async () => {
    try {
      const response = await analysisAPI.getUniverses();
      setUniverses(response.data.universes);
    } catch (error) {
      message.error('Erreur lors du chargement des univers');
    }
  };

  const loadJournal = async () => {
    setLoading(true);
    try {
      const response = await analysisAPI.getStatisticalJournal(selectedUniverse, limit);
      setJournal(response.data.journal);
      setFrequencies(response.data.frequencies);
      setTotalEntries(response.data.total_entries);
    } catch (error) {
      message.error('Erreur lors du chargement du journal');
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

  const journalColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      width: 100,
      render: (date, record, index) => {
        // Grouper par date avec une ligne de séparation
        const prevRecord = journal[index - 1];
        const showDate = !prevRecord || prevRecord.date !== date;
        
        return showDate ? (
          <div>
            {index > 0 && <Divider style={{ margin: '8px 0' }} />}
            <Text strong>{date}</Text>
          </div>
        ) : null;
      }
    },
    {
      title: 'Loterie',
      dataIndex: 'lottery_name',
      key: 'lottery_name',
      width: 150,
      render: (name, record, index) => {
        const prevRecord = journal[index - 1];
        const showName = !prevRecord || prevRecord.date !== record.date;
        return showName ? <Text>{name}</Text> : null;
      }
    },
    {
      title: 'Combinaison',
      dataIndex: 'combination',
      key: 'combination',
      width: 120,
      render: (text) => <Text strong style={{ color: '#1890ff' }}>{text}</Text>
    },
    {
      title: 'Univers',
      dataIndex: 'univers',
      key: 'univers',
      width: 100,
      render: (universe) => (
        <Tag color={getUniverseColor(universe)}>
          {universe.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Forme',
      dataIndex: 'forme',
      key: 'forme',
      width: 100
    },
    {
      title: 'Engine',
      dataIndex: 'engine',
      key: 'engine',
      width: 100
    },
    {
      title: 'Beastie',
      dataIndex: 'beastie',
      key: 'beastie',
      width: 100
    },
    {
      title: 'Tome',
      dataIndex: 'tome',
      key: 'tome',
      width: 100
    }
  ];

  const renderFrequencyCard = (title, data, color) => {
    if (!data || Object.keys(data).length === 0) return null;

    const sortedData = Object.entries(data)
      .sort(([,a], [,b]) => b.count - a.count)
      .slice(0, 10);

    return (
      <Card title={title} size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          {sortedData.map(([key, value]) => (
            <div key={key}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text>{key}</Text>
                <Text strong>{value.percentage}%</Text>
              </div>
              <Progress 
                percent={value.percentage} 
                size="small" 
                strokeColor={color}
                showInfo={false}
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {value.count} occurrences
              </Text>
            </div>
          ))}
        </Space>
      </Card>
    );
  };

  const exportJournal = () => {
    // Fonction pour exporter le journal en CSV
    const csvContent = [
      ['Date', 'Loterie', 'Combinaison', 'Univers', 'Forme', 'Engine', 'Beastie', 'Tome'],
      ...journal.map(entry => [
        entry.date,
        entry.lottery_name,
        entry.combination,
        entry.univers,
        entry.forme,
        entry.engine,
        entry.beastie,
        entry.tome
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `journal_statistique_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div>
      <Title level={2}>📋 Journal Statistique</Title>
      
      <Card title="Filtres et Options" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
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
          
          <Col xs={24} sm={8}>
            <Text strong>Nombre d'entrées :</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={limit}
              onChange={setLimit}
            >
              <Option value={25}>25 dernières</Option>
              <Option value={50}>50 dernières</Option>
              <Option value={100}>100 dernières</Option>
              <Option value={200}>200 dernières</Option>
            </Select>
          </Col>
          
          <Col xs={24} sm={8}>
            <Space style={{ marginTop: 24 }}>
              <Button
                type="primary"
                icon={<FileTextOutlined />}
                onClick={loadJournal}
                loading={loading}
              >
                Actualiser
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={exportJournal}
                disabled={journal.length === 0}
              >
                Exporter CSV
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          <Card 
            title={`Journal des Combinaisons (${totalEntries} entrées)`}
            extra={
              selectedUniverse && (
                <Tag color={getUniverseColor(selectedUniverse)}>
                  Filtré: {selectedUniverse.toUpperCase()}
                </Tag>
              )
            }
          >
            <Table
              dataSource={journal}
              columns={journalColumns}
              rowKey={(record, index) => `${record.date}-${record.combination}-${index}`}
              loading={loading}
              pagination={{ 
                pageSize: 20,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => 
                  `${range[0]}-${range[1]} sur ${total} entrées`
              }}
              size="small"
              scroll={{ x: 800 }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Card>
              <Statistic
                title="Total des Entrées"
                value={totalEntries}
                prefix={<FileTextOutlined />}
              />
            </Card>

            {renderFrequencyCard('Top Univers', frequencies.univers, '#52c41a')}
            {renderFrequencyCard('Top Formes', frequencies.forme, '#1890ff')}
            {renderFrequencyCard('Top Engines', frequencies.engine, '#fa8c16')}
            {renderFrequencyCard('Top Beasties', frequencies.beastie, '#eb2f96')}
            {renderFrequencyCard('Top Tomes', frequencies.tome, '#722ed1')}
          </Space>
        </Col>
      </Row>
    </div>
  );
}

export default StatisticalJournalPage;