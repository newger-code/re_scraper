const pkg = require('../package');

const configuration = {
  name: pkg.name,
  version: pkg.version,
  http: {
    port: 11010, session: {
      secret: 'mySecret',
      resave: false,
      saveUninitialized: true,
    },
    cors: { origin: '*', allowedHeaders: 'Authorization,content-type', methods: 'GET,PUT,POST' }
  },
  auth: {
    keycloak: {
      'auth-server-url': 'http://localhost:8080/auth',
      'ssl-required': 'external',
      'resource': 'elaraone',
    },
    routes: {
      logout: '/logout',
      admin: '/'
    }
  },
  redis: {
    host: 'localhost',
    port: 6379,
    ttl: 260
  },
  db: {
    host: 'localhost',
    port: 6432,
    database: 'books',
    user: 'picket',
    password: 'picket'
  },
  sonar: {
    serverUrl: 'https://sonar.pickethomes.com',
    login: '07fd8d0d7e98395479ef59879cafa3e0f0492636',
    options: {
      'sonar.sources': 'src',
      'sonar.tests': 'test',
      'sonar.inclusions': '**', // Entry point of your code
      'sonar.test.inclusions': 'src/**/*.spec.js,src/**/*.spec.jsx,src/**/*.test.js,src/**/*.test.jsx',
      'sonar.javascript.lcov.reportPaths': 'dist/coverage/lcov.info',
      'sonar.testExecutionReportPaths': 'dist/coverage/test-reporter.xml'
    }
  },
  logs: {
    elastic: {
      enabled: false,
      host: 'http://localhost:9200',
      username: 'elastic',
      password: 'changeme'
    },
    path: './logs/',
    level: 'debug'
  },
};

module.exports = configuration;
