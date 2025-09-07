import express from 'express';
import config from 'config';
import onHealthCheck from '../common/healthcheck/healthcheck';

const router = express.Router();
const startRouter = keycloak => {

  router.get('/', async (req, res) => {
    res.end('');
  });

  router.get('/config', keycloak.protect('realm:admin'), (req, res) => {
    res.json(config);
  });

  router.get('/healthcheck', async (req, res) => {
    const result = await onHealthCheck();
    res.json(result);
  });
};

module.exports = {
  router, startRouter
};
