import "../static/Admin.css"; // Import the CSS file for styling
import { useState, useEffect } from "react";
import axios from "axios";
import Chart from "chart.js/auto";

function Admin() {
  const [sysInfo, setSysInfo] = useState([]);
  const [humidityData, setHumidityData] = useState([]);
  const [httpTemperatureData, setHttpTemperatureData] = useState([]);
  const [mqttTemperatureData, setMqttTemperatureData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseSysInfo = await axios.get(
          "http://localhost:5002/get_sysinfo"
        );
        setSysInfo(responseSysInfo.data);

        const responseHumidity = await axios.get(
          "http://localhost:5002/weather/all"
        );
        setHumidityData(responseHumidity.data.weather_data);

        const responseHttpTemperature = await axios.get(
          "http://localhost:5002/ambient_temperature_http/all"
        );
        setHttpTemperatureData(responseHttpTemperature.data);

        const responseMqttTemperature = await axios.get(
          "http://localhost:5002/ambient_temperature_mqtt/all"
        );
        setMqttTemperatureData(responseMqttTemperature.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (sysInfo.length > 0) {
      renderSysInfoCharts(sysInfo);
    }
  }, [sysInfo]);

  useEffect(() => {
    if (humidityData.length > 0) {
      renderHumidityChart(humidityData);
    }
  }, [humidityData]);

  useEffect(() => {
    if (httpTemperatureData.length > 0) {
      renderTemperatureChart(
        httpTemperatureData,
        "httpTemperatureChart",
        "HTTP Temperature"
      );
    }
  }, [httpTemperatureData]);

  useEffect(() => {
    if (mqttTemperatureData.length > 0) {
      renderTemperatureChart(
        mqttTemperatureData,
        "mqttTemperatureChart",
        "MQTT Temperature"
      );
    }
  }, [mqttTemperatureData]);

  const renderSysInfoCharts = (sysInfo) => {
    // Render charts for system info
    const labels = sysInfo.map((data) => data.timestamp);
    const cpuUsage = sysInfo.map((data) => parseFloat(data.cpu_usage));
    const memoryUsage = sysInfo.map((data) => parseFloat(data.memory_usage));
    const diskUsage = sysInfo.map((data) => {
      const diskIndex = data.disk_description.indexOf("/");
      return data.disk_usage[diskIndex];
    });

    const ctxCPU = document.getElementById("cpuChart").getContext("2d");
    const ctxMemory = document.getElementById("memoryChart").getContext("2d");
    const ctxDisk = document.getElementById("diskChart").getContext("2d");

    new Chart(ctxCPU, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "CPU Usage",
            data: cpuUsage,
            borderColor: "rgba(75, 192, 192, 1)",
            tension: 0.1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });

    new Chart(ctxMemory, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Memory Usage",
            data: memoryUsage,
            borderColor: "rgba(255, 99, 132, 1)",
            tension: 0.1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });

    new Chart(ctxDisk, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Disk Usage",
            data: diskUsage,
            borderColor: "rgba(54, 162, 235, 1)",
            tension: 0.1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  };

  const renderHumidityChart = (humidityData) => {
    // Render humidity chart
    const timestamps = humidityData.map((data) => data.timestamp);
    const humidityValues = humidityData.map(
      (data) => data.relative_humidity_2m
    );

    const humidityCtx = document
      .getElementById("humidityChart")
      .getContext("2d");
    new Chart(humidityCtx, {
      type: "line",
      data: {
        labels: timestamps,
        datasets: [
          {
            label: "Humidity (%)",
            data: humidityValues,
            borderColor: "rgba(255, 99, 132, 1)",
            tension: 0.1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  };

  const renderTemperatureChart = (temperatureData, chartId, label) => {
    const timestamps = temperatureData.map((data) => data.timestamp);
    const temperatures = temperatureData.map((data) => data.temperature);

    const ctx = document.getElementById(chartId).getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: timestamps,
        datasets: [
          {
            label: label,
            data: temperatures,
            borderColor: "rgba(255, 99, 132, 1)",
            tension: 0.1,
          },
        ],
      },
    });
  };

  return (
    <div className="admin-container">
      <div className="main-pc">
        <div className="cpuchartdiv">
          <canvas id="cpuChart"></canvas>
          <canvas id="memoryChart"></canvas>
          <canvas id="diskChart"></canvas>
        </div>
      </div>
      <div className="admin-section city-humidity">
        <canvas id="humidityChart"></canvas>
      </div>
      <div className="admin-section iot-devices">
        <div className="http">
          <h2>HTTP Temperature IoT Device</h2>
          <canvas id="httpTemperatureChart"></canvas>
        </div>
        <div className="mqtt">
          <h2>MQTT Temperature IoT Device</h2>
          <canvas id="mqttTemperatureChart"></canvas>
        </div>
      </div>
    </div>
  );
}

export default Admin;
