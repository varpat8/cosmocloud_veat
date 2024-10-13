import React from "react";
import "./LocationPopup.css";

const LocationPopup = ({ onAllow, onDeny }) => {
  return (
    <div className="location-popup">
      <div className="popup-content">
        <h2>Allow Location Access</h2>
        <p>We need your location to show nearby restaurants.</p>
        <div className="popup-actions">
          <button onClick={onAllow} className="allow-btn">
            Allow
          </button>
          <button onClick={onDeny} className="deny-btn">
            Deny
          </button>
        </div>
      </div>
    </div>
  );
};

export default LocationPopup;
