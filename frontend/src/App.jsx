import "./App.css";
import { useState, useEffect } from "react";
import SearchBar from "./components/SearchBar";
import { SearchResultsList } from "./components/SearchResultsList";
import LocationPopup from "./components/LocationPopup"; // New Popup Component

function App() {
  const [results, setResults] = useState([]);
  const [location, setLocation] = useState({ lat: null, long: null });
  const [showPopup, setShowPopup] = useState(true); // State to manage popup visibility

  const handleLocationPermission = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setLocation({ lat: latitude, long: longitude });
          console.log("User location:", latitude, longitude);
          setShowPopup(false); // Close the popup after getting location
        },
        (error) => {
          console.error("Error getting location:", error);
          setShowPopup(false); // Close the popup even if there is an error
        }
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
      setShowPopup(false); // Close the popup if geolocation is not supported
    }
  };

  return (
    <div className="App">
      {showPopup && (
        <LocationPopup
          onAllow={handleLocationPermission}
          onDeny={() => setShowPopup(false)}
        />
      )}
      <div className="search-bar-container">
        {location.lat !== null && location.long !== null ? (
          <SearchBar setResults={setResults} location={location} />
        ) : (
          <p>Loading your location...</p>
        )}
        {results && results.length > 0 && (
          <SearchResultsList results={results} />
        )}
      </div>
    </div>
  );
}

export default App;
