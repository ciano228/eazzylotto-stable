import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Tag, 
  Space,
  Typography,
  message,
  Popconfirm,
  Modal
} from 'antd';
import { 
  EyeOutlined, 
  DeleteOutlined, 
  BarChartOutlined,
  TrophyOutlined 
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { lotteryAPI } from '../services/api';

const { Title, Text } = Typography;

function DrawHistoryPage() {
  const [draws, setDraws] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDraw, setSelectedDraw] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadDraws();
  }, []);

  const loadDraws = async () => {
    setLoading(true);
    try {
      const response = await lotteryAPI.getDraws(100);
      setDraws(response.data);
    } catch (error) {
      message.error('Erreur lors du chargement des tirages');
    } finally {
      setLoading(false);
    }
  };

  const deleteDraw = async (drawId) => {
    try {
      await lotteryAPI.deleteDraw(drawId);
      message.success('Tirage supprimé avec succès');
      loadDraws(); // Recharger la liste
    } catch (error) {
      message.error('Erreur lors de la suppression du tirage');
    }
  };

  const viewDrawDetails = async (drawId) => {
    try {
      const response = await lotteryAPI.getDraw(drawId);
      setSelectedDraw(response.data);
      setModalVisible(true);
    } catch (error) {
      message.error('Erreur lors du chargement des détails du tirage');
    }
  };

  const analyzeDraw = (drawId) => {
    navigate(`/analysis?drawId=${drawId}`);
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
      render: (id) => <Text strong>#{id}</Text>
    },
    {
      title: 'Nom de la Loterie',
      dataIndex: 'lottery_name',
      key: 'lottery_name',
      render: (name) => <Text strong>{name}</Text>
    },
    {
      title: 'Date du Tirage',
      dataIndex: 'draw_date',
      key: 'draw_date',
      width: 120,
      sorter: (a, b) => new Date(a.draw_date.split('/').reverse().join('-')) - new Date(b.draw_date.split('/').reverse().join('-')),
      render: (date) => <Tag color="blue">{date}</Tag>
    },
    {
      title: 'Numéros Gagnants',
      dataIndex: 'winning_numbers',
      key: 'winning_numbers',
      render: (numbers) => (
        <Space wrap>
          {numbers.map((num, index) => (
            <Tag key={index} color="gold" style={{ fontWeight: 'bold' }}>
              {num}
            </Tag>
          ))}
        </Space>
      )
    },
    {
      title: 'Plage',
      dataIndex: 'number_range',
      key: 'number_range',
      width: 80,
      render: (range) => <Text type="secondary">{range}</Text>
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => viewDrawDetails(record.id)}
          >
            Voir
          </Button>
          <Button
            type="default"
            size="small"
            icon={<BarChartOutlined />}
            onClick={() => analyzeDraw(record.id)}
          >
            Analyser
          </Button>
          <Popconfirm
            title="Êtes-vous sûr de vouloir supprimer ce tirage ?"
            onConfirm={() => deleteDraw(record.id)}
            okText="Oui"
            cancelText="Non"
          >
            <Button
              type="primary"
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              Supprimer
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Title level={2}>🕒 Historique des Tirages</Title>
      
      <Card 
        title={
          <Space>
            <TrophyOutlined />
            <span>Liste des Tirages ({draws.length})</span>
          </Space>
        }
        extra={
          <Button type="primary" onClick={loadDraws} loading={loading}>
            Actualiser
          </Button>
        }
      >
        <Table
          dataSource={draws}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} sur ${total} tirages`
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      <Modal
        title="Détails du Tirage"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            Fermer
          </Button>,
          <Button 
            key="analyze" 
            type="primary" 
            icon={<BarChartOutlined />}
            onClick={() => {
              setModalVisible(false);
              analyzeDraw(selectedDraw.id);
            }}
          >
            Analyser ce Tirage
          </Button>
        ]}
        width={600}
      >
        {selectedDraw && (
          <div>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>ID du Tirage : </Text>
                <Text>#{selectedDraw.id}</Text>
              </div>
              
              <div>
                <Text strong>Nom de la Loterie : </Text>
                <Text>{selectedDraw.lottery_name}</Text>
              </div>
              
              <div>
                <Text strong>Date du Tirage : </Text>
                <Tag color="blue">{selectedDraw.draw_date}</Tag>
              </div>
              
              <div>
                <Text strong>Plage de Numéros : </Text>
                <Text>{selectedDraw.number_range_min} - {selectedDraw.number_range_max}</Text>
              </div>
              
              <div>
                <Text strong>Numéros Gagnants : </Text>
                <div style={{ marginTop: 8 }}>
                  <Space wrap>
                    {selectedDraw.winning_numbers.map((num, index) => (
                      <Tag key={index} color="gold" style={{ 
                        fontWeight: 'bold', 
                        fontSize: '16px',
                        padding: '4px 8px'
                      }}>
                        {num}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
              
              <div>
                <Text strong>Nombre de Numéros : </Text>
                <Text>{selectedDraw.winning_numbers.length}</Text>
              </div>
              
              <div>
                <Text strong>Combinaisons Possibles : </Text>
                <Text>
                  {selectedDraw.winning_numbers.length >= 2 
                    ? Math.floor((selectedDraw.winning_numbers.length * (selectedDraw.winning_numbers.length - 1)) / 2)
                    : 0
                  }
                </Text>
              </div>
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default DrawHistoryPage;