import { db } from '../db';
import redisClient from '../redis';
import CacheHitRatio from './queries/cache_hit_ratio';
import gitUtil from '../util/gitUtil';
import Bloat from './queries/bloat';
import pkg from '../../../package.json';


async function databaseHealthcheck() {

  const result = {
    name: 'database',
  };
  try {
    const metadata = await db.task('Dependencies healthcheck', async t => {
      const cache = await t.one(CacheHitRatio);
      const bloat = await t.many(Bloat);
      result.status = 'Healthy';
      return {
        cache, bloat
      };
    });
    result.metadata = metadata;
    return result;
  } catch (err) {
    result.status = 'Unhealthy';
    result.message = err.message;
    return result;
  }
}

async function redistHealthcheck() {
  const result = {
    name: 'cache',
    status: 'Healthy'
  };
  try {
    redisClient.set('healthcheck', 'Ok', (err) => {
      if (err) {
        result.status = 'Unhealthy';
      }
      redisClient.get('healthcheck', (err) => {
        if (err) {
          result.status = 'Unhealthy';
        }
      });
    });
    return result;
  } catch (err) {
    result.status = 'Unhealthy';
    result.message = err.message;
    return result;
  }
}

export default async () => {
  const database = await databaseHealthcheck();
  const cache = await redistHealthcheck();
  const status = (database.status === 'Healthy' && cache.status === 'Healthy') ? 'Healthy' : 'Unhealthy';
  const commit = await gitUtil.lastCommit();
  const message = commit.sanitizedSubject;
  const version = new Date(commit.authoredOn * 1000);
  const result = {
    service: pkg.name,
    message,
    version,
    status,
    env: process.env.NODE_ENV || 'local',
    dependencies: [
      database, cache
    ]
  };
  try {
    result.dependencies = [database, cache];
    return result;
  } catch (err) {
    result.status = 'Unhealthy';

    return result;
  }
};
