/* 
 * TODO: 
 * Add rebasing
 * https://github.com/tunderdomb/rebase
 */

var gulp = require('gulp'),
    sass = require('gulp-sass'),
    path = require('path'),    browserify = require('browserify'),
    source = require('vinyl-source-stream'),
    paths = {
        // this is the starting point for the scripts.  
        // add in other scripts in this file by using the "require"
        // provided by browserfy.
        js: 'static_global/js_source/scripts.js',
        scss: 'static_global/sass/**/*.scss',
        css: 'static_global/css'
    };



gulp.task('sass', function () {
  return gulp.src(paths.scss)
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest(paths.css));
});

gulp.task('browserify', function () {
    var b = browserify({
            entries: [paths.js]
        });
    return b.bundle()
        .pipe(source('main.js'))
        .pipe(gulp.dest('static_global/js'));
});

gulp.task('build', ['sass','browserify'], function(){

});


gulp.task('watch', function () {
    gulp.watch(paths.scss, ['sass']);
    gulp.watch(paths.js, ['browserify']);
});

gulp.task('default', ['build', 'watch'], function () {

});