import React from 'react';

const DetectionTable = ({ detections }) => {
  return (
    <div className="overflow-x-auto mt-8">
      <table className="min-w-full bg-white border border-gray-200 shadow-md rounded-lg">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Timestamp</th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Object Detected</th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Confidence</th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Bounding Box</th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Source</th>
          </tr>
        </thead>
        <tbody>
          {detections.map((detection) => (
            <tr key={detection._id} className="border-t hover:bg-gray-50">
              <td className="px-4 py-2 text-sm text-gray-600">
                {new Date(detection.timestamp).toLocaleString()}
              </td>
              <td className="px-4 py-2 text-sm text-gray-600">{detection.label}</td>
              <td className="px-4 py-2 text-sm text-gray-600">
                {(detection.confidence * 100).toFixed(2)}%
              </td>
              <td className="px-4 py-2 text-sm text-gray-600">
                Top-left: ({detection.bbox.xmin.toFixed(2)}, {detection.bbox.ymin.toFixed(2)})<br />
                Bottom-right: ({detection.bbox.xmax.toFixed(2)}, {detection.bbox.ymax.toFixed(2)})
              </td>
              <td className="px-4 py-2 text-sm text-gray-600">{detection.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DetectionTable;