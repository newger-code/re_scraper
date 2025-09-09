import express from 'express';
import BookController from '../controllers/bookController';

const router = express.Router();
const startRouter = keycloak => {


  router.get('/:id', keycloak.protect(), async (req, res) => {
    try {
      const { id } = req.params;
      const book = await BookController.getBook(id);
      res.json(book);
    } catch (err) {
      res.json({ error: err.message });
    }
  });


  router.post('/', keycloak.protect(), async (req, res) => {
    try {
      const data = req.body;
      const book = await BookController.addBook(data);
      res.json(book);
    } catch (err) {
      res.json({ error: err.message });
    }
  });
};

module.exports = {
  router, startRouter
};
