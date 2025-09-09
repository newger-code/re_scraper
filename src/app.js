import session from 'express-session';
import createError from 'http-errors';
import morgan from 'morgan';
import http from 'http';
import express from 'express';
import cors from 'cors';
import config from 'config';
import connectRedis from 'connect-redis';
import bodyParser from 'body-parser';
import helmet from 'helmet';
import KeycloakMultirealm from 'keycloak-connect-multirealm';
import cookieParser from 'cookie-parser';

import serverErrorHandler from './common/ServerErrorHandler';
import logger from './common/logger';
import client from './common/redis';

const bookRouter = require('./routes/book');
const indexRouter = require('./routes');

const RedisStore = connectRedis(session);
const app = express();

const { port } = config.http;

app.set('port', port);
app.use(cors(config.http.cors));
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(helmet({
  frameguard: false
}));

const sessionStore = new RedisStore({
  ttl: config.redis.ttl,
  client
});

const sessionCfg = {
  secret: config.http.session.secret,
  resave: config.http.session.resave,
  saveUninitialized: config.http.session.saveUninitialized,
  store: sessionStore
};

app.use(session(sessionCfg));

const keycloak = new KeycloakMultirealm({ store: sessionStore }, config.auth.keycloak);
keycloak.getRealmNameFromRequest = (req) => {
  return req.headers.realm || req.query.realm;
};
app.use(keycloak.middleware());
bookRouter.startRouter(keycloak);
indexRouter.startRouter(keycloak);

app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const kc = keycloak.getKeycloakObjectForRealm(req.headers.realm || req.query.realm);
    const result = await kc.grantManager.obtainDirectly(username, password);
    req.session['keycloak-token'] = result;
    kc.storeGrant(result, req, res);
    res.json(result);
  } catch (err) {
    res.json({
      error: {
        message: err.message
      }
    });
  }
});

app.use('/book', bookRouter.router);
app.use('/', indexRouter.router);

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404, 'Not Found'));
});

const server = http.createServer(app);

server.listen(port, () => {
  logger.info(`Service [${config.name}:${config.version}] running on port [${port}]`);
}).on('error', serverErrorHandler);

module.exports = app;
