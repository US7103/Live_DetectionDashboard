import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const DetectionChart = ({ detections }) => {
  const labels = [...new Set(detections.map(d => d.label))];
  const counts = labels.map(label => 
    detections.filter(d => d.label === label).length
  );

  const data = {
    labels,
    datasets: [
      {
        label: 'Detection Count',
        data: counts,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Detections by Object Type' }
    },
    scales: {
      y: { beginAtZero: true }
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <Bar data={data} options={options} />
    </div>
  );
};

export default DetectionChart;