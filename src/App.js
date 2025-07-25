import React, { useState } from 'react';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [result, setResult] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    setSelectedImage(e.target.files[0]);
    setResult('');
    setName('');
  };

  const handleUpload = async () => {
    if (!selectedImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedImage);

    try {
      const response = await fetch('http://localhost:5000/recognize', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.plate_text || 'Грешка при разпознаване');
      setName(data.name || '');
    } catch (error) {
      setResult('Грешка при връзката със сървъра');
      setName('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Разпознаване на регистрационен номер</h1>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={handleUpload} disabled={!selectedImage || loading}>
        {loading ? 'Обработка...' : 'Разпознай номер'}
      </button>

      {result && (
        <div style={{ marginTop: 20 }}>
          <p>Регистрационен номер: <strong>{result}</strong></p>
          {name && <p>Име: <strong>{name}</strong></p>}
        </div>
      )}
    </div>
  );
}

export default App;



/*import React, { useState } from 'react';



function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    setSelectedImage(e.target.files[0]);
    setResult('');
  };

  const handleUpload = async () => {
    if (!selectedImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedImage);

    try {
      const response = await fetch('http://localhost:5000/recognize', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.plate_text || 'Грешка при разпознаване');
    } catch (error) {
      setResult('Грешка при връзката със сървъра');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Разпознаване на регистрационен номер</h1>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={handleUpload} disabled={!selectedImage || loading}>
        {loading ? 'Обработка...' : 'Разпознай номер'}
      </button>
      {result && <p>Резултат: <strong>{result}</strong></p>}
    </div>
  );
}

export default App; */



/*import React, { useState } from 'react';
const formData = new FormData();
formData.append("image", file);

fetch("http://localhost:5000/recognize", {
  method: "POST",
  body: formData
}) 
function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    setSelectedImage(e.target.files[0]);
    setResult('');
  };

  const handleUpload = async () => {
    if (!selectedImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedImage);

    try {
      const response = await fetch('http://localhost:5000/recognize', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.plate_text || 'Грешка при разпознаване');
    } catch (error) {
      setResult('Грешка при връзката със сървъра');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Разпознаване на регистрационен номер</h1>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={handleUpload} disabled={!selectedImage || loading}>
        {loading ? 'Обработка...' : 'Разпознай номер'}
      </button>
      {result && <p>Резултат: <strong>{result}</strong></p>}
    </div>
  );
}

export default App; */
