import rimraf from 'rimraf';
import gulp from 'gulp';
import babel from 'gulp-babel';
import scanner from 'sonarqube-scanner';
import config from 'config';
import jsdoc from 'gulp-jsdoc3';
import eslint from 'gulp-eslint';
import jsdocConf from './jsdoc.json';


/**
 * Clean the build, deletes the build files and coverage data located
 * in <code>dist</code> and <code>coverage</code>
 */

const clean = async (cb) => {
  rimraf('./dist', cb);
};

const babelify = () => gulp.src('src/**/*.js')
  .pipe(babel())
  .pipe(gulp.dest('dist/lib'));

/**
 * Lint the source files
 */
const lint = () => gulp.src('src/**/*.js')
  .pipe(eslint())
  .pipe(eslint.format('compact'));

/**
 * Generate JSDoc
 */
const jsDoc3 = (cb) => {
  gulp.src(['README.md', 'src/**/*.*', 'config/**/*.js'], { read: false })
    .pipe(jsdoc(jsdocConf, cb));
};

const sonar = (cb) => {
  scanner(config.sonar, () => {
  });
  return cb();
};

const templates = () => {
  return gulp.src(['package.json'])
    .pipe(gulp.dest('dist/'));
};

const watchFiles = () => {
  gulp.watch('src/**/*', gulp.series(babelify, lint, jsDoc3));
  gulp.watch('config/**/*', gulp.series(babelify, lint, jsDoc3));
};

gulp.task('clean', clean);
gulp.task('lint', lint);
gulp.task('babel', babelify);
gulp.task('jsdoc', jsDoc3);
gulp.task('sonar', sonar);
gulp.task('templates', templates);
gulp.task('build', gulp.series(lint, babelify, templates, jsDoc3));
gulp.task('dev', watchFiles);
