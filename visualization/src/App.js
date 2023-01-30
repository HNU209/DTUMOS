import "mapbox-gl/dist/mapbox-gl.css";
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";

import Splash from "./components/Splash";
import Trip from "./components/Trip";
import "./css/app.css";

const fetchData = (FilE_NAME) => {
  const res = axios.get(
    `https://raw.githubusercontent.com/HNU209/NewYork-visualization/main/src/data/${FilE_NAME}.json`
  );
  const data = res.then((r) => r.data);
  return data;
};

const App = () => {
  const [trip, setTrip] = useState([]);
  const [emptyTaxi, setEmptyTaxi] = useState([]);
  const [passenger, setPassenger] = useState([]);
  const [isloaded, setIsLoaded] = useState(false);

  const getData = useCallback(async () => {
    const TRIP = await fetchData("trip");
    const EMPTY_TAXI = await fetchData("empty_taxi");
    const PASSENGER = await fetchData("ps_location");

    setTrip((prev) => TRIP);
    setEmptyTaxi((prev) => EMPTY_TAXI);
    setPassenger((prev) => PASSENGER);
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    getData();
  }, [getData]);

  return (
    <div className="container">
      {!isloaded && <Splash />}
      {isloaded && (
        <Trip trip={trip} emptyTaxi={emptyTaxi} passenger={passenger} />
      )}
    </div>
  );
};

export default App;
