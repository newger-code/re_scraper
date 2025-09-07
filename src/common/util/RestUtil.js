import jwt_decode from 'jwt-decode';

const getToken = (req) => {
  const token = req.session['keycloak-token'] || req.headers.authorization.substring(7);
  return jwt_decode(token);
};
const getRealm = (req) => {
  return req.headers.realm || req.query.realm;
};

const jwt = (req) => {
  if (req.session['keycloak-token']) {
    const tokenStr = req.session['keycloak-token'];
    const token = JSON.parse(tokenStr);
    return token.access_token;
  }
  return req.headers.authorization.substring(7);
};

module.exports = {
  getToken, getRealm, jwt
};