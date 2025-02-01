import React from 'react';

const EmergencyCall: React.FC = () => {
  const emergencyNumbers = {
    medical: '108',
    fire: '101',
    police: '100',
    general: '112'
  };

  return (
    <div className="p-4 bg-white shadow-md rounded-md">
      <h2 className="text-xl font-bold mb-4">Emergency Numbers</h2>
      <div className="space-y-2">
        <div>
          <span className="font-semibold">Medical Emergency:</span> {emergencyNumbers.medical}
        </div>
        <div>
          <span className="font-semibold">Fire Station:</span> {emergencyNumbers.fire}
        </div>
        <div>
          <span className="font-semibold">Police Emergency:</span> {emergencyNumbers.police}
        </div>
        <div>
          <span className="font-semibold">General Emergency:</span> {emergencyNumbers.general}
        </div>
      </div>
    </div>
  );
};

export default EmergencyCall;
