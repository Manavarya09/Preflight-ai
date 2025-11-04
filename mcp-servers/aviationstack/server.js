/**
 * AviationStack MCP Server
 * 
 * MCP adapter for AviationStack Flight Tracking API
 * 
 * Tools:
 * - get_real_time_flights: Get live flight data
 * - get_historical_flights: Get historical flight records
 * - get_airport_info: Get airport information
 */

const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;
const AVIATIONSTACK_API_KEY = process.env.AVIATIONSTACK_API_KEY;

if (!AVIATIONSTACK_API_KEY) {
    console.error('[ERROR] AVIATIONSTACK_API_KEY environment variable is required');
    process.exit(1);
}

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
        service: 'aviationstack-mcp-server',
        version: '1.0.0',
        api_key_configured: !!AVIATIONSTACK_API_KEY,
        timestamp: new Date().toISOString()
    });
});

// MCP tool call endpoint
app.post('/call-tool', async (req, res) => {
    const { name, arguments: args } = req.body;

    console.log(`[MCP] Tool call: ${name}`, args);

    try {
        if (name === 'get_real_time_flights') {
            const flights = await getRealTimeFlights(args);
            res.json({ result: flights });
        } else if (name === 'get_historical_flights') {
            const flights = await getHistoricalFlights(args);
            res.json({ result: flights });
        } else if (name === 'get_airport_info') {
            const airport = await getAirportInfo(args);
            res.json({ result: airport });
        } else {
            res.status(400).json({
                error: `Unknown tool: ${name}`,
                available_tools: ['get_real_time_flights', 'get_historical_flights', 'get_airport_info']
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
 * Get real-time flight data from AviationStack
 */
async function getRealTimeFlights(args) {
    const {
        flight_iata,
        dep_iata,
        arr_iata,
        limit = 100
    } = args;

    const url = 'https://api.aviationstack.com/v1/flights';
    const params = {
        access_key: AVIATIONSTACK_API_KEY,
        limit: Math.min(limit, 100)
    };

    // Add optional filters
    if (flight_iata) params.flight_iata = flight_iata;
    if (dep_iata) params.dep_iata = dep_iata;
    if (arr_iata) params.arr_iata = arr_iata;

    console.log(`[AviationStack] Fetching real-time flights:`, params);

    const response = await axios.get(url, {
        params,
        timeout: 15000
    });

    return {
        pagination: response.data.pagination,
        data: response.data.data || []
    };
}

/**
 * Get historical flight data from AviationStack
 */
async function getHistoricalFlights(args) {
    const {
        flight_date,
        flight_iata,
        dep_iata,
        arr_iata,
        limit = 100
    } = args;

    // Validate flight_date
    if (!flight_date) {
        throw new Error('flight_date is required (format: YYYY-MM-DD)');
    }

    const url = 'https://api.aviationstack.com/v1/flights';
    const params = {
        access_key: AVIATIONSTACK_API_KEY,
        flight_date: flight_date,
        limit: Math.min(limit, 100)
    };

    // Add optional filters
    if (flight_iata) params.flight_iata = flight_iata;
    if (dep_iata) params.dep_iata = dep_iata;
    if (arr_iata) params.arr_iata = arr_iata;

    console.log(`[AviationStack] Fetching historical flights for ${flight_date}:`, params);

    const response = await axios.get(url, {
        params,
        timeout: 15000
    });

    return {
        pagination: response.data.pagination,
        data: response.data.data || []
    };
}

/**
 * Get airport information from AviationStack
 */
async function getAirportInfo(args) {
    const { airport_iata } = args;

    if (!airport_iata) {
        throw new Error('airport_iata is required');
    }

    const url = 'https://api.aviationstack.com/v1/airports';
    const params = {
        access_key: AVIATIONSTACK_API_KEY,
        iata_code: airport_iata
    };

    console.log(`[AviationStack] Fetching airport info for ${airport_iata}`);

    const response = await axios.get(url, {
        params,
        timeout: 15000
    });

    if (!response.data.data || response.data.data.length === 0) {
        throw new Error(`Airport ${airport_iata} not found`);
    }

    return response.data.data[0];
}

// List available tools (MCP standard)
app.get('/tools', (req, res) => {
    res.json({
        tools: [
            {
                name: 'get_real_time_flights',
                description: 'Get real-time flight tracking data',
                input_schema: {
                    type: 'object',
                    properties: {
                        flight_iata: {
                            type: 'string',
                            description: 'Flight IATA code (e.g., EK230)'
                        },
                        dep_iata: {
                            type: 'string',
                            description: 'Departure airport IATA code'
                        },
                        arr_iata: {
                            type: 'string',
                            description: 'Arrival airport IATA code'
                        },
                        limit: {
                            type: 'integer',
                            description: 'Maximum number of results (1-100)',
                            default: 100
                        }
                    }
                }
            },
            {
                name: 'get_historical_flights',
                description: 'Get historical flight data for a specific date',
                input_schema: {
                    type: 'object',
                    properties: {
                        flight_date: {
                            type: 'string',
                            description: 'Flight date in YYYY-MM-DD format',
                            pattern: '^\\d{4}-\\d{2}-\\d{2}$'
                        },
                        flight_iata: {
                            type: 'string',
                            description: 'Flight IATA code (e.g., EK230)'
                        },
                        dep_iata: {
                            type: 'string',
                            description: 'Departure airport IATA code'
                        },
                        arr_iata: {
                            type: 'string',
                            description: 'Arrival airport IATA code'
                        },
                        limit: {
                            type: 'integer',
                            description: 'Maximum number of results (1-100)',
                            default: 100
                        }
                    },
                    required: ['flight_date']
                }
            },
            {
                name: 'get_airport_info',
                description: 'Get detailed airport information',
                input_schema: {
                    type: 'object',
                    properties: {
                        airport_iata: {
                            type: 'string',
                            description: 'Airport IATA code (e.g., DXB, LHR, JFK)',
                            pattern: '^[A-Z]{3}$'
                        }
                    },
                    required: ['airport_iata']
                }
            }
        ]
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════╗
║   AviationStack MCP Server                    ║
║   Port: ${PORT}                                  ║
║   Status: RUNNING                             ║
║   API Key: ${AVIATIONSTACK_API_KEY ? '✓ Configured' : '✗ Missing'}               ║
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
