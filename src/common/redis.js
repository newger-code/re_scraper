import redis from 'redis';
const config = require('config');

const redisClient = redis.createClient({
  host: config.redis.host,
  port: config.redis.port,
});

export default redisClient;