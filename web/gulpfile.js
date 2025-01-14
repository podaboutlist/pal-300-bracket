const fs = require('fs');

const { series, parallel } = require('gulp');
const { src, dest } = require('gulp');
const { watch } = require('gulp');

const browserSync = require('browser-sync').create();
const { reload } = browserSync;

const concat = require('gulp-concat');
const rename = require("gulp-rename");

const { rimraf } = require('rimraf');

const babel = require('gulp-babel');
const uglify = require('gulp-uglify');

const browserslist = require('browserslist');
const { browserslistToTargets } = require('lightningcss');
const lightningcss = require('gulp-lightningcss');

const htmlmin = require('gulp-html-minifier-terser');

const jsonmin = require('gulp-json-minify');


const PACKAGE = JSON.parse(fs.readFileSync('./package.json'));
console.info('[browserslist]', 'targeting', `"${PACKAGE.browserslist}"`);


function clean() {
	// keep dist/.git for GH Actions / Pages deployment
	return rimraf('./dist/!(.git)', { glob: true });
}

function minifyJSON() {
	return src('../data/*.json')
		.pipe(jsonmin())
		.pipe(rename((path) => {
			path.basename += '.min';
		}))
		.pipe(dest('dist/data/'));
}

function buildJS() {
	return src('src/index.js', { sourcemaps: true })
		.pipe(babel({
			presets: ['@babel/preset-env'],
			targets: PACKAGE.browserslist,
		}))
		.pipe(concat('index.min.js'))
		.pipe(uglify({
			warnings: true,
			toplevel: true,
		}))
		.pipe(dest('dist', { sourcemaps: '.' }));
}

function minifyCSS() {
	return src('src/index.css', { sourcemaps: true })
		.pipe(lightningcss({
			minify: true,
			sourceMap: true,
			targets: browserslistToTargets(browserslist(PACKAGE.browserslist)),
		}))
		.pipe(concat('index.min.css'))
		.pipe(dest('dist', { sourcemaps: '.' }));
}

function minifyHTML() {
	return src('src/index.html')
		.pipe(htmlmin({
			collapseWhitespace: true,
			collapseBooleanAttributes: true,
			removeComments: true,
			minifyURLs: true,
			removeComments: true,
			sortAttributes: true,
			sortClassName: true,
		}))
		.pipe(dest('dist'));
}

function copyImages() {
	return src(['src/favicon.ico', 'src/img/**'], {
		base: 'src',
		// stop gulp messing up our images
		encoding: false,
	})
		.pipe(dest('dist'));
}

function copyParentFiles() {
	return src(['../CNAME', '../LICENSE.txt', '../.gitignore'], {
		// base: 'dist',
	})
		.pipe(dest('dist'));
}

function watchFiles() {
	watch('src/*.js', buildJS);
	watch('src/*.css', minifyCSS);
	watch('src/*.html', minifyHTML);
}

function serve() {
	browserSync.init({
		// don't open a new tab every time the gulp task restarts
		open: false,
		// but do reload the page
		reloadOnRestart: true,
		listen: '127.0.0.1',
		port: 8000,
		server: 'dist',
		// buffer build + sourcemap events into a single reload
		reloadDelay: 20,
	});

	watchFiles();

	watch('dist').on('change', reload);
}

const build = parallel(
	minifyJSON,
	buildJS,
	minifyCSS,
	minifyHTML,
	copyImages,
	copyParentFiles
);

exports.clean = clean;
exports.build = build;
exports.serve = series(clean, build, serve);
exports.ci = series(clean, build);

exports.default = exports.serve;
