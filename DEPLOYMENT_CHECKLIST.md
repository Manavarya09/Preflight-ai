# PreFlight AI - Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Configuration

- [ ] Create `.env` file in project root
- [ ] Set `DATABASE_URL` for PostgreSQL
- [ ] Set `REDIS_URL` for Redis cache
- [ ] Configure MCP server URLs:
  - [ ] `OPENMETEO_MCP_SERVER_URL`
  - [ ] `AVIATIONSTACK_MCP_SERVER_URL`
- [ ] Add API keys:
  - [ ] `AVIATIONSTACK_API_KEY` (for fallback)
  - [ ] `GOOGLE_MAPS_API_KEY` (optional)
- [ ] Set `LANGFLOW_URL` with correct Flow ID

### 2. MCP Server Deployment

#### Open-Meteo MCP Server

- [ ] Clone https://github.com/modelcontextprotocol/servers
- [ ] Navigate to `servers/src/weather`
- [ ] Run `npm install`
- [ ] Start server: `npm start` (default port 3000)
- [ ] Test health endpoint: `curl http://localhost:3000/health`

#### AviationStack MCP Server

- [ ] Create custom MCP server (see `MCP_INTEGRATION.md`)
- [ ] Install dependencies: `npm install express axios`
- [ ] Set `AVIATIONSTACK_API_KEY` environment variable
- [ ] Start server on port 3001
- [ ] Test health endpoint: `curl http://localhost:3001/health`

### 3. Database Initialization

- [ ] PostgreSQL container running
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Verify 13 tables created:
  - [ ] `flight_history`
  - [ ] `predictions`
  - [ ] `shap_explanations`
  - [ ] `alerts`
  - [ ] `weather_snapshots`
  - [ ] `airports`
  - [ ] `locations_cache`
  - [ ] `geocoding_cache`
  - [ ] `route_distances`
  - [ ] `users`
  - [ ] `user_preferences`
  - [ ] `notification_logs`
  - [ ] `system_metrics`

### 4. Redis Configuration

- [ ] Redis container running on port 6379
- [ ] Test connection: `redis-cli ping`
- [ ] Verify cache TTL settings

### 5. Langflow Setup

- [ ] Langflow container running on port 7860
- [ ] Access UI: http://localhost:7860
- [ ] Import flow from `backend/langflow_flow/preflight_ai_flow_router.json`
- [ ] Configure Ollama connection:
  - [ ] Ollama URL: `http://ollama:11434`
  - [ ] Model: `mistral:latest`
- [ ] Test flow with sample input
- [ ] Copy Flow ID and update `.env`

### 6. Ollama Model Setup

- [ ] Ollama container running on port 11434
- [ ] Pull Mistral model: `docker exec ollama ollama pull mistral`
- [ ] Verify model loaded: `docker exec ollama ollama list`
- [ ] Test generation: `curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"test"}'`

## Deployment Steps

### Docker Compose Deployment

1. [ ] Build all containers:
   ```bash
   docker-compose build --no-cache
   ```

2. [ ] Start all services:
   ```bash
   docker-compose up -d
   ```

3. [ ] Check container status:
   ```bash
   docker-compose ps
   ```

4. [ ] View logs:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

### Service Verification

- [ ] **Frontend**: http://localhost:3000 loads successfully
- [ ] **Backend API**: http://localhost:8000 returns service info
- [ ] **Health Check**: http://localhost:8000/health shows all services healthy
- [ ] **Langflow**: http://localhost:7860 accessible
- [ ] **Ollama**: http://localhost:11434/api/tags returns model list

### MCP Integration Verification

1. [ ] Check MCP client initialization in backend logs:
   ```
   ✓ MCP clients initialized successfully
   ```

2. [ ] Verify MCP server connectivity:
   ```bash
   curl http://localhost:8000/health
   ```
   Should show:
   ```json
   {
     "mcp_openmeteo": true,
     "mcp_aviationstack": true
   }
   ```

3. [ ] Test weather endpoint:
   ```bash
   curl http://localhost:8000/weather/current/DXB
   ```

4. [ ] Test flight tracking:
   ```bash
   curl "http://localhost:8000/flights/real-time?dep_iata=DXB&limit=5"
   ```

### API Testing

- [ ] Test `/weather/current/{airport_code}`
- [ ] Test `/weather/forecast/{airport_code}`
- [ ] Test `/flights/real-time`
- [ ] Test `/flights/route-statistics`
- [ ] Test `/predict/enhanced` with POST data
- [ ] Test `/location/airport/{code}` (if Google Maps enabled)

## Production Readiness Checklist

### Security

- [ ] Change default database passwords
- [ ] Use Docker secrets for API keys
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure CORS for production domain
- [ ] Add rate limiting middleware
- [ ] Enable request logging
- [ ] Set secure session cookies
- [ ] Implement API authentication (JWT)

### Performance

- [ ] Configure Redis connection pooling
- [ ] Set appropriate cache TTLs
- [ ] Enable database query caching
- [ ] Configure Nginx reverse proxy
- [ ] Enable gzip compression
- [ ] Set up CDN for frontend assets

### Monitoring

- [ ] Set up application logging (ELK stack or similar)
- [ ] Configure health check endpoints for k8s/monitoring
- [ ] Add Prometheus metrics
- [ ] Set up error tracking (Sentry or similar)
- [ ] Configure uptime monitoring
- [ ] Set up alerts for service failures

### Backup & Recovery

- [ ] Configure PostgreSQL automated backups
- [ ] Set retention policy for database backups
- [ ] Test backup restoration procedure
- [ ] Document disaster recovery plan
- [ ] Set up Redis persistence (RDB + AOF)

### Documentation

- [ ] Update API documentation with production URLs
- [ ] Document environment variables
- [ ] Create runbook for common issues
- [ ] Document scaling procedures
- [ ] Update architecture diagrams

## Post-Deployment Verification

### Smoke Tests (30 minutes)

1. [ ] Load homepage - verify UI loads correctly
2. [ ] Test live flight search
3. [ ] Test weather forecast retrieval
4. [ ] Submit prediction request
5. [ ] Verify SHAP explanation generation
6. [ ] Check AI insights generation
7. [ ] Test historical data endpoints
8. [ ] Verify database writes

### Performance Tests

- [ ] Run load test with 100 concurrent users
- [ ] Verify response times < 2 seconds for API calls
- [ ] Check database query performance
- [ ] Monitor memory usage over 1 hour
- [ ] Verify MCP fallback works when servers down

### Error Handling Tests

- [ ] Test with invalid airport codes
- [ ] Test with missing required parameters
- [ ] Test with malformed JSON requests
- [ ] Verify graceful degradation when MCP servers unavailable
- [ ] Test database connection failure handling
- [ ] Test Redis connection failure handling

## Rollback Plan

If deployment fails:

1. [ ] Stop all containers: `docker-compose down`
2. [ ] Restore database from backup
3. [ ] Rollback to previous Docker images
4. [ ] Verify previous version working
5. [ ] Document failure reason
6. [ ] Create fix plan

## Support Contacts

- **Backend Issues**: [Your Email]
- **Frontend Issues**: [Your Email]
- **Infrastructure**: [Your Email]
- **Database**: [DBA Email]

## Deployment Sign-off

- [ ] Development Team Lead: _______________
- [ ] QA Lead: _______________
- [ ] DevOps: _______________
- [ ] Product Owner: _______________

**Deployment Date**: _______________

**Deployment Time**: _______________

**Deployed By**: _______________

**Version**: v2.0.0-mcp

## Notes

_Add any deployment-specific notes here_

---

**Status Legend**:
- ✅ Completed
- ⏳ In Progress
- ❌ Failed
- ⏸️ Blocked
