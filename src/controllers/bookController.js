import {db} from '../common/db';

class BookController {
  constructor() {
    this.db = db;
  }

  async getBook(id) {
    try {
      return db.oneOrNone(`select *
                           from book
                           where id = $1`, [id]);
    } catch (err) {
      return new Error(`Unable to retrieve book ${id}`);
    }
  }

  async addBook(data) {
    try {
      return db.one(`
          insert into book(author, title)
          values ($1, $2)
          returning *`,
        [data.author, data.title]);
    } catch (err) {
      return new Error(`Unable to create customer ${data.id}`);
    }
  }
}

const bookController = new BookController();
export default bookController;