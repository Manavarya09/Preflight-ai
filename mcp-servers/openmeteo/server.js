/**
 * Open-Meteo MCP Server
 * 
 * Provides Model Context Protocol interface for Open-Meteo Weather API
 * 
 * Tools:
 * - get_forecast: Get weather forecast for coordinates
 * - get_current_weather: Get current weather conditions
 */

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Logger middleware
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'openmeteo-mcp-server',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

// MCP tool call endpoint
app.post('/call-tool', async (req, res) => {
    const { name, arguments: args } = req.body;

    console.log(`[MCP] Tool call: ${name}`, args);

    try {
        if (name === 'get_forecast') {
            const forecast = await getForecast(args);
            res.json({ result: forecast });
        } else if (name === 'get_current_weather') {
            const weather = await getCurrentWeather(args);
            res.json({ result: weather });
        } else {
            res.status(400).json({
                error: `Unknown tool: ${name}`,
                available_tools: ['get_forecast', 'get_current_weather']
            });
        }
    } catch (error) {
        console.error('[MCP] Tool call error:', error.message);
        res.status(500).json({
            error: error.message,
            tool: name
        });
    }
});

/**
 * Get weather forecast from Open-Meteo API
 */
async function getForecast(args) {
    const {
        latitude,
        longitude,
        forecast_days = 7
    } = args;

    // Validate inputs
    if (!latitude || !longitude) {
        throw new Error('latitude and longitude are required');
    }

    const url = 'https://api.open-meteo.com/v1/forecast';
    const params = {
        latitude,
        longitude,
        forecast_days,
        hourly: 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,cloud_cover,visibility,pressure_msl',
        current: 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,cloud_cover,visibility,pressure_msl',
        timezone: 'auto'
    };

    console.log(`[Open-Meteo] Fetching forecast for ${latitude}, ${longitude}`);

    const response = await axios.get(url, { params, timeout: 10000 });
    
    return {
        latitude: response.data.latitude,
        longitude: response.data.longitude,
        timezone: response.data.timezone,
        elevation: response.data.elevation,
        current: response.data.current,
        hourly: response.data.hourly,
        hourly_units: response.data.hourly_units
    };
}

/**
 * Get current weather from Open-Meteo API
 */
async function getCurrentWeather(args) {
    const {
        latitude,
        longitude
    } = args;

    // Validate inputs
    if (!latitude || !longitude) {
        throw new Error('latitude and longitude are required');
    }

    const url = 'https://api.open-meteo.com/v1/forecast';
    const params = {
        latitude,
        longitude,
        current: 'temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,visibility,pressure_msl,weather_code',
        timezone: 'auto'
    };

    console.log(`[Open-Meteo] Fetching current weather for ${latitude}, ${longitude}`);

    const response = await axios.get(url, { params, timeout: 10000 });
    
    return {
        latitude: response.data.latitude,
        longitude: response.data.longitude,
        timezone: response.data.timezone,
        elevation: response.data.elevation,
        current: response.data.current,
        current_units: response.data.current_units
    };
}

// List available tools (MCP standard)
app.get('/tools', (req, res) => {
    res.json({
        tools: [
            {
                name: 'get_forecast',
                description: 'Get weather forecast for specific coordinates',
                input_schema: {
                    type: 'object',
                    properties: {
                        latitude: {
                            type: 'number',
                            description: 'Latitude coordinate (-90 to 90)'
                        },
                        longitude: {
                            type: 'number',
                            description: 'Longitude coordinate (-180 to 180)'
                        },
                        forecast_days: {
                            type: 'integer',
                            description: 'Number of forecast days (1-16)',
                            default: 7
                        }
                    },
                    required: ['latitude', 'longitude']
                }
            },
            {
                name: 'get_current_weather',
                description: 'Get current weather conditions for specific coordinates',
                input_schema: {
                    type: 'object',
                    properties: {
                        latitude: {
                            type: 'number',
                            description: 'Latitude coordinate (-90 to 90)'
                        },
                        longitude: {
                            type: 'number',
                            description: 'Longitude coordinate (-180 to 180)'
                        }
                    },
                    required: ['latitude', 'longitude']
                }
            }
        ]
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════╗
║   Open-Meteo MCP Server                       ║
║   Port: ${PORT}                                  ║
║   Status: RUNNING                             ║
║   Health: http://localhost:${PORT}/health        ║
║   Tools: http://localhost:${PORT}/tools          ║
╚═══════════════════════════════════════════════╝
    `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('[Server] SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('[Server] SIGINT received, shutting down gracefully');
    process.exit(0);
});
