import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Select, DatePicker, message } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrophyOutlined, CalculatorOutlined, BarChartOutlined, RiseOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { RangePicker } = DatePicker;

const Analytics = () => {
  const [stats, setStats] = useState({});
  const [chartData, setChartData] = useState([]);
  const [frequencyData, setFrequencyData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState([moment().subtract(30, 'days'), moment()]);

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const params = {
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD')
      };

      const response = await axios.get('/api/analytics', {
        headers: { Authorization: `Bearer ${token}` },
        params
      });

      setStats(response.data.stats);
      setChartData(response.data.trends);
      setFrequencyData(response.data.frequency);
    } catch (error) {
      // Données de test
      setStats({
        totalSessions: 45,
        totalDraws: 1250,
        winRate: 12.5,
        avgAccuracy: 78.3
      });

      setChartData([
        { date: '2024-01-01', sessions: 5, accuracy: 75 },
        { date: '2024-01-02', sessions: 8, accuracy: 82 },
        { date: '2024-01-03', sessions: 6, accuracy: 78 },
        { date: '2024-01-04', sessions: 12, accuracy: 85 },
        { date: '2024-01-05', sessions: 9, accuracy: 80 },
        { date: '2024-01-06', sessions: 15, accuracy: 88 },
        { date: '2024-01-07', sessions: 11, accuracy: 83 }
      ]);

      setFrequencyData([
        { number: 1, frequency: 25 },
        { number: 5, frequency: 32 },
        { number: 12, frequency: 28 },
        { number: 23, frequency: 35 },
        { number: 34, frequency: 22 },
        { number: 41, frequency: 30 },
        { number: 45, frequency: 18 }
      ]);

      message.warning('Utilisation des données de test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Analytics & Statistiques</h2>
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
          format="DD/MM/YYYY"
        />
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Sessions Totales"
              value={stats.totalSessions}
              prefix={<CalculatorOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Tirages Analysés"
              value={stats.totalDraws}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Taux de Réussite"
              value={stats.winRate}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Précision Moyenne"
              value={stats.avgAccuracy}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="Évolution des Sessions" loading={loading}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="sessions" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Précision par Jour" loading={loading}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="accuracy" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="Fréquence des Numéros" loading={loading}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={frequencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="number" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="frequency" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics;