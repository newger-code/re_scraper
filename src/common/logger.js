const config = require('config');
const { addColors, createLogger, format, transports } = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');

require('winston-daily-rotate-file');

const levelToUpperCase = format((info) => {
  info.level = info.level.toUpperCase();
  return info;
});

const plevels = {
  levels: {
    error: 0,
    warn: 1,
    info: 2,
    bold: 3,
    verbose: 4,
    debug: 5,
    silly: 6,
    trace: 7,
    force: 8
  },
  colors: {
    error: 'red',
    warn: 'yellow',
    info: 'green',
    bold: 'white bold',
    verbose: 'magenta',
    debug: 'green',
    silly: 'magenta italic',
    trace: 'magenta',
    force: 'magenta bold'
  }
};

const devFormat = format.combine(levelToUpperCase(),
  format.colorize(),
  format.timestamp(),
  format.align(),
  format.printf(info => {
    return `[${info.level}] ${info.timestamp} : ${info.message}`;
  }));

const logger = createLogger({
  levels: plevels.levels,
  level: config.logs.level,
  format: format.json(),
  defaultMeta: { service: config.name, env: process.env.NODE_ENV },
  transports: [
    new transports.DailyRotateFile({
      filename: `${config.logs.path + config.name}-%DATE%.log`,
      datePattern: 'YYYY-MM-DD-HH',
      zippedArchive: true,
      maxSize: '20m',
      format: devFormat
    })
  ],
});

addColors(plevels.colors);

logger.on('error', (error) => {
  console.error('Error caught', error);
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new transports.Console({
    format: devFormat
  }));
}

if (config.logs.elastic.enabled) {
  logger.add(new ElasticsearchTransport({
    level: config.logs.level,
    handleExceptions: false,
    clientOpts: {
      node: config.logs.elastic.host,
      auth: {
        username: config.logs.elastic.username,
        password: config.logs.elastic.password
      },
    }
  }));
}

module.exports = logger;