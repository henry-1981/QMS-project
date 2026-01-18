import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Cpu } from 'lucide-react';

interface GeminiModel {
  name: string;
  display_name: string;
  description: string;
}

export const GeminiModelSelector = () => {
  const [models, setModels] = useState<GeminiModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('gemini-1.5-pro');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8000/api/v1/agents/models', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setModels(response.data);
        // 기본값 설정 (gemini-1.5-pro가 목록에 있으면 그것으로, 없으면 첫번째 모델로)
        const hasPro = response.data.some((m: GeminiModel) => m.name === 'models/gemini-1.5-pro');
        if (hasPro) setSelectedModel('models/gemini-1.5-pro');
        else if (response.data.length > 0) setSelectedModel(response.data[0].name);
      } catch (error) {
        console.error('Failed to fetch Gemini models:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    localStorage.setItem('selected_gemini_model', newModel);
  };

  if (loading) return <div className="text-sm text-gray-400">Loading models...</div>;

  return (
    <div className="flex items-center space-x-2 bg-white px-3 py-1.5 rounded-lg border border-gray-200 shadow-sm">
      <Cpu className="w-4 h-4 text-blue-500" />
      <select 
        value={selectedModel} 
        onChange={handleModelChange}
        className="text-sm font-medium text-gray-700 bg-transparent border-none focus:ring-0 cursor-pointer"
      >
        {models.map((model) => (
          <option key={model.name} value={model.name}>
            {model.display_name}
          </option>
        ))}
      </select>
    </div>
  );
};
