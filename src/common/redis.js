import redis from 'redis';
import config from 'config';

const redisClient = redis.createClient({
  host: config.redis.host,
  port: config.redis.port,
});

export default redisClient;