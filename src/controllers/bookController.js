import { db } from '../common/db';

class BookController {
  static async getBook(id) {
    try {
      return db.oneOrNone(`select *
                           from book
                           where id = $1`, [id]);
    } catch (err) {
      return new Error(`Unable to retrieve book ${id}`);
    }
  }

  static async addBook(data) {
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

export default BookController;