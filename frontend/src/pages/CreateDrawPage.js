import React, { useState } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  InputNumber, 
  Button, 
  DatePicker, 
  Space, 
  Tag, 
  message, 
  Row, 
  Col,
  Typography,
  Divider
} from 'antd';
import { PlusOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { lotteryAPI } from '../services/api';
import moment from 'moment';

const { Title, Text } = Typography;

function CreateDrawPage() {
  const [form] = Form.useForm();
  const [numbers, setNumbers] = useState([]);
  const [currentNumber, setCurrentNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const addNumber = () => {
    const num = parseInt(currentNumber);
    if (!num || num < 1 || num > 90) {
      message.error('Veuillez entrer un numéro entre 1 et 90');
      return;
    }
    if (numbers.includes(num)) {
      message.error('Ce numéro a déjà été ajouté');
      return;
    }
    setNumbers([...numbers, num]);
    setCurrentNumber('');
  };

  const removeNumber = (numToRemove) => {
    setNumbers(numbers.filter(num => num !== numToRemove));
  };

  const handleSubmit = async (values) => {
    if (numbers.length < 5) {
      message.error('Veuillez entrer au moins 5 numéros');
      return;
    }

    setLoading(true);
    try {
      const drawData = {
        lottery_name: values.lotteryName,
        draw_date: values.drawDate.format('DD/MM/YYYY'),
        winning_numbers: numbers.sort((a, b) => a - b),
        number_range_min: values.rangeMin || 1,
        number_range_max: values.rangeMax || 90
      };

      const response = await lotteryAPI.createDraw(drawData);
      setResult(response.data);
      message.success('Tirage créé avec succès !');
      
      // Reset form
      form.resetFields();
      setNumbers([]);
      
    } catch (error) {
      message.error('Erreur lors de la création du tirage');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeResult = () => {
    if (result?.draw_id) {
      navigate(`/analysis?drawId=${result.draw_id}`);
    }
  };

  return (
    <div>
      <Title level={2}>🎲 Nouveau Tirage</Title>
      
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card title="Informations du Tirage">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
            >
              <Form.Item
                name="lotteryName"
                label="Nom de la Loterie"
                rules={[{ required: true, message: 'Veuillez entrer le nom de la loterie' }]}
              >
                <Input placeholder="Ex: Loto du Samedi" />
              </Form.Item>

              <Form.Item
                name="drawDate"
                label="Date du Tirage"
                rules={[{ required: true, message: 'Veuillez sélectionner la date' }]}
              >
                <DatePicker 
                  style={{ width: '100%' }}
                  format="DD/MM/YYYY"
                  placeholder="Sélectionner la date"
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="rangeMin"
                    label="Plage Min"
                    initialValue={1}
                  >
                    <InputNumber min={1} max={89} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="rangeMax"
                    label="Plage Max"
                    initialValue={90}
                  >
                    <InputNumber min={2} max={90} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Numéros Gagnants">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Ajouter un numéro :</Text>
                <Space>
                  <InputNumber
                    min={1}
                    max={90}
                    value={currentNumber}
                    onChange={setCurrentNumber}
                    onPressEnter={addNumber}
                    placeholder="1-90"
                  />
                  <Button 
                    type="primary" 
                    icon={<PlusOutlined />} 
                    onClick={addNumber}
                  >
                    Ajouter
                  </Button>
                </Space>
              </div>

              <Divider />

              <div>
                <Text strong>Numéros sélectionnés ({numbers.length}) :</Text>
                <div style={{ marginTop: 8 }}>
                  {numbers.sort((a, b) => a - b).map(num => (
                    <Tag
                      key={num}
                      closable
                      onClose={() => removeNumber(num)}
                      style={{ margin: '4px', fontSize: '14px', padding: '4px 8px' }}
                    >
                      {num}
                    </Tag>
                  ))}
                  {numbers.length === 0 && (
                    <Text type="secondary">Aucun numéro sélectionné</Text>
                  )}
                </div>
              </div>

              {numbers.length >= 5 && (
                <div style={{ marginTop: 16 }}>
                  <Text type="success">
                    ✅ {numbers.length} numéros sélectionnés (minimum 5 requis)
                  </Text>
                </div>
              )}
            </Space>
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <Space>
          <Button
            type="primary"
            size="large"
            loading={loading}
            onClick={() => form.submit()}
            disabled={numbers.length < 5}
            icon={<PlayCircleOutlined />}
          >
            Créer le Tirage et Générer les Combinaisons
          </Button>
          
          <Button
            onClick={() => {
              form.resetFields();
              setNumbers([]);
              setResult(null);
            }}
            icon={<DeleteOutlined />}
          >
            Réinitialiser
          </Button>
        </Space>
      </Card>

      {result && (
        <Card 
          title="✅ Tirage Créé avec Succès" 
          style={{ marginTop: 24 }}
          extra={
            <Button type="primary" onClick={analyzeResult}>
              Analyser ce Tirage
            </Button>
          }
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={8}>
              <Text strong>ID du Tirage :</Text>
              <br />
              <Text>{result.draw_id}</Text>
            </Col>
            <Col xs={24} sm={8}>
              <Text strong>Combinaisons Générées :</Text>
              <br />
              <Text>{result.total_combinations}</Text>
            </Col>
            <Col xs={24} sm={8}>
              <Text strong>Aperçu des Univers :</Text>
              <br />
              {Object.entries(result.universes_preview || {}).map(([universe, count]) => (
                <Tag key={universe} style={{ margin: '2px' }}>
                  {universe}: {count}
                </Tag>
              ))}
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
}

export default CreateDrawPage;