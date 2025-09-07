import config from 'config';
import bluebird from 'bluebird';
import monitor from 'pg-monitor';

const initOptions = {
  promiseLib: bluebird,
  query(e) {
    /* do some of your own processing, if needed */

    monitor.query(e); // monitor the event;
  },
  error(err, e) {
    /* do some of your own processing, if needed */

    monitor.error(err, e); // monitor the event;
  }
};

const pgp = require('pg-promise')(initOptions);

monitor.attach(initOptions);
const db = pgp(config.db);

export {
  db, pgp
};
