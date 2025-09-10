const redis = require('redis');
const config = require('config');

const client = redis.createClient({
  host: config.redis.host,
  port: config.redis.port,
});

module.exports = client;