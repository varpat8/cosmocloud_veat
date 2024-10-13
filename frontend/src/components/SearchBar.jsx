import React, { useState } from "react";
import { FaSearch } from "react-icons/fa";
import "./SearchBar.css";

const SearchBar = ({ setResults, location }) => {
  const [input, setInput] = useState("");

  const fetchData = (value) => {
    fetch("http://localhost:5000/zomato-search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: value,
        lat: location.lat,
        long: location.long,
      }),
    })
      .then((response) => response.json())
      .then((json) => {
        const results = json.filter((restaurant) => {
          return (
            value && restaurant.toLowerCase().includes(value.toLowerCase())
          );
        });
        console.log(results);
        setResults(results);
      })
      .catch((error) => {
        console.error("Error fetching data: ", error);
      });
  };

  const handleChange = (value) => {
    setInput(value);
    fetchData(value);
  };

  return (
    <div className="input-wrapper">
      <FaSearch id="search-icon" />
      <input
        placeholder="Type name of a restaurant.."
        value={input}
        onChange={(e) => handleChange(e.target.value)}
      />
    </div>
  );
};

export default SearchBar;
