const express = require('express');
const config = require('config');
const onHealthCheck = require('../common/healthcheck/healthcheck');

const router = express.Router();
const startRouter = (keycloak) => {
  router.get('/', (req, res) => {
    res.send('UP');
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
  router, startRouter,
};
