import React from 'react';

const DataForm = ({ formData, setFormData }) => {
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  return (
    <div className="data-form">
      <h3 className="form-title">Clinical Tabular Features</h3>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="age">Age</label>
          <input
            type="number"
            id="age"
            name="age"
            min="0"
            max="120"
            value={formData.age}
            onChange={handleChange}
            placeholder="e.g. 45"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="packYears">Pack Years (Smoking History)</label>
          <input
            type="number"
            id="packYears"
            name="packYears"
            min="0"
            max="100"
            step="0.1"
            value={formData.packYears}
            onChange={handleChange}
            placeholder="e.g. 10.5"
          />
        </div>

        <div className="form-group">
          <label htmlFor="gender">Gender</label>
          <select
            id="gender"
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            required
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <h4 className="checkbox-title">Symptoms & History (Check all that apply)</h4>
      <div className="checkbox-grid">
        <label className="checkbox-label">
          <input
            type="checkbox"
            name="tbContactHistory"
            checked={formData.tbContactHistory}
            onChange={handleChange}
          />
          <span className="checkmark"></span>
          TB Contact History
        </label>
        
        <label className="checkbox-label">
          <input
            type="checkbox"
            name="wheezingHistory"
            checked={formData.wheezingHistory}
            onChange={handleChange}
          />
          <span className="checkmark"></span>
          Wheezing History
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            name="phlegmCough"
            checked={formData.phlegmCough}
            onChange={handleChange}
          />
          <span className="checkmark"></span>
          Phlegm Cough
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            name="familyAsthmaHistory"
            checked={formData.familyAsthmaHistory}
            onChange={handleChange}
          />
          <span className="checkmark"></span>
          Family Asthma History
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            name="feverHistory"
            checked={formData.feverHistory}
            onChange={handleChange}
          />
          <span className="checkmark"></span>
          Fever History
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            name="coldPresent"
            checked={formData.coldPresent}
            onChange={handleChange}
          />
          <span className="checkmark"></span>
          Cold Present
        </label>
      </div>
    </div>
  );
};

export default DataForm;
