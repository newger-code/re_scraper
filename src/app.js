const session = require('express-session');
const createError = require('http-errors');
const morgan = require('morgan');
const http = require('http');
const express = require('express');
const cors = require('cors');
const config = require('config');
const connectRedis = require('connect-redis');
const bodyParser = require('body-parser');
const helmet = require('helmet');
const KeycloakMultirealm = require('keycloak-connect-multirealm');
const cookieParser = require('cookie-parser');
const logger = require('./common/logger').default;
const client = require('./common/redis').default;
const serverErrorHandler = require('./common/ServerErrorHandler');
const bookRouter = require('./routes/book');
const indexRouter = require('./routes/index');

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Application specific logging, throwing an error, or other logic here
});

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
}).on('error', serverErrorHandler(port));

module.exports = app;
